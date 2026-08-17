"""
main.py
Application entry point: splash screen -> login -> dashboard.

Run with:
    python main.py
"""

import tkinter as tk

import utils
from database import Database


class SplashScreen(tk.Tk):
    def __init__(self):
        super().__init__()
        self.overrideredirect(True)
        utils.center_window(self, 460, 300)
        t = utils.theme()
        self.configure(bg=t["bg"])
        utils.setup_ttk_style(self)

        bg = utils.gradient_canvas(self, 460, 300, t["primary_dark"], t["primary"])
        bg.place(x=0, y=0)

        tk.Label(bg, text="🍽", font=("Segoe UI", 50), bg=t["primary"], fg="white").place(relx=0.5, y=90, anchor="center")
        tk.Label(bg, text=utils.RESTAURANT_NAME, font=utils.FONT_DISPLAY, bg=t["primary"], fg="white").place(relx=0.5, y=150, anchor="center")
        tk.Label(bg, text="Restaurant POS System", font=utils.FONT_SMALL, bg=t["primary"], fg="#E3E7FB").place(relx=0.5, y=178, anchor="center")

        self.bar_w = 320
        self.bar_bg = tk.Canvas(bg, width=self.bar_w, height=8, bg=t["primary"], highlightthickness=0, bd=0)
        self.bar_bg.place(relx=0.5, y=225, anchor="center")
        self.bar_bg.create_polygon(
            *self._rounded(0, 0, self.bar_w, 8, 4), smooth=True,
            fill=utils.mix(t["primary"], "#000000", 0.25), outline="")
        self.fill_id = None

        tk.Label(bg, text="Loading…", font=utils.FONT_TINY, bg=t["primary"], fg="#C7CEF7").place(relx=0.5, y=245, anchor="center")

        self.progress = 0
        self._animate()

    def _rounded(self, x1, y1, x2, y2, r):
        r = min(r, (x2 - x1) / 2, (y2 - y1) / 2)
        return [x1 + r, y1, x2 - r, y1, x2, y1, x2, y1 + r, x2, y2 - r, x2, y2,
                x2 - r, y2, x1 + r, y2, x1, y2, x1, y2 - r, x1, y1 + r, x1, y1]

    def _animate(self):
        self.progress += 4
        t = utils.theme()
        if self.fill_id:
            self.bar_bg.delete(self.fill_id)
        w = max(8, int(self.bar_w * self.progress / 100))
        self.fill_id = self.bar_bg.create_polygon(*self._rounded(0, 0, w, 8, 4), smooth=True, fill=t["accent"], outline="")
        if self.progress < 100:
            self.after(28, self._animate)
        else:
            self.after(150, self._go_to_login)

    def _go_to_login(self):
        self.destroy()
        from login import LoginWindow
        LoginWindow().mainloop()


def main():
    utils.ensure_dirs()
    db = Database.instance()
    ok, msg = db.test_connection()
    if ok:
        db.seed_data()
    SplashScreen().mainloop()


if __name__ == "__main__":
    main()
