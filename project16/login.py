"""
login.py
Login screen with Admin / Waiter role selection, authenticated against
the MongoDB `users` collection.
"""

import tkinter as tk
from tkinter import messagebox

import utils
import models
from database import Database


class LoginWindow(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title(f"{utils.RESTAURANT_NAME} - Login")
        utils.center_window(self, 900, 560)
        self.resizable(False, False)
        self.db = Database.instance()
        t = utils.theme()
        self.configure(bg=t["bg"])
        utils.setup_ttk_style(self)
        self._build_ui()

    def _build_ui(self):
        t = utils.theme()
        root = tk.Frame(self, bg=t["surface"])
        root.pack(fill="both", expand=True)

        # ---- Left: branding panel with gradient ----
        left = utils.gradient_canvas(root, 440, 560, t["primary_dark"], t["primary"])
        left.pack(side="left", fill="y")
        left.create_text(60, 210, text="🍽", font=("Segoe UI", 54), fill="white", anchor="w")
        left.create_text(60, 280, text=utils.RESTAURANT_NAME, font=utils.FONT_DISPLAY, fill="white", anchor="w")
        left.create_text(60, 315, text="Fast, friendly service —\nevery table, every time.",
                          font=utils.FONT_NORMAL, fill="#E3E7FB", anchor="w", justify="left")
        left.create_text(60, 500, text=utils.RESTAURANT_ADDRESS, font=utils.FONT_SMALL, fill="#C7CEF7", anchor="w")

        # ---- Right: form panel ----
        right = tk.Frame(root, bg=t["surface"])
        right.pack(side="left", fill="both", expand=True)

        card = tk.Frame(right, bg=t["surface"])
        card.place(relx=0.5, rely=0.5, anchor="center", width=340)

        tk.Label(card, text="Welcome back", font=utils.FONT_TITLE, bg=t["surface"], fg=t["text"]).pack(anchor="w")
        tk.Label(card, text="Sign in to continue to the POS", font=utils.FONT_SMALL, bg=t["surface"], fg=t["muted"]).pack(anchor="w", pady=(0, 22))

        tk.Label(card, text="I AM A", font=utils.FONT_TINY, bg=t["surface"], fg=t["muted"], anchor="w").pack(fill="x")
        self.role_var = tk.StringVar(value="waiter")
        seg = utils.segmented(card, ["waiter", "admin"], self.role_var, width=150)
        seg.pack(fill="x", pady=(4, 18))

        tk.Label(card, text="USERNAME", font=utils.FONT_TINY, bg=t["surface"], fg=t["muted"], anchor="w").pack(fill="x")
        user_wrap, self.user_entry = utils.entry_field(card, textvariable=tk.StringVar())
        user_wrap.pack(fill="x", pady=(4, 16))

        tk.Label(card, text="PASSWORD", font=utils.FONT_TINY, bg=t["surface"], fg=t["muted"], anchor="w").pack(fill="x")
        pass_wrap, self.pass_entry = utils.entry_field(card, show="•")
        pass_wrap.pack(fill="x", pady=(4, 24))
        self.pass_entry.bind("<Return>", lambda e: self.do_login())

        utils.make_round_button(card, "Log In", self.do_login, radius=10, height=44).pack(fill="x")

        tk.Label(card, text="Demo — admin/admin123  •  waiter/waiter123",
                 font=utils.FONT_TINY, bg=t["surface"], fg=t["muted"]).pack(pady=(18, 0))

        ok, msg = self.db.test_connection()
        status_color = t["success"] if ok else t["danger"]
        status_text = "MongoDB connected" if ok else "MongoDB not reachable"
        status_row = tk.Frame(card, bg=t["surface"])
        status_row.pack(pady=(10, 0))
        utils.Pill(status_row, status_text, color=status_color).pack()

    def do_login(self):
        username = self.user_entry.get().strip()
        password = self.pass_entry.get().strip()
        role = self.role_var.get()

        if not username or not password:
            messagebox.showwarning("Missing info", "Please enter username and password.")
            return

        try:
            self.db.seed_data()
            user = self.db.users.find_one({"username": username, "role": role, "status": "active"})
        except Exception as e:
            messagebox.showerror("Database Error", f"Could not reach MongoDB:\n{e}")
            return

        if not user or not utils.verify_password(password, user["password"]):
            messagebox.showerror("Login Failed", "Invalid username or password.")
            return

        self.destroy()
        from dashboard import DashboardWindow
        DashboardWindow(user).mainloop()


if __name__ == "__main__":
    LoginWindow().mainloop()
