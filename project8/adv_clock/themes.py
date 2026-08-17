
from __future__ import annotations
from typing import Dict, Callable, List
import tkinter as tk
from tkinter import ttk


# ------------------------------------------------------------------
# Theme color palettes
# ------------------------------------------------------------------
THEMES: Dict[str, Dict[str, str]] = {
    "light": {
        "bg": "#f5f5f7",
        "fg": "#1c1c1e",
        "sidebar_bg": "#e6e6ea",
        "accent": "#0a84ff",
        "accent_fg": "#ffffff",
        "card_bg": "#ffffff",
        "border": "#d1d1d6",
        "status_bg": "#e6e6ea",
        "danger": "#ff3b30",
        "success": "#34c759",
        "muted": "#6e6e73",
    },
    "dark": {
        "bg": "#1c1c1e",
        "fg": "#f5f5f7",
        "sidebar_bg": "#121212",
        "accent": "#0a84ff",
        "accent_fg": "#ffffff",
        "card_bg": "#2c2c2e",
        "border": "#3a3a3c",
        "status_bg": "#121212",
        "danger": "#ff453a",
        "success": "#32d74b",
        "muted": "#9a9a9e",
    },
    "blue": {
        "bg": "#0f1c2e",
        "fg": "#eaf2fb",
        "sidebar_bg": "#0a1420",
        "accent": "#3d9dff",
        "accent_fg": "#ffffff",
        "card_bg": "#16283f",
        "border": "#25405f",
        "status_bg": "#0a1420",
        "danger": "#ff5c5c",
        "success": "#3ddc97",
        "muted": "#8ba7c4",
    },
    "green": {
        "bg": "#0f2418",
        "fg": "#eafff2",
        "sidebar_bg": "#0a1a11",
        "accent": "#2ecc71",
        "accent_fg": "#03150a",
        "card_bg": "#163a26",
        "border": "#245b3a",
        "status_bg": "#0a1a11",
        "danger": "#ff6b6b",
        "success": "#2ecc71",
        "muted": "#8fbfa4",
    },
    "purple": {
        "bg": "#1a1330",
        "fg": "#f3eeff",
        "sidebar_bg": "#120c22",
        "accent": "#a259ff",
        "accent_fg": "#ffffff",
        "card_bg": "#241a3d",
        "border": "#3a2a5c",
        "status_bg": "#120c22",
        "danger": "#ff6b81",
        "success": "#4bd8a3",
        "muted": "#b6a6d9",
    },
}

VALID_THEMES: List[str] = list(THEMES.keys())


class ThemeManager:
    """
    Centralized theme manager.

    Keeps track of the currently active theme, exposes the color
    palette, configures ttk styles, and notifies subscribers whenever
    the theme changes so they can refresh their own widgets.
    """

    def __init__(self, root: tk.Tk, initial_theme: str = "dark") -> None:
        self.root = root
        self.style = ttk.Style(root)
        # 'clam' allows full color customization on every platform.
        try:
            self.style.theme_use("clam")
        except tk.TclError:
            pass

        self.current_theme: str = initial_theme if initial_theme in THEMES else "dark"
        self._subscribers: List[Callable[[Dict[str, str]], None]] = []

        self.apply_theme(self.current_theme)

    # ------------------------------------------------------------
    def colors(self) -> Dict[str, str]:
        """Return the color dictionary for the active theme."""
        return THEMES[self.current_theme]

    # ------------------------------------------------------------
    def subscribe(self, callback: Callable[[Dict[str, str]], None]) -> None:
        """Register a callback invoked with the palette on every theme change."""
        self._subscribers.append(callback)

    # ------------------------------------------------------------
    def apply_theme(self, theme_name: str) -> None:
        """Apply a theme by name across ttk styles and notify subscribers."""
        if theme_name not in THEMES:
            theme_name = "dark"
        self.current_theme = theme_name
        c = THEMES[theme_name]

        self.root.configure(bg=c["bg"])

        # General ttk widget styles
        self.style.configure("TFrame", background=c["bg"])
        self.style.configure("Card.TFrame", background=c["card_bg"])
        self.style.configure("Sidebar.TFrame", background=c["sidebar_bg"])
        self.style.configure("Status.TFrame", background=c["status_bg"])

        self.style.configure(
            "TLabel", background=c["bg"], foreground=c["fg"], font=("Segoe UI", 10)
        )
        self.style.configure(
            "Card.TLabel", background=c["card_bg"], foreground=c["fg"]
        )
        self.style.configure(
            "Sidebar.TLabel", background=c["sidebar_bg"], foreground=c["fg"]
        )
        self.style.configure(
            "Status.TLabel", background=c["status_bg"], foreground=c["muted"]
        )
        self.style.configure(
            "Title.TLabel",
            background=c["bg"],
            foreground=c["fg"],
            font=("Segoe UI", 20, "bold"),
        )
        self.style.configure(
            "Clock.TLabel",
            background=c["bg"],
            foreground=c["accent"],
            font=("Consolas", 48, "bold"),
        )
        self.style.configure(
            "SubClock.TLabel",
            background=c["bg"],
            foreground=c["muted"],
            font=("Segoe UI", 14),
        )

        self.style.configure(
            "TButton",
            background=c["accent"],
            foreground=c["accent_fg"],
            font=("Segoe UI", 10, "bold"),
            padding=8,
            borderwidth=0,
        )
        self.style.map(
            "TButton",
            background=[("active", c["accent"]), ("disabled", c["border"])],
        )

        self.style.configure(
            "Sidebar.TButton",
            background=c["sidebar_bg"],
            foreground=c["fg"],
            font=("Segoe UI", 11),
            padding=10,
            borderwidth=0,
            anchor="w",
        )
        self.style.map(
            "Sidebar.TButton",
            background=[("active", c["accent"])],
            foreground=[("active", c["accent_fg"])],
        )

        self.style.configure(
            "Danger.TButton", background=c["danger"], foreground="#ffffff"
        )
        self.style.map("Danger.TButton", background=[("active", c["danger"])])

        self.style.configure(
            "Success.TButton", background=c["success"], foreground="#08240f"
        )
        self.style.map("Success.TButton", background=[("active", c["success"])])

        self.style.configure(
            "TEntry",
            fieldbackground=c["card_bg"],
            foreground=c["fg"],
            insertcolor=c["fg"],
        )

        self.style.configure(
            "Treeview",
            background=c["card_bg"],
            fieldbackground=c["card_bg"],
            foreground=c["fg"],
            rowheight=28,
        )
        self.style.configure(
            "Treeview.Heading",
            background=c["sidebar_bg"],
            foreground=c["fg"],
            font=("Segoe UI", 10, "bold"),
        )
        self.style.map("Treeview", background=[("selected", c["accent"])])

        self.style.configure(
            "TCheckbutton", background=c["bg"], foreground=c["fg"]
        )
        self.style.configure(
            "TRadiobutton", background=c["bg"], foreground=c["fg"]
        )
        self.style.configure("TScale", background=c["bg"])
        self.style.configure(
            "Horizontal.TSeparator", background=c["border"]
        )

        # Notify all subscribed widgets so they can refresh non-ttk elements
        for callback in self._subscribers:
            try:
                callback(c)
            except Exception as exc:  # pragma: no cover - defensive
                print(f"[ThemeManager] Subscriber refresh failed: {exc}")
