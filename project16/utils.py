"""
utils.py
Shared constants, modern theming/design-system, and helper functions
used across the Restaurant POS application.

Design system additions (modern GUI pass):
  - Refreshed indigo/slate colour palette (light + dark)
  - RoundButton: real rounded-corner canvas button (solid / outline / ghost)
  - Pill: small rounded status badge
  - gradient_canvas: soft two-colour gradient background
  - entry_field: bordered input with an animated focus ring
  - segmented(): pill-style single-select control (replaces plain radios/combos)
  - setup_ttk_style(): flat modern styling for ttk widgets (Combobox,
    Notebook, Treeview, Scrollbar) so they match the custom palette
"""

import datetime
import hashlib
import os
import tkinter as tk
from tkinter import ttk

# --------------------------------------------------------------------------- #
# Restaurant Info (edit these to customise the receipt / dashboard branding)
# --------------------------------------------------------------------------- #
RESTAURANT_NAME = "Spice Route Kitchen"
RESTAURANT_ADDRESS = "12, MG Road, Kolkata, West Bengal - 700001"
RESTAURANT_GSTIN = "19ABCDE1234F1Z5"
RESTAURANT_PHONE = "+91 98765 43210"
UPI_ID = "8777059815@ptyes"

LOGO_PATH = os.path.join("assets", "logo", "logo.png")
RECEIPTS_DIR = "receipts"

# --------------------------------------------------------------------------- #
# Theme — modern indigo / slate palette
# --------------------------------------------------------------------------- #
LIGHT_THEME = {
    "bg": "#F1F5F9",          # slate-100 app background
    "bg_soft": "#E8EDF3",     # slightly deeper panel background
    "surface": "#FFFFFF",     # card / panel surface
    "surface_alt": "#F8FAFC", # subtle alt row / hover surface
    "primary": "#4F46E5",     # indigo-600
    "primary_dark": "#4338CA",# indigo-700
    "primary_soft": "#EEF2FF",# indigo-50 (chips / soft backgrounds)
    "accent": "#F59E0B",      # amber-500
    "accent_dark": "#D97706",
    "text": "#1E293B",        # slate-800
    "text_soft": "#334155",
    "muted": "#64748B",       # slate-500
    "success": "#10B981",     # emerald-500
    "success_dark": "#059669",
    "danger": "#EF4444",      # red-500
    "danger_dark": "#DC2626",
    "warning": "#F59E0B",
    "border": "#E2E8F0",      # slate-200
    "shadow": "#CBD5E1",
    "on_primary": "#FFFFFF",
}

DARK_THEME = {
    "bg": "#0F172A",          # slate-900
    "bg_soft": "#0B1220",
    "surface": "#1E293B",     # slate-800
    "surface_alt": "#243244",
    "primary": "#6366F1",     # indigo-500
    "primary_dark": "#4F46E5",
    "primary_soft": "#1E2340",
    "accent": "#FBBF24",
    "accent_dark": "#F59E0B",
    "text": "#F1F5F9",
    "text_soft": "#E2E8F0",
    "muted": "#94A3B8",
    "success": "#34D399",
    "success_dark": "#10B981",
    "danger": "#F87171",
    "danger_dark": "#EF4444",
    "warning": "#FBBF24",
    "border": "#334155",
    "shadow": "#020617",
    "on_primary": "#0F172A",
}

# Mutable, process wide theme state. Screens read from this dict at
# construction time; toggling the theme reopens the current screen so the
# new colours take effect (see dashboard.py -> toggle_theme).
STATE = {
    "mode": "light",  # "light" or "dark"
}


def theme():
    """Return the currently active colour palette."""
    return DARK_THEME if STATE["mode"] == "dark" else LIGHT_THEME


def toggle_theme():
    STATE["mode"] = "dark" if STATE["mode"] == "light" else "light"


FONT_FAMILY = "Segoe UI"
FONT_DISPLAY = (FONT_FAMILY, 24, "bold")
FONT_TITLE = (FONT_FAMILY, 19, "bold")
FONT_SUBTITLE = (FONT_FAMILY, 12, "bold")
FONT_NORMAL = (FONT_FAMILY, 11)
FONT_SMALL = (FONT_FAMILY, 9)
FONT_TINY = (FONT_FAMILY, 8)
FONT_BUTTON = (FONT_FAMILY, 10, "bold")
FONT_MONO = ("Consolas", 10)


