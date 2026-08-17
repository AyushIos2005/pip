from __future__ import annotations
import time
import tkinter as tk
from tkinter import ttk


class Stopwatch(ttk.Frame):
    """A stopwatch widget with lap tracking, driven by `after()` so the
    GUI thread is never blocked."""

    def __init__(self, parent: tk.Widget, **kwargs) -> None:
        super().__init__(parent, style="TFrame", **kwargs)

        self._running = False
        self._start_time = 0.0
        self._elapsed = 0.0
        self._after_id: str | None = None
        self._lap_count = 0

        self.columnconfigure(0, weight=1)

        ttk.Label(self, text="Stopwatch", style="Title.TLabel").grid(
            row=0, column=0, pady=(10, 20)
        )

        self.display = ttk.Label(self, text="00:00:00.000", style="Clock.TLabel")
        self.display.grid(row=1, column=0, pady=10)

        btn_frame = ttk.Frame(self, style="TFrame")
        btn_frame.grid(row=2, column=0, pady=20)

        self.start_btn = ttk.Button(btn_frame, text="Start", command=self.start)
        self.start_btn.grid(row=0, column=0, padx=6)

        self.pause_btn = ttk.Button(
            btn_frame, text="Pause", command=self.pause, state="disabled"
        )
        self.pause_btn.grid(row=0, column=1, padx=6)

        self.lap_btn = ttk.Button(
            btn_frame, text="Lap", command=self.lap, state="disabled"
        )
        self.lap_btn.grid(row=0, column=2, padx=6)

        self.reset_btn = ttk.Button(
            btn_frame, text="Reset", style="Danger.TButton", command=self.reset
        )
        self.reset_btn.grid(row=0, column=3, padx=6)

        # Lap list
        lap_frame = ttk.Frame(self, style="TFrame")
        lap_frame.grid(row=3, column=0, pady=(10, 0), sticky="nsew")
        self.rowconfigure(3, weight=1)

        self.lap_list = tk.Listbox(
            lap_frame, height=8, width=30, activestyle="none",
            borderwidth=0, highlightthickness=0
        )
        self.lap_list.pack(fill="both", expand=True)

    # ------------------------------------------------------------
    def _format(self, total_seconds: float) -> str:
        """Format seconds into HH:MM:SS.mmm."""
        millis = int((total_seconds - int(total_seconds)) * 1000)
        hours, rem = divmod(int(total_seconds), 3600)
        minutes, seconds = divmod(rem, 60)
        return f"{hours:02}:{minutes:02}:{seconds:02}.{millis:03}"

    # ------------------------------------------------------------
    def start(self) -> None:
        """Start or resume the stopwatch."""
        if self._running:
            return
        self._running = True
        self._start_time = time.perf_counter() - self._elapsed
        self.start_btn.config(text="Resume", state="disabled")
        self.pause_btn.config(state="normal")
        self.lap_btn.config(state="normal")
        self._update()

    # ------------------------------------------------------------
    def pause(self) -> None:
        """Pause the stopwatch, preserving elapsed time."""
        if not self._running:
            return
        self._running = False
        self._elapsed = time.perf_counter() - self._start_time
        self.start_btn.config(state="normal")
        self.pause_btn.config(state="disabled")
        self.lap_btn.config(state="disabled")
        if self._after_id is not None:
            self.after_cancel(self._after_id)
            self._after_id = None

    # ------------------------------------------------------------
    def reset(self) -> None:
        """Reset the stopwatch to zero and clear laps."""
        self._running = False
        self._elapsed = 0.0
        self._lap_count = 0
        if self._after_id is not None:
            self.after_cancel(self._after_id)
            self._after_id = None
        self.display.config(text="00:00:00.000")
        self.lap_list.delete(0, tk.END)
        self.start_btn.config(text="Start", state="normal")
        self.pause_btn.config(state="disabled")
        self.lap_btn.config(state="disabled")

    # ------------------------------------------------------------
    def lap(self) -> None:
        """Record the current elapsed time as a lap."""
        if not self._running:
            return
        self._lap_count += 1
        elapsed = time.perf_counter() - self._start_time
        self.lap_list.insert(
            0, f"Lap {self._lap_count}: {self._format(elapsed)}"
        )

    # ------------------------------------------------------------
    def _update(self) -> None:
        if not self._running:
            return
        try:
            elapsed = time.perf_counter() - self._start_time
            self.display.config(text=self._format(elapsed))
        except Exception as exc:  # pragma: no cover - defensive
            print(f"[Stopwatch] update error: {exc}")
        finally:
            self._after_id = self.after(31, self._update)  # ~32fps refresh

    # ------------------------------------------------------------
    def destroy(self) -> None:
        if self._after_id is not None:
            try:
                self.after_cancel(self._after_id)
            except Exception:
                pass
        super().destroy()
