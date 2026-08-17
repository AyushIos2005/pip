"""
main.py
-------
Application entry point for Internet Speed Tester Pro.

Flow:
    1. Show an animated splash screen ("Internet Speed Tester Pro /
       Loading...") for the configured duration (default 3 seconds).
    2. Destroy the splash and build the main application window
       (MainWindow from dashboard.py) inside a ttkbootstrap Window.

Run with:
    python main.py
"""

from __future__ import annotations

import sys
import tkinter as tk

import ttkbootstrap as ttk

from dashboard import MainWindow
from settings import Settings
from themes import FONTS
from utils import ensure_directories, get_logger

logger = get_logger(__name__)


class SplashScreen(tk.Toplevel):
    """
    Borderless animated splash screen shown while the application
    warms up. Displays the app name, a "Loading..." caption with an
    animated ellipsis, and a thin progress indicator.
    """

    def __init__(self, master: tk.Tk, duration_ms: int, on_finished) -> None:
        super().__init__(master)
        self.on_finished = on_finished
        self.duration_ms = duration_ms
        self._dot_count = 0

        self.overrideredirect(True)  # Borderless window
        self.configure(bg="#0F172A")

        width, height = 1080, 300
        self.update_idletasks()
        screen_w = self.winfo_screenwidth()
        screen_h = self.winfo_screenheight()
        x = (screen_w - width) // 2
        y = (screen_h - height) // 2
        self.geometry(f"{width}x{height}+{x}+{y}")

        container = tk.Frame(self, bg="#0F172A")
        container.pack(fill="both", expand=True)

        tk.Label(
            container, text="\U0001F4E1", font=("Segoe UI", 40), bg="#0F172A", fg="#2563EB"
        ).pack(pady=(50, 10))

        tk.Label(
            container, text="Internet Speed Tester Pro",
            font=FONTS["splash_title"], bg="#0F172A", fg="#F8FAFC",
        ).pack()

        self.loading_label = tk.Label(
            container, text="Loading", font=FONTS["splash_subtitle"], bg="#0F172A", fg="#94A3B8"
        )
        self.loading_label.pack(pady=(15, 20))

        self.progress = ttk.Progressbar(
            container, mode="determinate", maximum=100, value=0, length=320, bootstyle="success-striped"
        )
        self.progress.pack()

        self._animate_dots()
        self._animate_progress(elapsed=0)

    def _animate_dots(self) -> None:
        self._dot_count = (self._dot_count + 1) % 4
        self.loading_label.configure(text="Loading" + "." * self._dot_count)
        self.after(400, self._animate_dots)

    def _animate_progress(self, elapsed: int) -> None:
        step_ms = 30
        fraction = min(elapsed / self.duration_ms, 1.0)
        self.progress.configure(value=fraction * 100)
        if elapsed < self.duration_ms:
            self.after(step_ms, self._animate_progress, elapsed + step_ms)
        else:
            self.destroy()
            self.on_finished()


class Application:
    """Bootstraps directories, settings, splash screen, and the main window."""

    def __init__(self) -> None:
        ensure_directories()
        self.settings = Settings.load()

        self.root = ttk.Window(
            title=self.settings.get("app", "name", "Internet Speed Tester Pro"),
            themename="darkly",
            size=self.settings.window_size,
            minsize=(
                self.settings.get("window", "min_width", 1024),
                self.settings.get("window", "min_height", 700),
            ),
        )
        self.root.withdraw()  # Hide main window until splash finishes

        splash_duration_ms = self.settings.splash_duration * 1000
        SplashScreen(self.root, splash_duration_ms, self._launch_main_window)

    def _launch_main_window(self) -> None:
        self.root.deiconify()
        try:
            MainWindow(self.root, self.settings)
        except Exception:
            logger.exception("Failed to initialize main window")
            raise

    def run(self) -> None:
        """Start the Tkinter event loop."""
        self.root.mainloop()


def main() -> int:
    """Application entry point."""
    try:
        app = Application()
        app.run()
        return 0
    except Exception as exc:  # noqa: BLE001 - top-level safety net
        logger.exception("Fatal error during application startup")
        print(f"Fatal error: {exc}", file=sys.stderr)
        return 1


if __name__ == "__main__":
    sys.exit(main())
