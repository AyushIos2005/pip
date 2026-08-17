"""
dashboard.py
------------
The complete Tkinter/ttkbootstrap UI layer for Internet Speed Tester
Pro: sidebar navigation, top bar, status bar, menu bar, the animated
circular speed gauge, stat cards, live matplotlib graph, and the
History / Reports / Settings / About views.

Architecture note (MVC-style):
    - Model  -> speed_test.SpeedTestResult, history.HistoryManager, settings.Settings
    - View   -> the ttk widget classes in this file
    - Controller -> MainWindow, which wires user actions to the model
      layer and pushes results back into the views.

No GUI work is ever performed from a background thread - all worker
callbacks are marshalled onto the Tk main loop via `root.after(0, ...)`.
"""

from __future__ import annotations

import math
import tkinter as tk
from tkinter import filedialog, messagebox
from typing import Callable, Optional

import ttkbootstrap as ttk
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg
from matplotlib.figure import Figure

from history import HistoryManager
from notifications import NotificationManager
from reports import ReportGenerator
from settings import Settings
from speed_test import SpeedTestResult, SpeedTestWorker
from themes import FONTS, Palette, ThemeManager
from utils import (
    current_date_str,
    current_time_str,
    format_ping,
    format_speed,
    get_logger,
    get_public_ip_and_isp,
    is_connected,
)

logger = get_logger(__name__)


# =============================================================================
# Reusable Widgets
# =============================================================================
class StatCard(ttk.Frame):
    """A large rounded stat card displaying a label, value, and unit."""

    def __init__(self, parent, palette: Palette, label: str, initial_value: str = "--", icon: str = "") -> None:
        super().__init__(parent, bootstyle="dark")
        self.palette = palette
        self.configure(padding=16)

        header = ttk.Frame(self)
        header.pack(fill="x")
        ttk.Label(header, text=f"{icon}  {label}".strip(), font=FONTS["card_label"], bootstyle="secondary").pack(
            side="left"
        )

        self.value_label = ttk.Label(self, text=initial_value, font=FONTS["card_value"])
        self.value_label.pack(anchor="w", pady=(10, 0))

    def set_value(self, value: str) -> None:
        """Update the displayed value text."""
        self.value_label.configure(text=value)


class SpeedGauge(tk.Canvas):
    """
    Animated circular speedometer drawn with raw Canvas primitives.
    The needle smoothly interpolates towards a target value on each
    animation tick so speed changes never feel abrupt.
    """

    def __init__(self, parent, palette: Palette, max_value: float = 200.0, size: int = 260) -> None:
        super().__init__(parent, width=size, height=size, highlightthickness=0, bg=palette.bg_card)
        self.palette = palette
        self.size = size
        self.max_value = max_value
        self.current_value = 0.0
        self.target_value = 0.0
        self._animating = False
        self._draw_static()

    def _draw_static(self) -> None:
        """Draw the non-changing parts of the gauge: arc track and tick marks."""
        self.delete("all")
        pad = 20
        self.arc_bbox = (pad, pad, self.size - pad, self.size - pad)

        # Background track (270 degree sweep, starting at 135deg)
        self.create_arc(
            *self.arc_bbox, start=225, extent=-270, style="arc", width=14,
            outline=self.palette.border,
        )
        self.value_arc_id = self.create_arc(
            *self.arc_bbox, start=225, extent=0, style="arc", width=14,
            outline=self.palette.accent,
        )

        self.needle_id = self.create_line(0, 0, 0, 0, fill=self.palette.text_primary, width=3)
        self.hub_id = self.create_oval(0, 0, 0, 0, fill=self.palette.accent, outline="")

        self.text_id = self.create_text(
            self.size / 2, self.size / 2 + 45, text="0.00", fill=self.palette.text_primary,
            font=FONTS["gauge_value"],
        )
        self.unit_id = self.create_text(
            self.size / 2, self.size / 2 + 70, text="Mbps", fill=self.palette.text_secondary,
            font=FONTS["small"],
        )
        self._update_needle(0.0)

    def set_max_value(self, max_value: float) -> None:
        """Rescale the gauge for a new maximum speed (auto-scaling)."""
        self.max_value = max(max_value, 10.0)

    def animate_to(self, value: float) -> None:
        """Begin smoothly animating the needle towards `value`."""
        self.target_value = min(value, self.max_value)
        if not self._animating:
            self._animating = True
            self._tick()

    def _tick(self) -> None:
        diff = self.target_value - self.current_value
        if abs(diff) < 0.05:
            self.current_value = self.target_value
            self._animating = False
        else:
            self.current_value += diff * 0.15
            self.after(16, self._tick)
        self._update_needle(self.current_value)

    def _update_needle(self, value: float) -> None:
        cx, cy = self.size / 2, self.size / 2
        radius = self.size / 2 - 40
        fraction = min(value / self.max_value, 1.0) if self.max_value else 0
        angle_deg = 225 - (fraction * 270)
        angle_rad = math.radians(angle_deg)

        x = cx + radius * math.cos(angle_rad)
        y = cy - radius * math.sin(angle_rad)

        self.coords(self.needle_id, cx, cy, x, y)
        self.coords(self.hub_id, cx - 8, cy - 8, cx + 8, cy + 8)
        self.itemconfigure(self.value_arc_id, extent=-fraction * 270)
        self.itemconfigure(self.text_id, text=f"{value:.2f}")

    def apply_palette(self, palette: Palette) -> None:
        """Re-theme the gauge colors after a theme change."""
        self.palette = palette
        self.configure(bg=palette.bg_card)
        self._draw_static()
        self._update_needle(self.current_value)


