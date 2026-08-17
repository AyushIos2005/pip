from __future__ import annotations
import json
import os
import sys
from datetime import datetime
from typing import Optional

import tkinter as tk
from tkinter import ttk, messagebox

from themes import ThemeManager, VALID_THEMES
from clock_module import ClockFrame, WorldClockFrame
from stopwatch import Stopwatch
from timer import Timer
from alarm import AlarmFrame

APP_NAME = "Smart Clock"
APP_VERSION = "1.2.0"
DEVELOPER = "CODEHUB Team-@VGI"


BASE_DIR = os.path.dirname(os.path.abspath(__file__))
SETTINGS_FILE = os.path.join(BASE_DIR, "settings.json")
ASSETS_DIR = os.path.join(BASE_DIR, "assets")
ICON_PATH = os.path.join(ASSETS_DIR, "icon.ico")
SPLASH_LOGO_PATH = os.path.join(ASSETS_DIR, "splash.png")

DEFAULT_SETTINGS = {
    "theme": "dark",
    "time_format": "12",
    "notifications": True,
    "hourly_chime": False,
    "alarm_volume": 80,
}


# ------------------------------------------------------------------
def load_settings() -> dict:
    """Load settings.json, tolerating a missing or corrupted file."""
    if not os.path.isfile(SETTINGS_FILE):
        return DEFAULT_SETTINGS.copy()
    try:
        with open(SETTINGS_FILE, "r", encoding="utf-8") as f:
            data = json.load(f)
        merged = DEFAULT_SETTINGS.copy()
        merged.update(data if isinstance(data, dict) else {})
        return merged
    except (json.JSONDecodeError, OSError) as exc:
        print(f"[Settings] Corrupted or unreadable settings.json, using defaults: {exc}")
        return DEFAULT_SETTINGS.copy()


def save_settings(settings: dict) -> None:
    """Persist settings.json to disk."""
    try:
        with open(SETTINGS_FILE, "w", encoding="utf-8") as f:
            json.dump(settings, f, indent=4)
    except OSError as exc:
        print(f"[Settings] Could not save settings.json: {exc}")


# ------------------------------------------------------------------
class SplashScreen(tk.Toplevel):
    """A borderless splash screen shown for a few seconds at startup."""

    def __init__(self, root: tk.Tk, duration_ms: int = 3000) -> None:
        super().__init__(root)
        self.overrideredirect(True)
        self.configure(bg="#121212")

        width, height = 420, 280
        screen_w = self.winfo_screenwidth()
        screen_h = self.winfo_screenheight()
        x = (screen_w - width) // 2
        y = (screen_h - height) // 2
        self.geometry(f"{width}x{height}+{x}+{y}")

        self._logo_img: Optional[tk.PhotoImage] = None
        if os.path.isfile(SPLASH_LOGO_PATH):
            try:
                self._logo_img = tk.PhotoImage(file=SPLASH_LOGO_PATH)
                tk.Label(self, image=self._logo_img, bg="#121212").pack(pady=(30, 10))
            except tk.TclError as exc:
                print(f"[Splash] Could not load splash image: {exc}")

        tk.Label(
            self, text=APP_NAME, fg="#0a84ff", bg="#121212",
            font=("Segoe UI", 22, "bold")
        ).pack(pady=(10, 4))

        self.loading_label = tk.Label(
            self, text="Loading...", fg="#eaeaea", bg="#121212",
            font=("Segoe UI", 11)
        )
        self.loading_label.pack(pady=4)

        self._alpha = 0.0
        try:
            self.attributes("-alpha", self._alpha)
        except tk.TclError:
            pass

        self.after(10, self._fade_in)
        self.after(duration_ms, self._fade_out_and_close)

    # ------------------------------------------------------------
    def _fade_in(self) -> None:
        try:
            self._alpha = min(self._alpha + 0.08, 1.0)
            self.attributes("-alpha", self._alpha)
            if self._alpha < 1.0:
                self.after(20, self._fade_in)
        except tk.TclError:
            pass

    # ------------------------------------------------------------
    def _fade_out_and_close(self) -> None:
        try:
            self._alpha = max(self._alpha - 0.1, 0.0)
            self.attributes("-alpha", self._alpha)
            if self._alpha > 0.0:
                self.after(20, self._fade_out_and_close)
            else:
                self.destroy()
        except tk.TclError:
            self.destroy()


