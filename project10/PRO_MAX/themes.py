"""
themes.py
---------
Centralized color palette, font definitions, and theme management for
Internet Speed Tester Pro. Provides a single ThemeManager class that
translates a logical theme name (dark / light / blue / green / purple)
into a ttkbootstrap style name and a dictionary of raw hex colors that
custom-drawn widgets (gauge, cards, graph) can use directly.

No global mutable state is used - ThemeManager instances hold their
own current theme and notify subscribers via a simple callback list.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import Callable, Dict, List


@dataclass(frozen=True)
class Palette:
    """Immutable color palette for a single theme variant."""

    name: str
    bootstyle: str          # ttkbootstrap theme name to apply
    bg_primary: str
    bg_secondary: str
    bg_card: str
    accent: str
    accent_hover: str
    success: str
    danger: str
    warning: str
    text_primary: str
    text_secondary: str
    border: str


# ---------------------------------------------------------------------------
# Base brand colors (from the design spec)
# ---------------------------------------------------------------------------
DARK_BG = "#0F172A"
ACCENT_BLUE = "#2563EB"
ACCENT_GREEN = "#10B981"
ACCENT_RED = "#EF4444"
TEXT_WHITE = "#F8FAFC"


PALETTES: Dict[str, Palette] = {
    "dark": Palette(
        name="dark",
        bootstyle="darkly",
        bg_primary=DARK_BG,
        bg_secondary="#1E293B",
        bg_card="#1E293B",
        accent=ACCENT_BLUE,
        accent_hover="#1D4ED8",
        success=ACCENT_GREEN,
        danger=ACCENT_RED,
        warning="#F59E0B",
        text_primary=TEXT_WHITE,
        text_secondary="#94A3B8",
        border="#334155",
    ),
    "light": Palette(
        name="light",
        bootstyle="flatly",
        bg_primary="#F8FAFC",
        bg_secondary="#FFFFFF",
        bg_card="#FFFFFF",
        accent=ACCENT_BLUE,
        accent_hover="#1D4ED8",
        success=ACCENT_GREEN,
        danger=ACCENT_RED,
        warning="#F59E0B",
        text_primary="#0F172A",
        text_secondary="#475569",
        border="#E2E8F0",
    ),
    "blue": Palette(
        name="blue",
        bootstyle="darkly",
        bg_primary="#0B1220",
        bg_secondary="#111C33",
        bg_card="#132140",
        accent=ACCENT_BLUE,
        accent_hover="#3B82F6",
        success=ACCENT_GREEN,
        danger=ACCENT_RED,
        warning="#F59E0B",
        text_primary=TEXT_WHITE,
        text_secondary="#93A5C7",
        border="#1E3A63",
    ),
    "green": Palette(
        name="green",
        bootstyle="darkly",
        bg_primary="#0B1A15",
        bg_secondary="#0F2A22",
        bg_card="#123529",
        accent=ACCENT_GREEN,
        accent_hover="#059669",
        success=ACCENT_GREEN,
        danger=ACCENT_RED,
        warning="#F59E0B",
        text_primary=TEXT_WHITE,
        text_secondary="#8FBDA9",
        border="#1E4A38",
    ),
    "purple": Palette(
        name="purple",
        bootstyle="darkly",
        bg_primary="#150F27",
        bg_secondary="#20163B",
        bg_card="#271C47",
        accent="#8B5CF6",
        accent_hover="#7C3AED",
        success=ACCENT_GREEN,
        danger=ACCENT_RED,
        warning="#F59E0B",
        text_primary=TEXT_WHITE,
        text_secondary="#B7A9DE",
        border="#3B2D63",
    ),
}


FONT_FAMILY_HEADING = "Segoe UI Semibold"
FONT_FAMILY_BODY = "Segoe UI"
FONT_FAMILY_MONO = "Consolas"

FONTS = {
    "splash_title": (FONT_FAMILY_HEADING, 28, "bold"),
    "splash_subtitle": (FONT_FAMILY_BODY, 12),
    "app_title": (FONT_FAMILY_HEADING, 16, "bold"),
    "card_value": (FONT_FAMILY_HEADING, 26, "bold"),
    "card_label": (FONT_FAMILY_BODY, 11),
    "section_title": (FONT_FAMILY_HEADING, 14, "bold"),
    "body": (FONT_FAMILY_BODY, 10),
    "small": (FONT_FAMILY_BODY, 9),
    "mono": (FONT_FAMILY_MONO, 10),
    "gauge_value": (FONT_FAMILY_HEADING, 22, "bold"),
}


class ThemeManager:
    """
    Manages the active application theme and notifies registered
    listeners whenever the theme changes, so open widgets can restyle
    themselves without a full application restart.
    """

    def __init__(self, initial_theme: str = "dark") -> None:
        self._current_theme: str = initial_theme if initial_theme in PALETTES else "dark"
        self._listeners: List[Callable[[Palette], None]] = []

    @property
    def palette(self) -> Palette:
        """Return the currently active color palette."""
        return PALETTES[self._current_theme]

    @property
    def theme_name(self) -> str:
        """Return the current theme's logical name."""
        return self._current_theme

    def available_themes(self) -> List[str]:
        """Return all available theme names."""
        return list(PALETTES.keys())

    def set_theme(self, theme_name: str) -> None:
        """Switch to a new theme and notify all listeners."""
        if theme_name not in PALETTES:
            raise ValueError(f"Unknown theme: {theme_name}")
        self._current_theme = theme_name
        for listener in self._listeners:
            listener(self.palette)

    def subscribe(self, callback: Callable[[Palette], None]) -> None:
        """Register a callback invoked with the new palette on theme change."""
        self._listeners.append(callback)

    def unsubscribe(self, callback: Callable[[Palette], None]) -> None:
        """Remove a previously registered callback."""
        if callback in self._listeners:
            self._listeners.remove(callback)