class LiveGraph(ttk.Frame):
    """Embeds a matplotlib line chart showing download/upload history."""

    def __init__(self, parent, palette: Palette) -> None:
        super().__init__(parent)
        self.palette = palette
        self.download_history: list[float] = []
        self.upload_history: list[float] = []

        self.figure = Figure(figsize=(5, 2.6), dpi=100)
        self.ax = self.figure.add_subplot(111)
        self.canvas = FigureCanvasTkAgg(self.figure, master=self)
        self.canvas.get_tk_widget().pack(fill="both", expand=True)
        self.apply_palette(palette)

    def add_point(self, download: float, upload: float) -> None:
        """Append a new download/upload data point and redraw the chart."""
        self.download_history.append(download)
        self.upload_history.append(upload)
        self.download_history = self.download_history[-30:]
        self.upload_history = self.upload_history[-30:]
        self._redraw()

    def _redraw(self) -> None:
        self.ax.clear()
        self.ax.plot(self.download_history, label="Download", color=self.palette.accent, linewidth=2)
        self.ax.plot(self.upload_history, label="Upload", color=self.palette.success, linewidth=2)
        self.ax.set_facecolor(self.palette.bg_card)
        self.ax.legend(loc="upper left", fontsize=7, facecolor=self.palette.bg_card, labelcolor=self.palette.text_primary)
        self.ax.tick_params(colors=self.palette.text_secondary, labelsize=7)
        for spine in self.ax.spines.values():
            spine.set_color(self.palette.border)
        self.figure.tight_layout()
        self.canvas.draw_idle()

    def apply_palette(self, palette: Palette) -> None:
        """Re-theme the chart colors after a theme change."""
        self.palette = palette
        self.figure.patch.set_facecolor(palette.bg_card)
        self._redraw()


