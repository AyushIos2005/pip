"""
dashboard.py
Main waiter/admin dashboard: live clock, table grid (5 tables) coloured
by status, notifications when the kitchen marks an order "Ready".
"""

import tkinter as tk
from tkinter import messagebox
import os

import utils
from database import Database

try:
    from PIL import Image, ImageTk
    PIL_OK = True
except ImportError:
    PIL_OK = False

STATUS_COLOR_KEY = {
    "available": "success",
    "occupied": "danger",
    "reserved": "warning",
}
STATUS_ICON = {"available": "✓", "occupied": "●", "reserved": "◷"}


class DashboardWindow(tk.Tk):
    def __init__(self, user):
        super().__init__()
        self.user = user
        self.db = Database.instance()
        self.title(f"{utils.RESTAURANT_NAME} - Dashboard")
        utils.center_window(self, 1040, 660)
        self.minsize(900, 580)
        t = utils.theme()
        self.configure(bg=t["bg"])
        utils.setup_ttk_style(self)

        self.table_widgets = {}
        self._build_topbar()
        self._build_tables_grid()
        self._tick_clock()
        self._poll_notifications()

    # ------------------------------------------------------------------ #
    def _build_topbar(self):
        t = utils.theme()
        bar = tk.Frame(self, bg=t["surface"], height=76)
        bar.pack(fill="x", side="top")
        bar.pack_propagate(False)
        tk.Frame(self, bg=t["border"], height=1).pack(fill="x")

        left = tk.Frame(bar, bg=t["surface"])
        left.pack(side="left", padx=20)

        logo_shown = False
        if PIL_OK and os.path.exists(utils.LOGO_PATH):
            try:
                img = Image.open(utils.LOGO_PATH).resize((44, 44))
                self._logo_img = ImageTk.PhotoImage(img)
                tk.Label(left, image=self._logo_img, bg=t["surface"]).pack(side="left", padx=(0, 12))
                logo_shown = True
            except Exception:
                logo_shown = False
        if not logo_shown:
            badge = tk.Canvas(left, width=46, height=46, bg=t["surface"], highlightthickness=0, bd=0)
            badge.pack(side="left", padx=(0, 12))
            badge.create_oval(2, 2, 44, 44, fill=t["primary"], outline="")
            badge.create_text(23, 23, text="🍽", font=("Segoe UI", 18), fill="white")

        name_frame = tk.Frame(left, bg=t["surface"])
        name_frame.pack(side="left")
        tk.Label(name_frame, text=utils.RESTAURANT_NAME, font=utils.FONT_SUBTITLE, bg=t["surface"], fg=t["text"]).pack(anchor="w")
        tk.Label(name_frame, text=f"{self.user['full_name']}  ·  {self.user['role'].title()}",
                 font=utils.FONT_SMALL, bg=t["surface"], fg=t["muted"]).pack(anchor="w")

        right = tk.Frame(bar, bg=t["surface"])
        right.pack(side="right", padx=20)

        utils.make_round_button(right, "Logout", self.logout, variant="ghost", fg=t["danger"], padx=14, pady=8).pack(side="right", padx=4)
        utils.make_round_button(right, "Kitchen", self.open_kitchen, icon="👨‍🍳", variant="outline", padx=14, pady=8).pack(side="right", padx=4)
        if self.user["role"] == "admin":
            utils.make_round_button(right, "Admin Panel", self.open_admin, icon="⚙", bg=t["accent"], fg="#1E1E1E", padx=14, pady=8).pack(side="right", padx=4)
        utils.make_round_button(right, "Theme", self.toggle_theme, icon="🌓", variant="ghost", padx=14, pady=8).pack(side="right", padx=4)

        clock_wrap = tk.Frame(right, bg=t["surface"])
        clock_wrap.pack(side="right", padx=(0, 16))
        self.clock_label = tk.Label(clock_wrap, text="", font=utils.FONT_SUBTITLE, bg=t["surface"], fg=t["primary"])
        self.clock_label.pack(anchor="e")
        self.date_label = tk.Label(clock_wrap, text="", font=utils.FONT_TINY, bg=t["surface"], fg=t["muted"])
        self.date_label.pack(anchor="e")

    def _build_tables_grid(self):
        t = utils.theme()
        wrap = tk.Frame(self, bg=t["bg"])
        wrap.pack(fill="both", expand=True, padx=28, pady=24)

        utils.section_header(wrap, "Tables", icon="🍽", subtitle="Tap a table to open its order").pack(anchor="w", fill="x", pady=(0, 18))

        self.grid_frame = tk.Frame(wrap, bg=t["bg"])
        self.grid_frame.pack(fill="both", expand=True)
        for i in range(5):
            self.grid_frame.grid_columnconfigure(i, weight=1)

        self._render_all_tables()
        self.after(3000, self._refresh_tables)

    def _render_all_tables(self):
        """(Re)draw every table card, incl. status-dependent action buttons."""
        for w in self.grid_frame.winfo_children():
            w.destroy()
        self.table_widgets = {}

        tables = list(self.db.tables.find().sort("table_no", 1))
        for idx, tb in enumerate(tables):
            self._render_table_card(idx, tb)

    def _render_table_card(self, idx, tb):
        t = utils.theme()
        color = t[STATUS_COLOR_KEY.get(tb["status"], "muted")]
        c = utils.card(self.grid_frame, accent=color, padx=0, pady=0)
        c.grid(row=0, column=idx, padx=8, sticky="nsew", ipady=4)

        body = tk.Frame(c, bg=t["surface"], padx=14, pady=16)
        body.pack(fill="both", expand=True)

        top_row = tk.Frame(body, bg=t["surface"])
        top_row.pack(fill="x")
        tk.Label(top_row, text=f"Table {tb['table_no']}", font=utils.FONT_SUBTITLE, bg=t["surface"], fg=t["text"]).pack(side="left")

        status_pill = utils.Pill(body, tb["status"].title(), color=color)
        status_pill.pack(anchor="w", pady=(6, 10))

        reservation = tb.get("reservation")
        if tb["status"] == "reserved" and reservation:
            info = f"{reservation.get('name', 'Guest')} · {reservation.get('party_size', '-')} pax"
            tk.Label(body, text=info, font=utils.FONT_TINY, bg=t["surface"], fg=t["muted"],
                     wraplength=160, justify="left").pack(anchor="w", pady=(0, 10))

        if tb["status"] == "available":
            utils.make_round_button(body, "Book Now", lambda n=tb["table_no"]: self.book_table(n),
                                     variant="outline", height=34).pack(fill="x", pady=(0, 6))
            utils.make_round_button(body, "Open Table", lambda n=tb["table_no"]: self.open_table(n),
                                     bg=t["primary"], height=36).pack(fill="x")
        elif tb["status"] == "reserved":
            utils.make_round_button(body, "Seat Guests", lambda n=tb["table_no"]: self.open_table(n),
                                     bg=t["primary"], height=36).pack(fill="x", pady=(0, 6))
            utils.make_round_button(body, "Cancel Reservation", lambda n=tb["table_no"]: self.cancel_reservation(n),
                                     variant="ghost", fg=t["danger"], height=32).pack(fill="x")
        else:
            utils.make_round_button(body, "Open Table", lambda n=tb["table_no"]: self.open_table(n),
                                     bg=t["primary"], height=36).pack(fill="x")

        self.table_widgets[tb["table_no"]] = c

    # ------------------------------------------------------------------ #
    def _refresh_tables(self):
        try:
            self._render_all_tables()
        except Exception:
            pass
        self.after(3000, self._refresh_tables)

    # ------------------------------------------------------------------ #
    def book_table(self, table_no):
        BookingDialog(self, table_no, self._confirm_booking)

    def _confirm_booking(self, table_no, name, phone, party_size):
        self.db.tables.update_one(
            {"table_no": table_no},
            {"$set": {
                "status": "reserved",
                "reservation": {
                    "name": name,
                    "phone": phone,
                    "party_size": party_size,
                    "reserved_at": utils.now(),
                },
                "updatedAt": utils.now(),
            }},
        )
        self._render_all_tables()

    def cancel_reservation(self, table_no):
        if messagebox.askyesno("Cancel Reservation", f"Cancel reservation for Table {table_no}?"):
            self.db.tables.update_one(
                {"table_no": table_no},
                {"$set": {"status": "available", "reservation": None, "updatedAt": utils.now()}},
            )
            self._render_all_tables()

    def _tick_clock(self):
        self.clock_label.config(text=utils.format_time())
        self.date_label.config(text=utils.format_date())
        self.after(1000, self._tick_clock)

    def _poll_notifications(self):
        """Alert the logged-in waiter when their order becomes 'ready'."""
        try:
            ready_orders = self.db.orders.find({
                "waiter_id": self.user["_id"], "status": "ready", "notified": False
            })
            for o in ready_orders:
                messagebox.showinfo("Order Ready", f"🔔 Table {o['table_no']} Order Ready!")
                self.db.orders.update_one({"_id": o["_id"]}, {"$set": {"notified": True}})
        except Exception:
            pass
        self.after(3000, self._poll_notifications)

    # ------------------------------------------------------------------ #
    def open_table(self, table_no):
        from menu import OrderWindow
        OrderWindow(self, table_no, self.user)

    def open_kitchen(self):
        from kitchen import KitchenWindow
        KitchenWindow(self)

    def open_admin(self):
        from admin import AdminPanel
        AdminPanel(self, self.user)

    def toggle_theme(self):
        utils.toggle_theme()
        self.destroy()
        DashboardWindow(self.user).mainloop()

    def logout(self):
        self.destroy()
        from login import LoginWindow
        LoginWindow().mainloop()


