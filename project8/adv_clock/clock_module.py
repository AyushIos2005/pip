from __future__ import annotations
import time
import tkinter as tk
from tkinter import ttk
from datetime import datetime
from typing import Dict

try:
    from zoneinfo import ZoneInfo  # Python 3.9+
except ImportError:  # pragma: no cover
    ZoneInfo = None  # type: ignore


# ------------------------------------------------------------------
class ClockFrame(ttk.Frame):
    """Live digital clock with date, and 12h/24h toggle support."""

    def __init__(self, parent: tk.Widget, settings: dict, **kwargs) -> None:
        super().__init__(parent, style="TFrame", **kwargs)
        self.settings = settings
        self._blink_on = True
        self._after_id: str | None = None

        self.columnconfigure(0, weight=1)

        ttk.Label(self, text="Digital Clock", style="Title.TLabel").grid(
            row=0, column=0, pady=(10, 20), sticky="n"
        )

        self.time_label = ttk.Label(self, text="--:--:--", style="Clock.TLabel")
        self.time_label.grid(row=1, column=0, pady=10)

        self.date_label = ttk.Label(self, text="", style="SubClock.TLabel")
        self.date_label.grid(row=2, column=0, pady=(0, 20))

        # Format toggle
        toggle_frame = ttk.Frame(self, style="TFrame")
        toggle_frame.grid(row=3, column=0, pady=10)

        self.format_var = tk.StringVar(
            value=self.settings.get("time_format", "12")
        )
        ttk.Radiobutton(
            toggle_frame,
            text="12-Hour",
            variable=self.format_var,
            value="12",
            command=self._on_format_change,
        ).grid(row=0, column=0, padx=10)
        ttk.Radiobutton(
            toggle_frame,
            text="24-Hour",
            variable=self.format_var,
            value="24",
            command=self._on_format_change,
        ).grid(row=0, column=1, padx=10)

        self._tick()

    # ------------------------------------------------------------
    def _on_format_change(self) -> None:
        self.settings["time_format"] = self.format_var.get()

    # ------------------------------------------------------------
    def _tick(self) -> None:
        """Update the clock every 500ms (twice per second) for a smooth
        blinking colon effect without freezing the GUI."""
        try:
            now = datetime.now()
            colon = ":" if self._blink_on else " "
            self._blink_on = not self._blink_on

            if self.format_var.get() == "24":
                time_str = now.strftime(f"%H{colon}%M{colon}%S")
            else:
                time_str = now.strftime(f"%I{colon}%M{colon}%S %p")

            self.time_label.config(text=time_str)
            self.date_label.config(
                text=now.strftime("%A\n%d %B %Y")
            )
        except Exception as exc:  # pragma: no cover - defensive
            self.time_label.config(text="Error")
            print(f"[ClockFrame] tick error: {exc}")
        finally:
            self._after_id = self.after(500, self._tick)

    # ------------------------------------------------------------
    def destroy(self) -> None:
        if self._after_id is not None:
            try:
                self.after_cancel(self._after_id)
            except Exception:
                pass
        super().destroy()


# ------------------------------------------------------------------
WORLD_CITIES: Dict[str, str] = {
    "Kolkata": "Asia/Kolkata",
    "London": "Europe/London",
    "New York": "America/New_York",
    "Dubai": "Asia/Dubai",
    "Tokyo": "Asia/Tokyo",
    "Sydney": "Australia/Sydney",
}


class WorldClockFrame(ttk.Frame):
    """Displays simultaneous live clocks for several world cities."""

    def __init__(self, parent: tk.Widget, **kwargs) -> None:
        super().__init__(parent, style="TFrame", **kwargs)
        self._after_id: str | None = None
        self._city_labels: Dict[str, ttk.Label] = {}

        ttk.Label(self, text="World Clock", style="Title.TLabel").grid(
            row=0, column=0, columnspan=2, pady=(10, 20)
        )

        grid = ttk.Frame(self, style="TFrame")
        grid.grid(row=1, column=0, columnspan=2)

        for i, city in enumerate(WORLD_CITIES):
            card = ttk.Frame(grid, style="Card.TFrame", padding=16)
            card.grid(row=i // 2, column=i % 2, padx=12, pady=12, sticky="nsew")

            ttk.Label(card, text=city, style="Card.TLabel",
                      font=("Segoe UI", 12, "bold")).pack(anchor="w")
            time_lbl = ttk.Label(card, text="--:--:--", style="Card.TLabel",
                                  font=("Consolas", 20, "bold"))
            time_lbl.pack(anchor="w", pady=(4, 0))
            self._city_labels[city] = time_lbl

        self._tick()

    # ------------------------------------------------------------
    def _tick(self) -> None:
        try:
            for city, tz_name in WORLD_CITIES.items():
                label = self._city_labels.get(city)
                if label is None:
                    continue
                if ZoneInfo is not None:
                    try:
                        now = datetime.now(ZoneInfo(tz_name))
                        label.config(text=now.strftime("%I:%M:%S %p"))
                    except Exception as exc:
                        label.config(text="N/A")
                        print(f"[WorldClockFrame] zone error for {city}: {exc}")
                else:
                    label.config(text="zoneinfo unavailable")
        except Exception as exc:  # pragma: no cover - defensive
            print(f"[WorldClockFrame] tick error: {exc}")
        finally:
            self._after_id = self.after(1000, self._tick)

    # ------------------------------------------------------------
    def destroy(self) -> None:
        if self._after_id is not None:
            try:
                self.after_cancel(self._after_id)
            except Exception:
                pass
        super().destroy()