# =============================================================================
# Dashboard View
# =============================================================================
class DashboardView(ttk.Frame):
    """The main dashboard: stat cards, gauge, live graph, and START TEST button."""

    def __init__(self, parent, palette: Palette, settings: Settings, on_start_test: Callable[[], None]) -> None:
        super().__init__(parent, padding=20)
        self.palette = palette
        self.settings = settings
        self.on_start_test = on_start_test
        self._build_layout()

    def _build_layout(self) -> None:
        top_row = ttk.Frame(self)
        top_row.pack(fill="x", pady=(0, 20))

        gauge_frame = ttk.Frame(top_row, bootstyle="dark", padding=16)
        gauge_frame.pack(side="left", padx=(0, 20))
        self.gauge = SpeedGauge(gauge_frame, self.palette)
        self.gauge.pack()

        control_frame = ttk.Frame(top_row, bootstyle="dark", padding=16)
        control_frame.pack(side="left", fill="both", expand=True)

        self.status_label = ttk.Label(control_frame, text="Ready to test your connection", font=FONTS["section_title"])
        self.status_label.pack(anchor="w")

        self.progress_bar = ttk.Progressbar(control_frame, bootstyle="success-striped", maximum=100, value=0)
        self.progress_bar.pack(fill="x", pady=(15, 15))

        self.start_button = ttk.Button(
            control_frame, text="START TEST", bootstyle="success", command=self.on_start_test, width=20
        )
        self.start_button.pack(anchor="w")

        info_frame = ttk.Frame(control_frame)
        info_frame.pack(fill="x", pady=(15, 0))
        self.conn_status_label = ttk.Label(info_frame, text="\u25cf Checking connection...", font=FONTS["body"])
        self.conn_status_label.pack(side="left")
        self.datetime_label = ttk.Label(info_frame, text="", font=FONTS["body"], bootstyle="secondary")
        self.datetime_label.pack(side="right")

        cards_frame = ttk.Frame(self)
        cards_frame.pack(fill="x", pady=(0, 20))
        for i in range(4):
            cards_frame.columnconfigure(i, weight=1)

        self.cards: dict[str, StatCard] = {}
        card_specs = [
            ("download", "Download", "\u25bc"),
            ("upload", "Upload", "\u25b2"),
            ("ping", "Ping", "\u25f7"),
            ("jitter", "Jitter", "\u2248"),
            ("public_ip", "Public IP", "IP"),
            ("isp", "ISP", "\u2302"),
            ("server", "Server", "SVR"),
            ("duration", "Test Duration", "\u23f1"),
        ]
        for idx, (key, label, icon) in enumerate(card_specs):
            row, col = divmod(idx, 4)
            card = StatCard(cards_frame, self.palette, label, icon=icon)
            card.grid(row=row, column=col, sticky="nsew", padx=6, pady=6)
            self.cards[key] = card

        graph_container = ttk.Frame(self, bootstyle="dark", padding=10)
        graph_container.pack(fill="both", expand=True)
        ttk.Label(graph_container, text="Live Speed History", font=FONTS["section_title"]).pack(anchor="w")
        self.graph = LiveGraph(graph_container, self.palette)
        self.graph.pack(fill="both", expand=True, pady=(10, 0))

    def set_status(self, message: str) -> None:
        self.status_label.configure(text=message)

    def set_progress(self, percent: float) -> None:
        self.progress_bar.configure(value=percent)

    def set_connection_status(self, connected: bool) -> None:
        if connected:
            self.conn_status_label.configure(text="\u25cf Connected", bootstyle="success")
        else:
            self.conn_status_label.configure(text="\u25cf Disconnected", bootstyle="danger")

    def update_datetime(self) -> None:
        self.datetime_label.configure(text=f"{current_date_str()}   {current_time_str()}")

    def set_test_running(self, running: bool) -> None:
        self.start_button.configure(state="disabled" if running else "normal")

    def display_result(self, result: SpeedTestResult) -> None:
        unit = self.settings.speed_unit
        self.cards["download"].set_value(format_speed(result.download_mbps, unit))
        self.cards["upload"].set_value(format_speed(result.upload_mbps, unit))
        self.cards["ping"].set_value(format_ping(result.ping_ms))
        self.cards["jitter"].set_value(format_ping(result.jitter_ms))
        self.cards["public_ip"].set_value(result.public_ip)
        self.cards["isp"].set_value(result.isp)
        self.cards["server"].set_value(f"{result.server_name} ({result.server_country})")
        self.cards["duration"].set_value(f"{result.duration_seconds:.1f} s")

        self.gauge.set_max_value(max(result.download_mbps, result.upload_mbps) * 1.3)
        self.gauge.animate_to(result.download_mbps)
        self.graph.add_point(result.download_mbps, result.upload_mbps)

    def apply_palette(self, palette: Palette) -> None:
        self.palette = palette
        self.gauge.apply_palette(palette)
        self.graph.apply_palette(palette)