# --------------------------------------------------------------------------- #
# Generic helpers
# --------------------------------------------------------------------------- #
def now():
    return datetime.datetime.now()


def format_currency(amount):
    try:
        return f"₹{float(amount):,.2f}"
    except (TypeError, ValueError):
        return "₹0.00"


def format_currency_pdf(amount):
    """ASCII-safe currency string for use inside ReportLab PDF canvases.

    ReportLab's standard PDF fonts (Helvetica, etc.) use WinAnsiEncoding,
    which has no glyph for the Indian Rupee sign (₹, U+20B9). Drawing it
    directly silently renders as a garbled character (e.g. 'n') instead
    of raising an error, so PDFs must use this "Rs." fallback instead of
    format_currency() wherever text is drawn with c.drawString / etc.
    """
    try:
        return f"Rs. {float(amount):,.2f}"
    except (TypeError, ValueError):
        return "Rs. 0.00"


def format_date(dt=None):
    dt = dt or now()
    return dt.strftime("%d-%b-%Y")


def format_time(dt=None):
    dt = dt or now()
    return dt.strftime("%I:%M:%S %p")


def format_datetime(dt=None):
    dt = dt or now()
    return dt.strftime("%d-%b-%Y %I:%M %p")


def hash_password(password: str, salt: str = None) -> str:
    """Return 'salt$hash' using PBKDF2-HMAC-SHA256."""
    salt = salt or os.urandom(16).hex()
    digest = hashlib.pbkdf2_hmac("sha256", password.encode(), bytes.fromhex(salt), 100_000)
    return f"{salt}${digest.hex()}"


def verify_password(password: str, stored: str) -> bool:
    try:
        salt, _ = stored.split("$")
    except ValueError:
        return False
    return hash_password(password, salt) == stored


def ensure_dirs():
    for d in ("assets/images", "assets/icons", "assets/logo", RECEIPTS_DIR, "database"):
        os.makedirs(d, exist_ok=True)


def center_window(win, width, height):
    win.update_idletasks()
    sw = win.winfo_screenwidth()
    sh = win.winfo_screenheight()
    x = (sw - width) // 2
    y = (sh - height) // 2
    win.geometry(f"{width}x{height}+{x}+{y}")


def toast(parent, message, bg=None, fg="white", duration=2200, icon=None):
    """Small auto-dismissing notification pinned to the bottom of `parent`."""
    t = theme()
    bg = bg or t["success"]
    win = tk.Toplevel(parent)
    win.overrideredirect(True)
    win.attributes("-topmost", True)
    try:
        win.attributes("-alpha", 0.97)
    except tk.TclError:
        pass

    label_text = f"{icon}  {message}" if icon else message
    card_frame = tk.Frame(win, bg=bg, padx=22, pady=14)
    card_frame.pack()
    tk.Label(card_frame, text=label_text, font=FONT_SUBTITLE, bg=bg, fg=fg,
             wraplength=340, justify="left").pack()

    parent.update_idletasks()
    px, py = parent.winfo_rootx(), parent.winfo_rooty()
    pw, ph = parent.winfo_width(), parent.winfo_height()
    win.update_idletasks()
    ww, wh = win.winfo_width(), win.winfo_height()
    x = px + (pw - ww) // 2
    y = py + ph - wh - 40
    win.geometry(f"+{max(0, x)}+{max(0, y)}")

    win.after(duration, win.destroy)
    return win


def _hex_to_rgb(h):
    h = h.lstrip("#")
    return tuple(int(h[i:i + 2], 16) for i in (0, 2, 4))


def _rgb_to_hex(rgb):
    return "#%02x%02x%02x" % tuple(max(0, min(255, int(c))) for c in rgb)


def mix(color_a, color_b, t):
    """Linear-interpolate between two hex colours (t in [0, 1])."""
    a, b = _hex_to_rgb(color_a), _hex_to_rgb(color_b)
    return _rgb_to_hex(tuple(a[i] + (b[i] - a[i]) * t for i in range(3)))


