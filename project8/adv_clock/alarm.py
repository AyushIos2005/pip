from __future__ import annotations
import json
import os
import uuid
from dataclasses import dataclass, asdict, field
from datetime import datetime, timedelta
from typing import List, Optional

import tkinter as tk
from tkinter import ttk, messagebox

import notifications

ALARMS_FILE = os.path.join(os.path.dirname(os.path.abspath(__file__)), "alarms.json")


# ------------------------------------------------------------------
@dataclass
class Alarm:
    """A single alarm entry."""
    id: str
    time: str  # "HH:MM" 24-hour format
    message: str = "Alarm"
    repeat_daily: bool = True
    enabled: bool = True
    last_triggered_date: Optional[str] = None  # "YYYY-MM-DD", to avoid re-firing


# ------------------------------------------------------------------
class AlarmManager:
    """Handles loading, saving, and CRUD operations for alarms in JSON."""

    def __init__(self, filepath: str = ALARMS_FILE) -> None:
        self.filepath = filepath
        self.alarms: List[Alarm] = []
        self.load()

    # ------------------------------------------------------------
    def load(self) -> None:
        """Load alarms from disk, tolerating a missing or corrupted file."""
        if not os.path.isfile(self.filepath):
            self.alarms = []
            return
        try:
            with open(self.filepath, "r", encoding="utf-8") as f:
                data = json.load(f)
            self.alarms = [Alarm(**item) for item in data]
        except (json.JSONDecodeError, TypeError, ValueError) as exc:
            print(f"[AlarmManager] Corrupted alarms.json, starting fresh: {exc}")
            self.alarms = []
        except OSError as exc:
            print(f"[AlarmManager] Could not read alarms.json: {exc}")
            self.alarms = []

    # ------------------------------------------------------------
    def save(self) -> None:
        """Persist alarms to disk."""
        try:
            with open(self.filepath, "w", encoding="utf-8") as f:
                json.dump([asdict(a) for a in self.alarms], f, indent=4)
        except OSError as exc:
            print(f"[AlarmManager] Could not save alarms.json: {exc}")

    # ------------------------------------------------------------
    def add(self, time_str: str, message: str, repeat_daily: bool) -> Alarm:
        alarm = Alarm(id=str(uuid.uuid4()), time=time_str, message=message,
                       repeat_daily=repeat_daily)
        self.alarms.append(alarm)
        self.save()
        return alarm

    # ------------------------------------------------------------
    def update(self, alarm_id: str, **fields) -> None:
        for a in self.alarms:
            if a.id == alarm_id:
                for k, v in fields.items():
                    setattr(a, k, v)
                self.save()
                return

    # ------------------------------------------------------------
    def delete(self, alarm_id: str) -> None:
        self.alarms = [a for a in self.alarms if a.id != alarm_id]
        self.save()