# =============================================================================
# History View
# =============================================================================
class HistoryView(ttk.Frame):
    """Displays past speed test results in a searchable, sortable table."""

    def __init__(self, parent, palette: Palette, history_manager: HistoryManager, notifier: NotificationManager) -> None:
        super().__init__(parent, padding=20)
        self.palette = palette
        self.history_manager = history_manager
        self.notifier = notifier
        self._build_layout()
        self.refresh()

    def _build_layout(self) -> None:
        header = ttk.Frame(self)
        header.pack(fill="x", pady=(0, 15))
        ttk.Label(header, text="Test History", font=FONTS["section_title"]).pack(side="left")

        self.search_var = tk.StringVar()
        search_entry = ttk.Entry(header, textvariable=self.search_var, width=30)
        search_entry.pack(side="right", padx=(0, 5))
        search_entry.bind("<KeyRelease>", lambda e: self.refresh())
        ttk.Label(header, text="Search:").pack(side="right", padx=(0, 5))

        columns = ["Date", "Time", "Download", "Upload", "Ping", "Jitter", "ISP", "Server", "IP"]
        self.tree = ttk.Treeview(self, columns=columns, show="headings", bootstyle="dark")
        for col in columns:
            self.tree.heading(col, text=col, command=lambda c=col: self._sort_by(c))
            self.tree.column(col, width=110, anchor="center")
        self.tree.pack(fill="both", expand=True)

        action_bar = ttk.Frame(self)
        action_bar.pack(fill="x", pady=(10, 0))
        ttk.Button(action_bar, text="Delete Selected", bootstyle="danger-outline", command=self._delete_selected).pack(
            side="left"
        )
        ttk.Button(action_bar, text="Clear All", bootstyle="danger", command=self._clear_all).pack(
            side="left", padx=8
        )
        ttk.Button(action_bar, text="Export CSV", bootstyle="success-outline", command=self._export).pack(side="right")

        self._sort_column: Optional[str] = None
        self._sort_ascending = True

    def refresh(self) -> None:
        for row in self.tree.get_children():
            self.tree.delete(row)
        keyword = self.search_var.get()
        df = self.history_manager.search(keyword) if keyword else self.history_manager.load_dataframe()
        for _, row in df.iterrows():
            self.tree.insert("", "end", values=list(row))

    def _sort_by(self, column: str) -> None:
        self._sort_ascending = not self._sort_ascending if self._sort_column == column else True
        self._sort_column = column
        df = self.history_manager.sort(column, ascending=self._sort_ascending)
        for row in self.tree.get_children():
            self.tree.delete(row)
        for _, row in df.iterrows():
            self.tree.insert("", "end", values=list(row))

    def _delete_selected(self) -> None:
        selected = self.tree.selection()
        if not selected:
            return
        indices = sorted((self.tree.index(item) for item in selected), reverse=True)
        for idx in indices:
            self.history_manager.delete_record(idx)
        self.refresh()

    def _clear_all(self) -> None:
        if messagebox.askyesno("Clear History", "Delete all history records? This cannot be undone."):
            self.history_manager.clear_all()
            self.refresh()

    def _export(self) -> None:
        path = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV files", "*.csv")])
        if path:
            self.history_manager.export_csv(path)
            self.notifier.notify_history_exported(path)
            messagebox.showinfo("Export Complete", f"History exported to:\n{path}")

    def apply_palette(self, palette: Palette) -> None:
        self.palette = palette


# =============================================================================
# Reports View
# =============================================================================
class ReportsView(ttk.Frame):
    """Lets the user export the current history as CSV, PDF, or TXT."""

    def __init__(self, parent, palette: Palette, history_manager: HistoryManager, notifier: NotificationManager) -> None:
        super().__init__(parent, padding=20)
        self.palette = palette
        self.history_manager = history_manager
        self.report_generator = ReportGenerator()
        self.notifier = notifier
        self._build_layout()

    def _build_layout(self) -> None:
        ttk.Label(self, text="Generate Reports", font=FONTS["section_title"]).pack(anchor="w", pady=(0, 20))

        card = ttk.Frame(self, bootstyle="dark", padding=20)
        card.pack(fill="x")

        ttk.Label(card, text="Export your complete test history as a formatted report.", font=FONTS["body"]).pack(
            anchor="w", pady=(0, 15)
        )

        btn_frame = ttk.Frame(card)
        btn_frame.pack(anchor="w")
        ttk.Button(btn_frame, text="Export as CSV", bootstyle="info", command=lambda: self._export("csv")).pack(
            side="left", padx=(0, 10)
        )
        ttk.Button(btn_frame, text="Export as PDF", bootstyle="danger", command=lambda: self._export("pdf")).pack(
            side="left", padx=(0, 10)
        )
        ttk.Button(btn_frame, text="Export as TXT", bootstyle="secondary", command=lambda: self._export("txt")).pack(
            side="left"
        )

        self.result_label = ttk.Label(card, text="", font=FONTS["small"], bootstyle="success")
        self.result_label.pack(anchor="w", pady=(15, 0))

    def _export(self, fmt: str) -> None:
        df = self.history_manager.load_dataframe()
        try:
            if fmt == "csv":
                path = self.report_generator.export_csv(df)
            elif fmt == "pdf":
                path = self.report_generator.export_pdf(df)
            else:
                path = self.report_generator.export_txt(df)
            self.result_label.configure(text=f"Saved: {path}")
            self.notifier.notify_report_saved(path)
            messagebox.showinfo("Report Saved", f"Report saved to:\n{path}")
        except Exception as exc:  # noqa: BLE001
            logger.exception("Report export failed")
            messagebox.showerror("Export Failed", str(exc))

    def apply_palette(self, palette: Palette) -> None:
        self.palette = palette


