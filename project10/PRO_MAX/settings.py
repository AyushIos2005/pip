"""
settings.py
-----------
Loads, validates, and persists application configuration from
settings.json into a typed Settings object. Every module that needs
configuration (themes, notifications, history, reports, dashboard)
reads from a single Settings instance rather than parsing JSON itself.
"""

from __future__ import annotations

import json
import os
from dataclasses import dataclass, field
from typing import Any, Dict

from utils import APP_ROOT, get_logger

logger = get_logger(__name__)

SETTINGS_PATH = os.path.join(APP_ROOT, "settings.json")

DEFAULT_SETTINGS: Dict[str, Any] = {
    "app": {
        "name": "Internet Speed Tester",
        "version": "2.0.0",
        "developer": "CODEHUB_TEAM@VGI",
        "license": "MIT",
    },
    "theme": {"mode": "dark", "accent": "blue", "available_themes": ["dark", "light", "blue", "green", "purple"]},
    "units": {"speed_unit": "Mbps", "available_units": ["Mbps", "MBps", "Kbps"]},
    "notifications": {
        "enabled": True,
        "notify_on_test_complete": True,
        "notify_on_disconnect": True,
        "notify_on_export": True,
        "notify_on_report_saved": True,
    },
    "auto_save": {"enabled": True, "save_to_history": True},
    "auto_export": {"enabled": False, "format": "csv", "export_path": "reports/"},
    "animation": {"speed": "normal", "available_speeds": ["slow", "normal", "fast"], "gauge_smoothness_ms": 16},
    "language": {"current": "en", "available_languages": ["en"]},
    "network": {"monitor_interval_seconds": 5, "auto_detect_disconnect": True},
    "history": {"file_path": "history/history.csv", "max_records": 1000},
    "reports": {"output_path": "reports/", "include_logo": True, "include_graphs": True},
    "window": {"width": 1280, "height": 800, "min_width": 1024, "min_height": 700, "start_maximized": False},
    "splash": {"duration_seconds": 3},
}


@dataclass
class Settings:
    """In-memory representation of application settings."""

    data: Dict[str, Any] = field(default_factory=lambda: json.loads(json.dumps(DEFAULT_SETTINGS)))

    # ------------------------------------------------------------------
    # Loading / saving
    # ------------------------------------------------------------------
    @classmethod
    def load(cls, path: str = SETTINGS_PATH) -> "Settings":
        """Load settings from disk, creating defaults if the file is missing."""
        if not os.path.exists(path):
            logger.info("settings.json not found - creating defaults at %s", path)
            settings = cls()
            settings.save(path)
            return settings

        try:
            with open(path, "r", encoding="utf-8") as f:
                data = json.load(f)
            merged = cls._merge_defaults(data)
            return cls(data=merged)
        except (json.JSONDecodeError, OSError) as exc:
            logger.error("Failed to load settings.json (%s) - falling back to defaults", exc)
            return cls()

    def save(self, path: str = SETTINGS_PATH) -> None:
        """Persist the current settings state back to disk."""
        try:
            with open(path, "w", encoding="utf-8") as f:
                json.dump(self.data, f, indent=2)
            logger.info("Settings saved to %s", path)
        except OSError as exc:
            logger.error("Failed to save settings.json: %s", exc)

    @staticmethod
    def _merge_defaults(data: Dict[str, Any]) -> Dict[str, Any]:
        """Fill in any missing keys from DEFAULT_SETTINGS (forward compatibility)."""
        merged = json.loads(json.dumps(DEFAULT_SETTINGS))
        for section, values in data.items():
            if section in merged and isinstance(values, dict):
                merged[section].update(values)
            else:
                merged[section] = values
        return merged

    # ------------------------------------------------------------------
    # Convenience accessors
    # ------------------------------------------------------------------
    def get(self, section: str, key: str, default: Any = None) -> Any:
        """Safely retrieve a nested settings value."""
        return self.data.get(section, {}).get(key, default)

    def set(self, section: str, key: str, value: Any) -> None:
        """Update a nested settings value in memory (call save() to persist)."""
        self.data.setdefault(section, {})[key] = value

    @property
    def theme_mode(self) -> str:
        return self.get("theme", "mode", "dark")

    @property
    def speed_unit(self) -> str:
        return self.get("units", "speed_unit", "Mbps")

    @property
    def notifications_enabled(self) -> bool:
        return bool(self.get("notifications", "enabled", True))

    @property
    def history_file_path(self) -> str:
        relative = self.get("history", "file_path", "history/history.csv")
        return os.path.join(APP_ROOT, relative) if not os.path.isabs(relative) else relative

    @property
    def reports_output_path(self) -> str:
        relative = self.get("reports", "output_path", "reports/")
        return os.path.join(APP_ROOT, relative) if not os.path.isabs(relative) else relative

    @property
    def window_size(self) -> tuple[int, int]:
        return (self.get("window", "width", 1280), self.get("window", "height", 800))

    @property
    def splash_duration(self) -> int:
        return int(self.get("splash", "duration_seconds", 3))
