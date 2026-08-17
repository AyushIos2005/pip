"""
notifications.py
-----------------
Wraps the `plyer` cross-platform notification API behind a single
NotificationManager class so the rest of the app never talks to
plyer directly. This keeps notification logic testable and makes it
easy to disable notifications globally from Settings.
"""

from __future__ import annotations

from typing import Optional

from plyer import notification

from utils import get_logger

logger = get_logger(__name__)


class NotificationManager:
    """Sends desktop notifications for key application events."""

    APP_NAME = "Internet Speed Tester Pro"

    def __init__(self, enabled: bool = True) -> None:
        self.enabled: bool = enabled

    def set_enabled(self, enabled: bool) -> None:
        """Enable or disable all notifications at runtime."""
        self.enabled = enabled

    def _send(self, title: str, message: str, timeout: int = 5) -> None:
        """Internal helper that performs the actual notification call."""
        if not self.enabled:
            return
        try:
            notification.notify(
                title=title,
                message=message,
                app_name=self.APP_NAME,
                timeout=timeout,
            )
        except Exception as exc:  # noqa: BLE001 - notifications must never crash the app
            logger.warning("Failed to send desktop notification: %s", exc)

    def notify_test_complete(self, download: float, upload: float, unit: str = "Mbps") -> None:
        """Notify the user that a speed test has finished."""
        self._send(
            "Speed Test Completed",
            f"Download: {download:.2f} {unit} | Upload: {upload:.2f} {unit}",
        )

    def notify_disconnected(self) -> None:
        """Notify the user that internet connectivity was lost."""
        self._send("Connection Lost", "Your internet connection appears to be down.")

    def notify_reconnected(self) -> None:
        """Notify the user that internet connectivity was restored."""
        self._send("Connection Restored", "Your internet connection is back online.")

    def notify_history_exported(self, path: str) -> None:
        """Notify the user that history was exported successfully."""
        self._send("History Exported", f"Saved to: {path}")

    def notify_report_saved(self, path: Optional[str]) -> None:
        """Notify the user that a report file was generated."""
        self._send("Report Saved", f"Saved to: {path}" if path else "Report generated.")