# =============================================================================
# Settings View
# =============================================================================
class SettingsView(ttk.Frame):
    """Lets the user configure theme, units, notifications, and automation options."""

    def __init__(self, parent, palette: Palette, settings: Settings, on_theme_change: Callable[[str], None]) -> None:
        super().__init__(parent, padding=20)
        self.palette = palette
        self.settings = settings
        self.on_theme_change = on_theme_change
        self._build_layout()

    def _build_layout(self) -> None:
        ttk.Label(self, text="Settings", font=FONTS["section_title"]).pack(anchor="w", pady=(0, 20))
        card = ttk.Frame(self, bootstyle="dark", padding=20)
        card.pack(fill="x")

        ttk.Label(card, text="Theme", font=FONTS["body"]).grid(row=0, column=0, sticky="w", pady=8)
        self.theme_var = tk.StringVar(value=self.settings.theme_mode)
        theme_combo = ttk.Combobox(
            card, textvariable=self.theme_var, state="readonly",
            values=["dark", "light", "blue", "green", "purple"], width=20,
        )
        theme_combo.grid(row=0, column=1, sticky="w", padx=10)
        theme_combo.bind("<<ComboboxSelected>>", lambda e: self._apply_theme())

        ttk.Label(card, text="Speed Unit", font=FONTS["body"]).grid(row=1, column=0, sticky="w", pady=8)
        self.unit_var = tk.StringVar(value=self.settings.speed_unit)
        unit_combo = ttk.Combobox(
            card, textvariable=self.unit_var, state="readonly", values=["Mbps", "MBps", "Kbps"], width=20
        )
        unit_combo.grid(row=1, column=1, sticky="w", padx=10)
        unit_combo.bind("<<ComboboxSelected>>", lambda e: self._save())

        self.notif_var = tk.BooleanVar(value=self.settings.notifications_enabled)
        ttk.Checkbutton(
            card, text="Enable Desktop Notifications", variable=self.notif_var,
            bootstyle="round-toggle", command=self._save,
        ).grid(row=2, column=0, columnspan=2, sticky="w", pady=8)

        self.autosave_var = tk.BooleanVar(value=bool(self.settings.get("auto_save", "enabled", True)))
        ttk.Checkbutton(
            card, text="Auto-Save Results to History", variable=self.autosave_var,
            bootstyle="round-toggle", command=self._save,
        ).grid(row=3, column=0, columnspan=2, sticky="w", pady=8)

        self.autoexport_var = tk.BooleanVar(value=bool(self.settings.get("auto_export", "enabled", False)))
        ttk.Checkbutton(
            card, text="Auto-Export After Each Test", variable=self.autoexport_var,
            bootstyle="round-toggle", command=self._save,
        ).grid(row=4, column=0, columnspan=2, sticky="w", pady=8)

        ttk.Label(card, text="Animation Speed", font=FONTS["body"]).grid(row=5, column=0, sticky="w", pady=8)
        self.anim_var = tk.StringVar(value=self.settings.get("animation", "speed", "normal"))
        anim_combo = ttk.Combobox(
            card, textvariable=self.anim_var, state="readonly", values=["slow", "normal", "fast"], width=20
        )
        anim_combo.grid(row=5, column=1, sticky="w", padx=10)
        anim_combo.bind("<<ComboboxSelected>>", lambda e: self._save())

    def _apply_theme(self) -> None:
        self._save()
        self.on_theme_change(self.theme_var.get())

    def _save(self) -> None:
        self.settings.set("theme", "mode", self.theme_var.get())
        self.settings.set("units", "speed_unit", self.unit_var.get())
        self.settings.set("notifications", "enabled", self.notif_var.get())
        self.settings.set("auto_save", "enabled", self.autosave_var.get())
        self.settings.set("auto_export", "enabled", self.autoexport_var.get())
        self.settings.set("animation", "speed", self.anim_var.get())
        self.settings.save()

    def apply_palette(self, palette: Palette) -> None:
        self.palette = palette