class BookingDialog(tk.Toplevel):
    """Small modal used by the 'Book Now' button to reserve a table."""

    def __init__(self, parent, table_no, on_confirm):
        super().__init__(parent)
        self.parent = parent
        self.table_no = table_no
        self.on_confirm = on_confirm
        t = utils.theme()
        self.configure(bg=t["surface"])
        self.title(f"Book Table {table_no}")
        utils.center_window(self, 340, 340)
        self.resizable(False, False)
        self.transient(parent)
        self.grab_set()

        tk.Label(self, text=f"Reserve Table {table_no}", font=utils.FONT_SUBTITLE,
                 bg=t["surface"], fg=t["text"]).pack(pady=(20, 14))

        form = tk.Frame(self, bg=t["surface"])
        form.pack(fill="x", padx=24)

        tk.Label(form, text="Customer Name", font=utils.FONT_SMALL, bg=t["surface"], fg=t["muted"]).pack(anchor="w")
        name_wrap, name_entry = utils.entry_field(form, font=utils.FONT_NORMAL)
        name_wrap.pack(fill="x", pady=(2, 12))
        self.name_var = tk.StringVar()
        name_entry.configure(textvariable=self.name_var)

        tk.Label(form, text="Phone Number", font=utils.FONT_SMALL, bg=t["surface"], fg=t["muted"]).pack(anchor="w")
        phone_wrap, phone_entry = utils.entry_field(form, font=utils.FONT_NORMAL)
        phone_wrap.pack(fill="x", pady=(2, 12))
        self.phone_var = tk.StringVar()
        phone_entry.configure(textvariable=self.phone_var)

        tk.Label(form, text="Party Size", font=utils.FONT_SMALL, bg=t["surface"], fg=t["muted"]).pack(anchor="w")
        party_wrap, party_entry = utils.entry_field(form, font=utils.FONT_NORMAL)
        party_wrap.pack(fill="x", pady=(2, 16))
        self.party_var = tk.StringVar(value="2")
        party_entry.configure(textvariable=self.party_var)

        btns = tk.Frame(self, bg=t["surface"])
        btns.pack(fill="x", padx=24, pady=(0, 20))
        utils.make_round_button(btns, "Confirm Booking", self._confirm, bg=t["success"], height=38).pack(fill="x", pady=(0, 6))
        utils.make_round_button(btns, "Cancel", self.destroy, variant="ghost", fg=t["muted"], height=32).pack(fill="x")

        name_entry.focus_set()

    def _confirm(self):
        name = self.name_var.get().strip()
        phone = self.phone_var.get().strip()
        party = self.party_var.get().strip()
        if not name:
            messagebox.showwarning("Missing Name", "Please enter the customer's name.", parent=self)
            return
        if not party.isdigit() or int(party) <= 0:
            messagebox.showwarning("Invalid Party Size", "Please enter a valid party size.", parent=self)
            return
        self.on_confirm(self.table_no, name, phone, int(party))
        self.destroy()