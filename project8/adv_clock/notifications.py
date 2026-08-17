from __future__ import annotations
import os
import threading
import tkinter as tk
from typing import Optional

APP_NAME = "Smart Time Suite"
ASSETS_DIR = os.path.join(os.path.dirname(os.path.abspath(__file__)), "assets")
DEFAULT_SOUND_PATH = os.path.join(ASSETS_DIR, "alarm.wav")


def notify(title: str, message: str, timeout: int = 8) -> None:
    """
    Show a desktop notification. Falls back silently (with a console
    message) if `plyer` is not installed or the platform backend
    fails, so the app never crashes because of a missing notifier.
    """
    try:
        from plyer import notification  # type: ignore

        notification.notify(
            title=title,
            message=message,
            app_name=APP_NAME,
            timeout=timeout,
        )
    except ModuleNotFoundError:
        print(f"[Notification - plyer missing] {title}: {message}")
    except Exception as exc:  # pragma: no cover - platform dependent
        print(f"[Notification failed] {title}: {message} ({exc})")


def play_sound(sound_path: Optional[str] = None, root: Optional[tk.Tk] = None) -> None:
    """
    Play the alarm/timer sound in a background thread so the GUI never
    freezes. Tries `playsound` first; falls back to the terminal bell
    or a Tkinter bell if the file or library is unavailable.
    """
    path = sound_path or DEFAULT_SOUND_PATH

    def _play() -> None:
        if os.path.isfile(path):
            try:
                from playsound import playsound  # type: ignore

                playsound(path)
                return
            except ModuleNotFoundError:
                print("[Sound] 'playsound' not installed - falling back to system bell.")
            except Exception as exc:  # pragma: no cover - platform dependent
                print(f"[Sound] Failed to play '{path}': {exc}")
        else:
            print(f"[Sound] File not found: {path} - falling back to system bell.")

        # Fallback: use the Tk bell (thread-safe to schedule via after)
        if root is not None:
            try:
                root.after(0, root.bell)
            except Exception:
                pass

    threading.Thread(target=_play, daemon=True).start()