# =============================================================================
# About View
# =============================================================================
class AboutView(ttk.Frame):
    """Static informational panel: app version, developer, libraries, license."""

    def __init__(self, parent, palette: Palette, settings: Settings) -> None:
        super().__init__(parent, padding=20)
        self.palette = palette
        self.settings = settings
        self._build_layout()

    def _build_layout(self) -> None:
        card = ttk.Frame(self, bootstyle="dark", padding=30)
        card.pack(fill="both", expand=True)

        ttk.Label(card, text=self.settings.get("app", "name", "Internet Speed Tester Pro"), font=FONTS["app_title"]).pack(
            anchor="w"
        )
        ttk.Label(card, text=f"Version {self.settings.get('app', 'version', '1.0.0')}", font=FONTS["body"]).pack(
            anchor="w", pady=(5, 20)
        )

        info_lines = [
            f"Developer: {self.settings.get('app', 'developer', 'Unknown')}",
            "Python Version: 3.12+",
            "Libraries: ttkbootstrap, speedtest-cli, matplotlib, pandas, reportlab, plyer, Pillow",
            f"License: {self.settings.get('app', 'license', 'MIT')}",
            f"GitHub: {self.settings.get('app', 'github', '')}",
        ]
        for line in info_lines:
            ttk.Label(card, text=line, font=FONTS["body"]).pack(anchor="w", pady=3)

    def apply_palette(self, palette: Palette) -> None:
        self.palette = palette


