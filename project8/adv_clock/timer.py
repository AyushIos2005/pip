from __future__ import annotations
import tkinter as tk
from tkinter import ttk, messagebox

import notifications


class Timer(ttk.Frame):
    """A countdown timer widget with pause/resume/reset support."""

    def __init__(self, parent: tk.Widget, settings: dict, **kwargs) -> None:
        super().__init__(parent, style="TFrame", **kwargs)
        self.settings = settings

        self._remaining = 0  # seconds left
        self._running = False
        self._after_id: str | None = None

        self.columnconfigure(0, weight=1)

        ttk.Label(self, text="Timer", style="Title.TLabel").grid(
            row=0, column=0, pady=(10, 20)
        )

        self.display = ttk.Label(self, text="00:00:00", style="Clock.TLabel")
        self.display.grid(row=1, column=0, pady=10)

        # Input fields
        input_frame = ttk.Frame(self, style="TFrame")
        input_frame.grid(row=2, column=0, pady=10)

        self.hours_var = tk.StringVar(value="0")
        self.minutes_var = tk.StringVar(value="1")
        self.seconds_var = tk.StringVar(value="0")

        self._make_spin(input_frame, "Hours", self.hours_var, 0, 23, 0)
        self._make_spin(input_frame, "Minutes", self.minutes_var, 0, 59, 1)
        self._make_spin(input_frame, "Seconds", self.seconds_var, 0, 59, 2)

        # Buttons
        btn_frame = ttk.Frame(self, style="TFrame")
        btn_frame.grid(row=3, column=0, pady=20)

        self.start_btn = ttk.Button(btn_frame, text="Start", command=self.start)
        self.start_btn.grid(row=0, column=0, padx=6)

        self.pause_btn = ttk.Button(
            btn_frame, text="Pause", command=self.pause, state="disabled"
        )
        self.pause_btn.grid(row=0, column=1, padx=6)

        self.reset_btn = ttk.Button(
            btn_frame, text="Reset", style="Danger.TButton", command=self.reset
        )
        self.reset_btn.grid(row=0, column=2, padx=6)

    # ------------------------------------------------------------
    def _make_spin(
        self, parent: tk.Widget, label: str, var: tk.StringVar,
        lo: int, hi: int, col: int
    ) -> None:
        frame = ttk.Frame(parent, style="TFrame")
        frame.grid(row=0, column=col, padx=10)
        ttk.Label(frame, text=label).pack()
        ttk.Spinbox(
            frame, from_=lo, to=hi, textvariable=var, width=5, wrap=True
        ).pack()

    # ------------------------------------------------------------
    def _format(self, total_seconds: int) -> str:
        hours, rem = divmod(max(total_seconds, 0), 3600)
        minutes, seconds = divmod(rem, 60)
        return f"{hours:02}:{minutes:02}:{seconds:02}"

    # ------------------------------------------------------------
    def start(self) -> None:
        """Start (or resume) the countdown, validating input first."""
        if self._running:
            return

        if self._remaining <= 0:
            try:
                h = int(self.hours_var.get() or 0)
                m = int(self.minutes_var.get() or 0)
                s = int(self.seconds_var.get() or 0)
                if h < 0 or m < 0 or s < 0:
                    raise ValueError("Negative values are not allowed.")
                total = h * 3600 + m * 60 + s
                if total <= 0:
                    raise ValueError("Please enter a duration greater than zero.")
                self._remaining = total
            except ValueError as exc:
                messagebox.showerror("Invalid Timer Input", str(exc) or "Please enter valid numeric values.")
                return

        self._running = True
        self.start_btn.config(state="disabled")
        self.pause_btn.config(state="normal")
        self._tick()

    # ------------------------------------------------------------
    def pause(self) -> None:
        """Pause the countdown, preserving remaining time."""
        self._running = False
        self.start_btn.config(state="normal", text="Resume")
        self.pause_btn.config(state="disabled")
        if self._after_id is not None:
            self.after_cancel(self._after_id)
            self._after_id = None

    # ------------------------------------------------------------
    def reset(self) -> None:
        """Reset the timer back to zero/idle state."""
        self._running = False
        self._remaining = 0
        if self._after_id is not None:
            self.after_cancel(self._after_id)
            self._after_id = None
        self.display.config(text="00:00:00")
        self.start_btn.config(state="normal", text="Start")
        self.pause_btn.config(state="disabled")

    # ------------------------------------------------------------
    def _tick(self) -> None:
        if not self._running:
            return
        try:
            self.display.config(text=self._format(self._remaining))
            if self._remaining <= 0:
                self._finish()
                return
            self._remaining -= 1
        except Exception as exc:  # pragma: no cover - defensive
            print(f"[Timer] tick error: {exc}")
        finally:
            if self._running and self._remaining >= 0:
                self._after_id = self.after(1000, self._tick)

    # ------------------------------------------------------------
    def _finish(self) -> None:
        """Handle timer completion: sound, notification, popup."""
        self._running = False
        self.display.config(text="00:00:00")
        self.start_btn.config(state="normal", text="Start")
        self.pause_btn.config(state="disabled")

        if self.settings.get("notifications", True):
            notifications.notify("Smart Time Suite", "Timer finished!")
            notifications.play_sound(root=self.winfo_toplevel())

        messagebox.showinfo("Timer Finished", "Your countdown timer has completed!")

    # ------------------------------------------------------------
    def destroy(self) -> None:
        if self._after_id is not None:
            try:
                self.after_cancel(self._after_id)
            except Exception:
                pass
        super().destroy()