# --------------------------------------------------------------------------- #
# Rounded, canvas-based button — the core "modern" building block.
# Supports solid / outline / ghost styles, hover + press states, optional
# leading icon glyph, and disabled state. Behaves like a normal widget
# (pack / grid / place all work since it subclasses tk.Canvas).
# --------------------------------------------------------------------------- #
class RoundButton(tk.Canvas):
    def __init__(self, parent, text, command=None, bg=None, fg=None, hover_bg=None,
                 font=None, radius=10, padx=18, pady=10, width=None, height=None,
                 variant="solid", icon=None, state="normal", border_color=None):
        t = theme()
        self._parent_bg = _widget_bg(parent)
        super().__init__(parent, bg=self._parent_bg, highlightthickness=0, bd=0,
                          cursor="hand2" if state != "disabled" else "arrow")
        self.command = command
        self.text = f"{icon}  {text}" if icon else text
        self.font = font or FONT_BUTTON
        self.radius = radius
        self.padx, self.pady = padx, pady
        self.variant = variant
        self.state_ = state

        if variant == "solid":
            base = bg or t["primary"]
            self.bg_normal = base
            self.bg_hover = hover_bg or mix(base, "#000000", 0.12)
            self.bg_press = mix(base, "#000000", 0.22)
            self.fg_color = fg or t["on_primary"]
            self.outline = None
        elif variant == "outline":
            self.bg_normal = t["surface"]
            self.bg_hover = t["surface_alt"]
            self.bg_press = t["border"]
            self.fg_color = fg or (bg or t["primary"])
            self.outline = border_color or (bg or t["primary"])
        else:  # ghost
            self.bg_normal = self._parent_bg
            self.bg_hover = t["surface_alt"] if variant != "ghost_dark" else mix(self._parent_bg, "#ffffff", 0.15)
            self.bg_press = t["border"]
            self.fg_color = fg or t["text"]
            self.outline = None

        if self.state_ == "disabled":
            self.bg_normal = self.bg_hover = self.bg_press = t["border"]
            self.fg_color = t["muted"]

        tmp = tk.Label(parent, text=self.text, font=self.font)
        tw = tmp.winfo_reqwidth() or (8 * len(self.text))
        th = tmp.winfo_reqheight() or 16
        tmp.destroy()

        w = width or (tw + padx * 2)
        h = height or (th + pady * 2)
        self.configure(width=w, height=h)

        self._draw(self.bg_normal)
        if self.state_ != "disabled":
            self.bind("<Enter>", lambda e: self._draw(self.bg_hover))
            self.bind("<Leave>", lambda e: self._draw(self.bg_normal))
            self.bind("<ButtonPress-1>", lambda e: self._draw(self.bg_press))
            self.bind("<ButtonRelease-1>", self._on_release)

    def _round_points(self, x1, y1, x2, y2, r):
        r = min(r, (x2 - x1) / 2, (y2 - y1) / 2)
        return [
            x1 + r, y1, x2 - r, y1, x2, y1, x2, y1 + r,
            x2, y2 - r, x2, y2, x2 - r, y2, x1 + r, y2,
            x1, y2, x1, y2 - r, x1, y1 + r, x1, y1,
        ]

    def _draw(self, fill):
        self.delete("all")
        w = int(self["width"])
        h = int(self["height"])
        pts = self._round_points(1, 1, w - 1, h - 1, self.radius)
        outline = self.outline or ""
        self.create_polygon(pts, smooth=True, fill=fill,
                             outline=outline if outline else fill,
                             width=1.4 if outline else 1)
        self.create_text(w / 2, h / 2, text=self.text, fill=self.fg_color, font=self.font)

    def _on_release(self, event):
        self._draw(self.bg_hover)
        w, h = int(self["width"]), int(self["height"])
        if 0 <= event.x <= w and 0 <= event.y <= h and self.command:
            self.command()

    def set_state(self, state):
        t = theme()
        self.state_ = state
        if state == "disabled":
            self.unbind("<Enter>"); self.unbind("<Leave>")
            self.unbind("<ButtonPress-1>"); self.unbind("<ButtonRelease-1>")
            self.configure(cursor="arrow")
            self._draw(t["border"])
        else:
            self.configure(cursor="hand2")
            self.bind("<Enter>", lambda e: self._draw(self.bg_hover))
            self.bind("<Leave>", lambda e: self._draw(self.bg_normal))
            self.bind("<ButtonPress-1>", lambda e: self._draw(self.bg_press))
            self.bind("<ButtonRelease-1>", self._on_release)
            self._draw(self.bg_normal)


def _widget_bg(widget):
    try:
        return widget["bg"]
    except tk.TclError:
        try:
            return widget["background"]
        except tk.TclError:
            return theme()["bg"]