# =============================================================================
# Main Window (Controller)
# =============================================================================
class MainWindow:
    """
    Top-level application controller. Owns the sidebar, top bar, menu
    bar, status bar, and swaps the visible content view. Wires user
    actions (START TEST, export, theme change) to the model layer
    (SpeedTestWorker, HistoryManager, ReportGenerator, Settings) and
    always marshals background-thread callbacks back onto the main
    Tk loop with `root.after(0, ...)`.
    """

    def __init__(self, root: ttk.Window, settings: Settings) -> None:
        self.root = root
        self.settings = settings
        self.theme_manager = ThemeManager(initial_theme=settings.theme_mode)
        self.history_manager = HistoryManager(
            file_path=settings.history_file_path,
            max_records=settings.get("history", "max_records", 1000),
        )
        self.notifier = NotificationManager(enabled=settings.notifications_enabled)
        self._test_worker: Optional[SpeedTestWorker] = None
        self._current_view: Optional[ttk.Frame] = None
        self._views: dict[str, ttk.Frame] = {}

        self._build_menu_bar()
        self._build_shell()
        self._bind_shortcuts()
        self._start_clock_and_monitor()
        self.show_view("dashboard")

    # ------------------------------------------------------------------
    # Layout construction
    # ------------------------------------------------------------------
    def _build_menu_bar(self) -> None:
        menu_bar = tk.Menu(self.root)

        file_menu = tk.Menu(menu_bar, tearoff=False)
        file_menu.add_command(label="New Test (Ctrl+N)", command=self.run_speed_test)
        file_menu.add_command(label="Export (Ctrl+E)", command=lambda: self.show_view("reports"))
        file_menu.add_separator()
        file_menu.add_command(label="Settings", command=lambda: self.show_view("settings"))
        file_menu.add_separator()
        file_menu.add_command(label="Exit (Ctrl+Q)", command=self.root.destroy)
        menu_bar.add_cascade(label="File", menu=file_menu)

        view_menu = tk.Menu(menu_bar, tearoff=False)
        view_menu.add_command(label="Dashboard", command=lambda: self.show_view("dashboard"))
        view_menu.add_command(label="History", command=lambda: self.show_view("history"))
        view_menu.add_command(label="Reports", command=lambda: self.show_view("reports"))
        menu_bar.add_cascade(label="View", menu=view_menu)

        theme_menu = tk.Menu(menu_bar, tearoff=False)
        for theme_name in ["dark", "light", "blue", "green", "purple"]:
            theme_menu.add_command(
                label=theme_name.capitalize(), command=lambda t=theme_name: self.apply_theme(t)
            )
        menu_bar.add_cascade(label="Theme", menu=theme_menu)

        help_menu = tk.Menu(menu_bar, tearoff=False)
        help_menu.add_command(label="About", command=lambda: self.show_view("about"))
        help_menu.add_command(label="Check Updates", command=self._check_updates)
        menu_bar.add_cascade(label="Help", menu=help_menu)

        self.root.configure(menu=menu_bar)

    def _build_shell(self) -> None:
        palette = self.theme_manager.palette

        # Top bar
        self.top_bar = ttk.Frame(self.root, bootstyle="dark", padding=12)
        self.top_bar.pack(fill="x", side="top")
        ttk.Label(self.top_bar, text="Internet Speed Tester Pro", font=FONTS["app_title"]).pack(side="left")
        self.top_bar_run_btn = ttk.Button(
            self.top_bar, text="Run Test (F5)", bootstyle="success-outline", command=self.run_speed_test
        )
        self.top_bar_run_btn.pack(side="right")

        # Body: sidebar + content
        body = ttk.Frame(self.root)
        body.pack(fill="both", expand=True)

        self.sidebar = ttk.Frame(body, bootstyle="dark", padding=10, width=200)
        self.sidebar.pack(side="left", fill="y")
        self.sidebar.pack_propagate(False)

        nav_items = [
            ("dashboard", "Dashboard"),
            ("history", "History"),
            ("reports", "Reports"),
            ("settings", "Settings"),
            ("about", "About"),
        ]
        self.nav_buttons: dict[str, ttk.Button] = {}
        for key, label in nav_items:
            btn = ttk.Button(
                self.sidebar, text=label, bootstyle="secondary",
                command=lambda k=key: self.show_view(k),
            )
            btn.pack(fill="x", pady=4)
            self.nav_buttons[key] = btn

        ttk.Separator(self.sidebar).pack(fill="x", pady=10)
        ttk.Button(self.sidebar, text="Exit", bootstyle="danger-outline", command=self.root.destroy).pack(fill="x")

        self.content_container = ttk.Frame(body)
        self.content_container.pack(side="left", fill="both", expand=True)

        # Status bar
        self.status_bar = ttk.Frame(self.root, bootstyle="dark", padding=6)
        self.status_bar.pack(fill="x", side="bottom")
        self.status_bar_ready_label = ttk.Label(self.status_bar, text="Ready", font=FONTS["small"])
        self.status_bar_ready_label.pack(side="left", padx=10)
        self.status_bar_python_label = ttk.Label(self.status_bar, text="Python 3.12+", font=FONTS["small"])
        self.status_bar_python_label.pack(side="left", padx=10)
        self.status_bar_conn_label = ttk.Label(self.status_bar, text="Checking...", font=FONTS["small"])
        self.status_bar_conn_label.pack(side="left", padx=10)
        self.status_bar_theme_label = ttk.Label(
            self.status_bar, text=f"Theme: {self.theme_manager.theme_name.capitalize()}", font=FONTS["small"]
        )
        self.status_bar_theme_label.pack(side="right", padx=10)

        # Instantiate views
        self._views["dashboard"] = DashboardView(
            self.content_container, palette, self.settings, on_start_test=self.run_speed_test
        )
        self._views["history"] = HistoryView(self.content_container, palette, self.history_manager, self.notifier)
        self._views["reports"] = ReportsView(self.content_container, palette, self.history_manager, self.notifier)
        self._views["settings"] = SettingsView(self.content_container, palette, self.settings, self.apply_theme)
        self._views["about"] = AboutView(self.content_container, palette, self.settings)

    def _bind_shortcuts(self) -> None:
        self.root.bind("<Control-n>", lambda e: self.run_speed_test())
        self.root.bind("<Control-s>", lambda e: self.settings.save())
        self.root.bind("<Control-e>", lambda e: self.show_view("reports"))
        self.root.bind("<Control-q>", lambda e: self.root.destroy())
        self.root.bind("<F5>", lambda e: self.run_speed_test())

    # ------------------------------------------------------------------
    # View switching
    # ------------------------------------------------------------------
    def show_view(self, key: str) -> None:
        """Show the requested view and hide all others."""
        if self._current_view is not None:
            self._current_view.pack_forget()
        view = self._views[key]
        view.pack(fill="both", expand=True)
        self._current_view = view
        if key == "history":
            view.refresh()
        for nav_key, btn in self.nav_buttons.items():
            btn.configure(bootstyle="success" if nav_key == key else "secondary")

    # ------------------------------------------------------------------
    # Speed test execution
    # ------------------------------------------------------------------
    def run_speed_test(self) -> None:
        """Kick off a new speed test on a background thread."""
        if self._test_worker is not None:
            return  # A test is already running

        dashboard = self._views["dashboard"]
        dashboard.set_test_running(True)
        dashboard.set_progress(0)
        dashboard.set_status("Connecting...")

        self._test_worker = SpeedTestWorker(
            on_status=lambda msg: self.root.after(0, self._on_test_status, msg),
            on_progress=lambda pct: self.root.after(0, self._on_test_progress, pct),
            on_complete=lambda result: self.root.after(0, self._on_test_complete, result),
            on_error=lambda msg: self.root.after(0, self._on_test_error, msg),
        )
        self._test_worker.start()

    def _on_test_status(self, message: str) -> None:
        self._views["dashboard"].set_status(message)
        self.status_bar_ready_label.configure(text=message)

    def _on_test_progress(self, percent: float) -> None:
        self._views["dashboard"].set_progress(percent)

    def _on_test_complete(self, result: SpeedTestResult) -> None:
        dashboard = self._views["dashboard"]
        dashboard.display_result(result)
        dashboard.set_test_running(False)
        self.status_bar_ready_label.configure(text="Ready")
        self._test_worker = None

        if self.settings.get("auto_save", "enabled", True):
            self.history_manager.add_result(result)
            self._views["history"].refresh()

        if self.settings.get("notifications", "notify_on_test_complete", True):
            self.notifier.notify_test_complete(result.download_mbps, result.upload_mbps, self.settings.speed_unit)

        if self.settings.get("auto_export", "enabled", False):
            fmt = self.settings.get("auto_export", "format", "csv")
            report_gen = self._views["reports"].report_generator
            df = self.history_manager.load_dataframe()
            if fmt == "pdf":
                report_gen.export_pdf(df)
            elif fmt == "txt":
                report_gen.export_txt(df)
            else:
                report_gen.export_csv(df)

    def _on_test_error(self, message: str) -> None:
        dashboard = self._views["dashboard"]
        dashboard.set_test_running(False)
        dashboard.set_status("Test failed")
        self.status_bar_ready_label.configure(text="Ready")
        self._test_worker = None
        messagebox.showerror("Speed Test Error", message)

    # ------------------------------------------------------------------
    # Theme handling
    # ------------------------------------------------------------------
    def apply_theme(self, theme_name: str) -> None:
        """Switch the active theme and restyle the whole window tree."""
        self.theme_manager.set_theme(theme_name)
        palette = self.theme_manager.palette

        style = ttk.Style()
        style.theme_use(palette.bootstyle)

        for view in self._views.values():
            view.apply_palette(palette)

        self.status_bar_theme_label.configure(text=f"Theme: {theme_name.capitalize()}")
        self.settings.set("theme", "mode", theme_name)
        self.settings.save()

    # ------------------------------------------------------------------
    # Background monitors
    # ------------------------------------------------------------------
    def _start_clock_and_monitor(self) -> None:
        self._tick_clock()
        self._tick_network_monitor(previous_state={"connected": None})

    def _tick_clock(self) -> None:
        self._views["dashboard"].update_datetime()
        self.root.after(1000, self._tick_clock)

    def _tick_network_monitor(self, previous_state: dict) -> None:
        connected = is_connected()
        self._views["dashboard"].set_connection_status(connected)
        self.status_bar_conn_label.configure(text="Online" if connected else "Offline")

        if previous_state["connected"] is not None and previous_state["connected"] != connected:
            if connected:
                self.notifier.notify_reconnected()
            elif self.settings.get("notifications", "notify_on_disconnect", True):
                self.notifier.notify_disconnected()
        previous_state["connected"] = connected

        interval_ms = int(self.settings.get("network", "monitor_interval_seconds", 5)) * 1000
        self.root.after(interval_ms, self._tick_network_monitor, previous_state)

    def _check_updates(self) -> None:
        messagebox.showinfo(
            "Check Updates",
            f"You are running version {self.settings.get('app', 'version', '1.0.0')}.\n"
            "Visit the GitHub repository to check for the latest release.",
        )