# ------------------------------------------------------------------
class SmartTimeSuiteApp:
    """Main application controller: builds and wires the dashboard UI."""

    def __init__(self, root: tk.Tk) -> None:
        self.root = root
        self.settings = load_settings()

        self.root.title(APP_NAME)
        self.root.geometry("1000x650")
        self.root.minsize(820, 560)

        self._set_icon()

        self.theme_manager = ThemeManager(self.root, self.settings.get("theme", "dark"))
        self.theme_manager.subscribe(self._on_theme_changed)

        self._current_module_name = "Clock"
        self._module_frame: Optional[ttk.Frame] = None

        self._build_menu()
        self._build_layout()
        self._bind_shortcuts()
        self.show_module("Clock")

        self._tick_status_clock()

        self.root.protocol("WM_DELETE_WINDOW", self.on_exit)

    # ------------------------------------------------------------
    def _set_icon(self) -> None:
        """Set the window icon, gracefully skipping if the file is missing."""
        if os.path.isfile(ICON_PATH):
            try:
                self.root.iconbitmap(ICON_PATH)
            except tk.TclError as exc:
                print(f"[Icon] Could not set icon: {exc}")
        else:
            print("[Icon] icon.ico not found - using default window icon.")

    # ------------------------------------------------------------
    def _build_menu(self) -> None:
        menubar = tk.Menu(self.root)

        file_menu = tk.Menu(menubar, tearoff=0)
        file_menu.add_command(label="Exit", command=self.on_exit, accelerator="Ctrl+Q")
        menubar.add_cascade(label="File", menu=file_menu)

        view_menu = tk.Menu(menubar, tearoff=0)
        view_menu.add_command(label="Clock", command=lambda: self.show_module("Clock"))
        view_menu.add_command(label="Stopwatch", command=lambda: self.show_module("Stopwatch"))
        view_menu.add_command(label="Timer", command=lambda: self.show_module("Timer"))
        view_menu.add_command(label="Alarm", command=lambda: self.show_module("Alarm"))
        view_menu.add_command(label="World Clock", command=lambda: self.show_module("World Clock"))
        menubar.add_cascade(label="View", menu=view_menu)

        theme_menu = tk.Menu(menubar, tearoff=0)
        for theme_name in VALID_THEMES:
            theme_menu.add_command(
                label=theme_name.capitalize(),
                command=lambda t=theme_name: self.set_theme(t),
            )
        menubar.add_cascade(label="Theme", menu=theme_menu)

        help_menu = tk.Menu(menubar, tearoff=0)
        help_menu.add_command(label="About", command=self.show_about)
        menubar.add_cascade(label="Help", menu=help_menu)

        self.root.config(menu=menubar)

    # ------------------------------------------------------------
    def _build_layout(self) -> None:
        self.root.columnconfigure(0, weight=0)
        self.root.columnconfigure(1, weight=1)
        self.root.rowconfigure(1, weight=1)

        # --- Top bar -------------------------------------------------
        self.top_bar = ttk.Frame(self.root, style="TFrame", padding=12)
        self.top_bar.grid(row=0, column=0, columnspan=2, sticky="ew")
        self.top_bar.columnconfigure(1, weight=1)

        ttk.Label(self.top_bar, text=APP_NAME, style="Title.TLabel").grid(
            row=0, column=0, sticky="w"
        )

        self.date_label_top = ttk.Label(self.top_bar, text="", style="TLabel")
        self.date_label_top.grid(row=0, column=1, sticky="e", padx=(0, 12))

        self.theme_toggle_btn = ttk.Button(
            self.top_bar, text="Toggle Theme", command=self._cycle_theme
        )
        self.theme_toggle_btn.grid(row=0, column=2, sticky="e")

        # --- Sidebar ---------------------------------------------------
        self.sidebar = ttk.Frame(self.root, style="Sidebar.TFrame", padding=10, width=190)
        self.sidebar.grid(row=1, column=0, sticky="ns")
        self.sidebar.grid_propagate(False)

        self._nav_buttons: dict[str, ttk.Button] = {}
        nav_items = ["Clock", "Stopwatch", "Timer", "Alarm", "World Clock", "Settings", "About"]
        for i, item in enumerate(nav_items):
            btn = ttk.Button(
                self.sidebar, text=item, style="Sidebar.TButton",
                command=lambda name=item: self._on_nav_click(name),
            )
            btn.grid(row=i, column=0, sticky="ew", pady=4)
            self._nav_buttons[item] = btn
        self.sidebar.columnconfigure(0, weight=1)

        # --- Content area ------------------------------------------
        self.content_area = ttk.Frame(self.root, style="TFrame", padding=10)
        self.content_area.grid(row=1, column=1, sticky="nsew")
        self.content_area.columnconfigure(0, weight=1)
        self.content_area.rowconfigure(0, weight=1)

        # --- Status bar ----------------------------------------------
        self.status_bar = ttk.Frame(self.root, style="Status.TFrame", padding=6)
        self.status_bar.grid(row=2, column=0, columnspan=2, sticky="ew")
        self.status_bar.columnconfigure(1, weight=1)

        self.status_mode_label = ttk.Label(self.status_bar, text="Ready", style="Status.TLabel")
        self.status_mode_label.grid(row=0, column=0, sticky="w", padx=8)

        self.status_theme_label = ttk.Label(
            self.status_bar, text=f"Theme: {self.theme_manager.current_theme.capitalize()}",
            style="Status.TLabel"
        )
        self.status_theme_label.grid(row=0, column=1, sticky="w", padx=8)

        self.status_time_label = ttk.Label(self.status_bar, text="", style="Status.TLabel")
        self.status_time_label.grid(row=0, column=2, sticky="e", padx=8)

    # ------------------------------------------------------------
    def _on_nav_click(self, name: str) -> None:
        if name == "Settings":
            self.show_settings()
        elif name == "About":
            self.show_about()
        else:
            self.show_module(name)

    # ------------------------------------------------------------
    def show_module(self, name: str) -> None:
        """Swap the content area to display the requested module."""
        if self._module_frame is not None:
            self._module_frame.destroy()
            self._module_frame = None

        if name == "Clock":
            self._module_frame = ClockFrame(self.content_area, self.settings)
        elif name == "Stopwatch":
            self._module_frame = Stopwatch(self.content_area)
        elif name == "Timer":
            self._module_frame = Timer(self.content_area, self.settings)
        elif name == "Alarm":
            self._module_frame = AlarmFrame(self.content_area, self.settings)
        elif name == "World Clock":
            self._module_frame = WorldClockFrame(self.content_area)
        else:
            return

        self._module_frame.grid(row=0, column=0, sticky="nsew")
        self._current_module_name = name
        self.status_mode_label.config(text=f"Mode: {name}")

    # ------------------------------------------------------------
    def show_settings(self) -> None:
        """Open a settings dialog for persisted preferences."""
        win = tk.Toplevel(self.root)
        win.title("Settings")
        win.transient(self.root)
        win.grab_set()
        win.geometry("360x300")

        row = 0
        ttk.Label(win, text="Theme:").grid(row=row, column=0, sticky="w", padx=10, pady=8)
        theme_var = tk.StringVar(value=self.settings.get("theme", "dark"))
        theme_combo = ttk.Combobox(
            win, textvariable=theme_var, values=VALID_THEMES, state="readonly"
        )
        theme_combo.grid(row=row, column=1, sticky="ew", padx=10, pady=8)
        row += 1

        ttk.Label(win, text="Time Format:").grid(row=row, column=0, sticky="w", padx=10, pady=8)
        fmt_var = tk.StringVar(value=self.settings.get("time_format", "12"))
        fmt_combo = ttk.Combobox(
            win, textvariable=fmt_var, values=["12", "24"], state="readonly"
        )
        fmt_combo.grid(row=row, column=1, sticky="ew", padx=10, pady=8)
        row += 1

        notif_var = tk.BooleanVar(value=self.settings.get("notifications", True))
        ttk.Checkbutton(win, text="Enable Notifications", variable=notif_var).grid(
            row=row, column=0, columnspan=2, sticky="w", padx=10, pady=8
        )
        row += 1

        chime_var = tk.BooleanVar(value=self.settings.get("hourly_chime", False))
        ttk.Checkbutton(win, text="Hourly Chime (optional)", variable=chime_var).grid(
            row=row, column=0, columnspan=2, sticky="w", padx=10, pady=8
        )
        row += 1

        ttk.Label(win, text="Alarm Volume:").grid(row=row, column=0, sticky="w", padx=10, pady=8)
        vol_var = tk.IntVar(value=self.settings.get("alarm_volume", 80))
        ttk.Scale(win, from_=0, to=100, variable=vol_var, orient="horizontal").grid(
            row=row, column=1, sticky="ew", padx=10, pady=8
        )
        row += 1

        win.columnconfigure(1, weight=1)

        def apply_and_close() -> None:
            self.settings["time_format"] = fmt_var.get()
            self.settings["notifications"] = notif_var.get()
            self.settings["hourly_chime"] = chime_var.get()
            self.settings["alarm_volume"] = vol_var.get()
            self.set_theme(theme_var.get())
            save_settings(self.settings)
            win.destroy()

        ttk.Button(win, text="Save", command=apply_and_close).grid(
            row=row, column=0, columnspan=2, pady=16
        )

    # ------------------------------------------------------------
    def show_about(self) -> None:
        win = tk.Toplevel(self.root)
        win.title("About Smart Time Suite")
        win.geometry("360x260")
        win.transient(self.root)
        win.grab_set()

        ttk.Label(win, text=APP_NAME, font=("Segoe UI", 16, "bold")).pack(pady=(20, 4))
        ttk.Label(win, text=f"Version {APP_VERSION}").pack(pady=2)
        ttk.Label(win, text=f"Developer: {DEVELOPER}").pack(pady=2)
        ttk.Label(
            win, text=f"Python {sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}"
        ).pack(pady=2)
        ttk.Label(win, text=GITHUB_URL, foreground="#0a84ff").pack(pady=(10, 4))
        ttk.Label(
            win, text="A modern, modular desktop time-management suite\nbuilt with Python & Tkinter.",
            justify="center"
        ).pack(pady=10)

        ttk.Button(win, text="Close", command=win.destroy).pack(pady=10)

    # ------------------------------------------------------------
    def _cycle_theme(self) -> None:
        idx = VALID_THEMES.index(self.theme_manager.current_theme)
        next_theme = VALID_THEMES[(idx + 1) % len(VALID_THEMES)]
        self.set_theme(next_theme)

    # ------------------------------------------------------------
    def set_theme(self, theme_name: str) -> None:
        self.theme_manager.apply_theme(theme_name)
        self.settings["theme"] = theme_name
        save_settings(self.settings)

    # ------------------------------------------------------------
    def _on_theme_changed(self, colors: dict) -> None:
        """Callback fired by ThemeManager whenever the theme changes."""
        self.status_theme_label.config(
            text=f"Theme: {self.theme_manager.current_theme.capitalize()}"
        )

    # ------------------------------------------------------------
    def _bind_shortcuts(self) -> None:
        self.root.bind_all("<Control-1>", lambda e: self.show_module("Clock"))
        self.root.bind_all("<Control-2>", lambda e: self.show_module("Stopwatch"))
        self.root.bind_all("<Control-3>", lambda e: self.show_module("Timer"))
        self.root.bind_all("<Control-4>", lambda e: self.show_module("Alarm"))
        self.root.bind_all("<Control-5>", lambda e: self.show_module("World Clock"))
        self.root.bind_all("<Control-q>", lambda e: self.on_exit())
        self.root.bind_all("<Control-Q>", lambda e: self.on_exit())

    # ------------------------------------------------------------
    def _tick_status_clock(self) -> None:
        now = datetime.now()
        self.status_time_label.config(text=now.strftime("%I:%M:%S %p"))
        self.date_label_top.config(text=now.strftime("%A, %d %B %Y"))
        self.root.after(1000, self._tick_status_clock)

    # ------------------------------------------------------------
    def on_exit(self) -> None:
        """Save settings and close the application cleanly."""
        try:
            save_settings(self.settings)
        finally:
            self.root.destroy()


# ------------------------------------------------------------------
def main() -> None:
    root = tk.Tk()
    root.withdraw()  # Hide main window while splash is shown

    splash_duration = 3000
    splash = SplashScreen(root, duration_ms=splash_duration)

    def launch_app() -> None:
        try:
            root.deiconify()
            SmartTimeSuiteApp(root)
        except Exception as exc:  # pragma: no cover - top-level safety net
            messagebox.showerror("Smart Time Suite - Fatal Error", str(exc))
            root.destroy()

    root.after(splash_duration + 50, launch_app)
    root.mainloop()


if __name__ == "__main__":
    main()