def make_round_button(parent, text, command, bg=None, fg=None, font=None, radius=10, padx=18, pady=10,
                       state="normal", variant="solid", icon=None, width=None, height=None):
    """Back-compatible factory used across every screen; now returns a real
    rounded-corner canvas button instead of a flat tk.Button."""
    return RoundButton(parent, text, command=command, bg=bg, fg=fg, font=font, radius=radius,
                        padx=padx, pady=pady, state=state, variant=variant,
                        icon=icon, width=width, height=height)


# --------------------------------------------------------------------------- #
# Pill — small rounded status badge (canvas based, crisp on any background)
# --------------------------------------------------------------------------- #
class Pill(tk.Canvas):
    def __init__(self, parent, text, color=None, fg=None, font=None, padx=12, pady=5, soft=True):
        t = theme()
        parent_bg = _widget_bg(parent)
        super().__init__(parent, bg=parent_bg, highlightthickness=0, bd=0)
        color = color or t["primary"]
        font = font or FONT_TINY
        fill = mix(color, t["surface"], 0.82) if soft else color
        text_color = fg or (color if soft else t["on_primary"])

        tmp = tk.Label(parent, text=text, font=font)
        tw = tmp.winfo_reqwidth() or (7 * len(text))
        th = tmp.winfo_reqheight() or 14
        tmp.destroy()
        w, h = tw + padx * 2, th + pady * 2
        self.configure(width=w, height=h)
        r = h / 2
        pts = [r, 1, w - r, 1, w - r, 1, w - 1, 1, w - 1, h - r, w - 1, h - 1,
               w - r, h - 1, r, h - 1, 1, h - 1, 1, h - r, 1, r, 1, 1]
        self.create_polygon(pts, smooth=True, fill=fill, outline=fill)
        self.create_text(w / 2, h / 2, text=text, fill=text_color, font=font)


def pill(parent, text, color=None, **kw):
    return Pill(parent, text, color=color, **kw)


# --------------------------------------------------------------------------- #
# Soft gradient background (used on splash / login for a premium feel)
# --------------------------------------------------------------------------- #
def gradient_canvas(parent, width, height, color_top, color_bottom, steps=120, **kw):
    cv = tk.Canvas(parent, width=width, height=height, highlightthickness=0, bd=0, **kw)
    for i in range(steps):
        f = i / max(1, steps - 1)
        color = mix(color_top, color_bottom, f)
        y0 = int(height * i / steps)
        y1 = int(height * (i + 1) / steps) + 1
        cv.create_rectangle(0, y0, width, y1, outline="", fill=color)
    return cv


# --------------------------------------------------------------------------- #
# Modern bordered entry field with an animated focus ring.
# Returns (wrapper_frame, entry_widget) — pack/grid the wrapper.
# --------------------------------------------------------------------------- #
def entry_field(parent, textvariable=None, show=None, font=None, justify="left"):
    t = theme()
    wrapper = tk.Frame(parent, bg=t["border"], highlightthickness=0, bd=0)
    inner = tk.Frame(wrapper, bg=t["surface"])
    inner.pack(fill="both", expand=True, padx=1, pady=1)
    entry = tk.Entry(inner, textvariable=textvariable, font=font or FONT_NORMAL,
                      relief="flat", bd=0, bg=t["surface"], fg=t["text"],
                      insertbackground=t["primary"], show=show or "", justify=justify)
    entry.pack(fill="both", expand=True, padx=10, ipady=8)

    def on_focus_in(_e):
        wrapper.configure(bg=t["primary"])

    def on_focus_out(_e):
        wrapper.configure(bg=t["border"])

    entry.bind("<FocusIn>", on_focus_in)
    entry.bind("<FocusOut>", on_focus_out)
    return wrapper, entry