# ------------------------------------------------------------------
class AlarmFrame(ttk.Frame):
    """UI for managing alarms and the background check loop that fires them."""

    def __init__(self, parent: tk.Widget, settings: dict, **kwargs) -> None:
        super().__init__(parent, style="TFrame", **kwargs)
        self.settings = settings
        self.manager = AlarmManager()
        self._after_id: str | None = None
        self._popup_open_ids: set[str] = set()

        self.columnconfigure(0, weight=1)
        self.rowconfigure(2, weight=1)

        ttk.Label(self, text="Alarms", style="Title.TLabel").grid(
            row=0, column=0, pady=(10, 10), sticky="w", padx=10
        )

        # --- New alarm entry form -----------------------------------
        form = ttk.Frame(self, style="TFrame")
        form.grid(row=1, column=0, sticky="ew", padx=10, pady=(0, 10))

        ttk.Label(form, text="Time (HH:MM, 24h):").grid(row=0, column=0, padx=4)
        self.time_entry = ttk.Entry(form, width=8)
        self.time_entry.insert(0, "07:00")
        self.time_entry.grid(row=0, column=1, padx=4)

        ttk.Label(form, text="Message:").grid(row=0, column=2, padx=4)
        self.message_entry = ttk.Entry(form, width=20)
        self.message_entry.insert(0, "Wake up!")
        self.message_entry.grid(row=0, column=3, padx=4)

        self.repeat_var = tk.BooleanVar(value=True)
        ttk.Checkbutton(
            form, text="Repeat Daily", variable=self.repeat_var
        ).grid(row=0, column=4, padx=8)

        ttk.Button(form, text="Add Alarm", command=self._add_alarm).grid(
            row=0, column=5, padx=8
        )

        # --- Alarm list ------------------------------------------------
        list_frame = ttk.Frame(self, style="TFrame")
        list_frame.grid(row=2, column=0, sticky="nsew", padx=10, pady=10)
        list_frame.columnconfigure(0, weight=1)
        list_frame.rowconfigure(0, weight=1)

        columns = ("time", "message", "repeat", "enabled")
        self.tree = ttk.Treeview(
            list_frame, columns=columns, show="headings", selectmode="browse"
        )
        for col, label, width in (
            ("time", "Time", 100),
            ("message", "Message", 220),
            ("repeat", "Repeat", 100),
            ("enabled", "Enabled", 100),
        ):
            self.tree.heading(col, text=label)
            self.tree.column(col, width=width, anchor="center")
        self.tree.grid(row=0, column=0, sticky="nsew")

        scrollbar = ttk.Scrollbar(list_frame, orient="vertical", command=self.tree.yview)
        self.tree.configure(yscrollcommand=scrollbar.set)
        scrollbar.grid(row=0, column=1, sticky="ns")

        # --- Action buttons ---------------------------------------------
        action_frame = ttk.Frame(self, style="TFrame")
        action_frame.grid(row=3, column=0, pady=(0, 10))

        ttk.Button(action_frame, text="Toggle Enable", command=self._toggle_selected).grid(
            row=0, column=0, padx=6
        )
        ttk.Button(action_frame, text="Edit", command=self._edit_selected).grid(
            row=0, column=1, padx=6
        )
        ttk.Button(
            action_frame, text="Delete", style="Danger.TButton", command=self._delete_selected
        ).grid(row=0, column=2, padx=6)

        self._refresh_list()
        self._check_loop()

    # ------------------------------------------------------------
    def _validate_time(self, time_str: str) -> bool:
        try:
            datetime.strptime(time_str, "%H:%M")
            return True
        except ValueError:
            return False

    # ------------------------------------------------------------
    def _add_alarm(self) -> None:
        time_str = self.time_entry.get().strip()
        message = self.message_entry.get().strip() or "Alarm"

        if not self._validate_time(time_str):
            messagebox.showerror(
                "Invalid Alarm Time", "Please enter a valid time in HH:MM (24-hour) format."
            )
            return

        self.manager.add(time_str, message, self.repeat_var.get())
        self._refresh_list()

    # ------------------------------------------------------------
    def _selected_alarm_id(self) -> Optional[str]:
        sel = self.tree.selection()
        if not sel:
            messagebox.showinfo("No Selection", "Please select an alarm first.")
            return None
        return sel[0]

    # ------------------------------------------------------------
    def _toggle_selected(self) -> None:
        alarm_id = self._selected_alarm_id()
        if not alarm_id:
            return
        for a in self.manager.alarms:
            if a.id == alarm_id:
                self.manager.update(alarm_id, enabled=not a.enabled)
                break
        self._refresh_list()

    # ------------------------------------------------------------
    def _edit_selected(self) -> None:
        alarm_id = self._selected_alarm_id()
        if not alarm_id:
            return
        alarm = next((a for a in self.manager.alarms if a.id == alarm_id), None)
        if not alarm:
            return

        editor = tk.Toplevel(self)
        editor.title("Edit Alarm")
        editor.transient(self.winfo_toplevel())
        editor.grab_set()

        ttk.Label(editor, text="Time (HH:MM):").grid(row=0, column=0, padx=8, pady=8)
        time_entry = ttk.Entry(editor)
        time_entry.insert(0, alarm.time)
        time_entry.grid(row=0, column=1, padx=8, pady=8)

        ttk.Label(editor, text="Message:").grid(row=1, column=0, padx=8, pady=8)
        msg_entry = ttk.Entry(editor)
        msg_entry.insert(0, alarm.message)
        msg_entry.grid(row=1, column=1, padx=8, pady=8)

        repeat_var = tk.BooleanVar(value=alarm.repeat_daily)
        ttk.Checkbutton(editor, text="Repeat Daily", variable=repeat_var).grid(
            row=2, column=0, columnspan=2, padx=8, pady=8
        )

        def save_changes() -> None:
            new_time = time_entry.get().strip()
            if not self._validate_time(new_time):
                messagebox.showerror("Invalid Alarm Time", "Please enter HH:MM (24-hour) format.")
                return
            self.manager.update(
                alarm.id,
                time=new_time,
                message=msg_entry.get().strip() or "Alarm",
                repeat_daily=repeat_var.get(),
            )
            self._refresh_list()
            editor.destroy()

        ttk.Button(editor, text="Save", command=save_changes).grid(
            row=3, column=0, columnspan=2, pady=10
        )

    # ------------------------------------------------------------
    def _delete_selected(self) -> None:
        alarm_id = self._selected_alarm_id()
        if not alarm_id:
            return
        if messagebox.askyesno("Delete Alarm", "Delete this alarm?"):
            self.manager.delete(alarm_id)
            self._refresh_list()

    # ------------------------------------------------------------
    def _refresh_list(self) -> None:
        self.tree.delete(*self.tree.get_children())
        for a in self.manager.alarms:
            self.tree.insert(
                "", "end", iid=a.id,
                values=(a.time, a.message, "Yes" if a.repeat_daily else "No",
                        "Yes" if a.enabled else "No"),
            )

    # ------------------------------------------------------------
    def _check_loop(self) -> None:
        """Check every second whether any enabled alarm should fire."""
        try:
            now = datetime.now()
            current_hm = now.strftime("%H:%M")
            today_str = now.strftime("%Y-%m-%d")

            for alarm in self.manager.alarms:
                if not alarm.enabled:
                    continue
                if alarm.time != current_hm:
                    continue
                if alarm.last_triggered_date == today_str:
                    continue
                if alarm.id in self._popup_open_ids:
                    continue
                self._fire_alarm(alarm, today_str)
        except Exception as exc:  # pragma: no cover - defensive
            print(f"[AlarmFrame] check loop error: {exc}")
        finally:
            self._after_id = self.after(1000, self._check_loop)

    # ------------------------------------------------------------
    def _fire_alarm(self, alarm: Alarm, today_str: str) -> None:
        """Trigger an alarm: sound + notification + snooze/dismiss popup."""
        self.manager.update(alarm.id, last_triggered_date=today_str)
        if not alarm.repeat_daily:
            self.manager.update(alarm.id, enabled=False)
        self._refresh_list()

        if self.settings.get("notifications", True):
            notifications.notify("Smart Time Suite - Alarm", alarm.message)
            notifications.play_sound(root=self.winfo_toplevel())

        self._popup_open_ids.add(alarm.id)
        self._show_alarm_popup(alarm)

    # ------------------------------------------------------------
    def _show_alarm_popup(self, alarm: Alarm) -> None:
        popup = tk.Toplevel(self)
        popup.title("Alarm")
        popup.attributes("-topmost", True)
        popup.transient(self.winfo_toplevel())

        ttk.Label(popup, text="⏰ " + alarm.message, font=("Segoe UI", 14, "bold")).pack(
            padx=20, pady=20
        )

        btn_frame = ttk.Frame(popup)
        btn_frame.pack(pady=(0, 15))

        def snooze() -> None:
            snooze_time = datetime.now() + timedelta(minutes=5)
            self.manager.update(
                alarm.id,
                time=snooze_time.strftime("%H:%M"),
                last_triggered_date=None,
                enabled=True,
            )
            self._popup_open_ids.discard(alarm.id)
            self._refresh_list()
            popup.destroy()

        def dismiss() -> None:
            self._popup_open_ids.discard(alarm.id)
            popup.destroy()

        ttk.Button(btn_frame, text="Snooze (5 min)", command=snooze).grid(
            row=0, column=0, padx=8
        )
        ttk.Button(
            btn_frame, text="Dismiss", style="Danger.TButton", command=dismiss
        ).grid(row=0, column=1, padx=8)

        popup.protocol("WM_DELETE_WINDOW", dismiss)

    # ------------------------------------------------------------
    def destroy(self) -> None:
        if self._after_id is not None:
            try:
                self.after_cancel(self._after_id)
            except Exception:
                pass
        super().destroy()