# --------------------------------------------------------------------------- #
# Segmented control — pill-style single-select (replaces bare Radiobuttons /
# a Combobox where only 2-4 options are involved).
# --------------------------------------------------------------------------- #
def segmented(parent, options, variable, command=None, width=110):
    t = theme()
    track = tk.Frame(parent, bg=t["bg_soft"], padx=3, pady=3)
    buttons = {}

    def refresh():
        for opt, b in buttons.items():
            active = variable.get() == opt
            b.configure(bg=t["surface"] if active else t["bg_soft"],
                        fg=t["primary"] if active else t["muted"])

    def select(opt):
        variable.set(opt)
        refresh()
        if command:
            command(opt)

    for opt in options:
        b = tk.Label(track, text=opt, font=utils_font_button(), padx=14, pady=8,
                      bg=t["bg_soft"], fg=t["muted"], cursor="hand2", width=max(0, width // 9))
        b.pack(side="left", padx=1)
        b.bind("<Button-1>", lambda e, o=opt: select(o))
        buttons[opt] = b
    refresh()
    return track


def utils_font_button():
    return FONT_BUTTON


# --------------------------------------------------------------------------- #
# Section header — accent bar + icon + title, used to open every screen
# section consistently.
# --------------------------------------------------------------------------- #
def section_header(parent, title, icon=None, subtitle=None):
    t = theme()
    wrap = tk.Frame(parent, bg=_widget_bg(parent))
    bar = tk.Frame(wrap, bg=t["primary"], width=4)
    bar.pack(side="left", fill="y", padx=(0, 10))
    text_wrap = tk.Frame(wrap, bg=_widget_bg(parent))
    text_wrap.pack(side="left", fill="both", expand=True)
    label_text = f"{icon}  {title}" if icon else title
    tk.Label(text_wrap, text=label_text, font=FONT_TITLE, bg=_widget_bg(parent), fg=t["text"]).pack(anchor="w")
    if subtitle:
        tk.Label(text_wrap, text=subtitle, font=FONT_SMALL, bg=_widget_bg(parent), fg=t["muted"]).pack(anchor="w")
    return wrap


# --------------------------------------------------------------------------- #
# Card frame — flat elevated surface: soft border + colour accent strip.
# --------------------------------------------------------------------------- #
def card(parent, accent=None, **kwargs):
    t = theme()
    outer = tk.Frame(parent, bg=t["border"])
    inner = tk.Frame(outer, bg=t["surface"], **kwargs)
    inner.pack(fill="both", expand=True, padx=1, pady=1)
    if accent:
        strip = tk.Frame(inner, bg=accent, width=4)
        strip.pack(side="left", fill="y")
    # expose outer's geometry methods on inner for a drop-in "card" API
    inner._outer = outer
    inner.grid = outer.grid
    inner.pack = outer.pack
    inner.place = outer.place
    return inner


# --------------------------------------------------------------------------- #
# ttk styling — flat, modern skin applied to every Tk() root so Combobox /
# Notebook / Treeview / Scrollbar match the custom palette instead of the
# OS-native look.
# --------------------------------------------------------------------------- #
def setup_ttk_style(root):
    t = theme()
    style = ttk.Style(root)
    try:
        style.theme_use("clam")
    except tk.TclError:
        pass

    style.configure("TCombobox", fieldbackground=t["surface"], background=t["surface"],
                     foreground=t["text"], bordercolor=t["border"], lightcolor=t["surface"],
                     darkcolor=t["surface"], arrowcolor=t["primary"], padding=6, relief="flat")
    style.map("TCombobox", fieldbackground=[("readonly", t["surface"])],
              bordercolor=[("focus", t["primary"])])

    style.configure("TNotebook", background=t["bg"], borderwidth=0, tabmargins=[8, 8, 8, 0])
    style.configure("TNotebook.Tab", background=t["bg_soft"], foreground=t["muted"],
                     padding=[16, 10], font=FONT_SUBTITLE, borderwidth=0)
    style.map("TNotebook.Tab",
              background=[("selected", t["surface"])],
              foreground=[("selected", t["primary"])])

    style.configure("Treeview", rowheight=30, font=FONT_SMALL, background=t["surface"],
                     fieldbackground=t["surface"], foreground=t["text"], borderwidth=0)
    style.configure("Treeview.Heading", font=FONT_SUBTITLE, background=t["bg_soft"],
                     foreground=t["text_soft"], relief="flat", padding=8)
    style.map("Treeview", background=[("selected", t["primary_soft"])],
              foreground=[("selected", t["primary"])])
    style.layout("Treeview", [("Treeview.treearea", {"sticky": "nswe"})])

    style.configure("Vertical.TScrollbar", background=t["bg_soft"], troughcolor=t["bg"],
                     bordercolor=t["bg"], arrowcolor=t["muted"], relief="flat")
    style.configure("Horizontal.TScrollbar", background=t["bg_soft"], troughcolor=t["bg"],
                     bordercolor=t["bg"], arrowcolor=t["muted"], relief="flat")
    return style
