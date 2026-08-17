"""
customer_feedback.py
Post-payment flow: a green "Payment Successful" screen, a Save Customer
modal (creates/updates a customer + upserts by mobile number), an
automatic Feedback modal, and a final Close Table step.

Flow:
    PaymentSuccessWindow
        -> Save Customer (SaveCustomerDialog) -> FeedbackDialog -> Close Table stage
        -> Skip & Close Table -> table closed immediately
"""

import os
import platform
import subprocess
import tkinter as tk
from tkinter import messagebox

import utils
import models
from database import Database


# --------------------------------------------------------------------------- #
# Star rating control — 5 clickable canvas stars.
# --------------------------------------------------------------------------- #
class StarRating(tk.Frame):
    def __init__(self, parent, value=0, size=34, on_change=None):
        t = utils.theme()
        super().__init__(parent, bg=t["surface"])
        self.size = size
        self.on_change = on_change
        self.value = tk.IntVar(value=value)
        self._stars = []
        for i in range(1, 6):
            c = tk.Canvas(self, width=size, height=size, bg=t["surface"], highlightthickness=0, bd=0, cursor="hand2")
            c.pack(side="left", padx=3)
            c.bind("<Button-1>", lambda e, n=i: self._select(n))
            c.bind("<Enter>", lambda e, n=i: self._draw(preview=n))
            c.bind("<Leave>", lambda e: self._draw())
            self._stars.append(c)
        self._draw()

    def _select(self, n):
        self.value.set(n)
        self._draw()
        if self.on_change:
            self.on_change(n)

    def _star_points(self, cx, cy, r_out, r_in):
        import math
        pts = []
        for i in range(10):
            r = r_out if i % 2 == 0 else r_in
            angle = math.pi / 2 + i * math.pi / 5
            pts.append(cx + r * math.cos(angle))
            pts.append(cy - r * math.sin(angle))
        return pts

    def _draw(self, preview=None):
        t = utils.theme()
        filled_upto = preview if preview is not None else self.value.get()
        for i, c in enumerate(self._stars, start=1):
            c.delete("all")
            filled = i <= filled_upto
            color = t["accent"] if filled else t["border"]
            pts = self._star_points(self.size / 2, self.size / 2, self.size * 0.46, self.size * 0.19)
            c.create_polygon(pts, fill=color, outline=color, smooth=False)

    def get(self):
        return self.value.get()


# --------------------------------------------------------------------------- #
# Checkmark success animation — simple canvas draw, no external assets.
# --------------------------------------------------------------------------- #
class SuccessBadge(tk.Canvas):
    def __init__(self, parent, size=110):
        t = utils.theme()
        super().__init__(parent, width=size, height=size, bg=t["surface"], highlightthickness=0, bd=0)
        self.size = size
        self._progress = 0
        self._animate()

    def _animate(self):
        t = utils.theme()
        self.delete("all")
        s = self.size
        # Growing ring
        ring_extent = min(360, self._progress * 18)
        self.create_oval(4, 4, s - 4, s - 4, outline=t["border"], width=4)
        if ring_extent > 0:
            self.create_arc(4, 4, s - 4, s - 4, start=90, extent=-ring_extent,
                             style="arc", outline=t["success"], width=4)
        # Checkmark, drawn once the ring is mostly complete
        if self._progress >= 16:
            frac = min(1.0, (self._progress - 16) / 5.0)
            x1, y1 = s * 0.28, s * 0.53
            x2, y2 = s * 0.44, s * 0.68
            x3, y3 = s * 0.74, s * 0.34
            if frac <= 0.5:
                f = frac / 0.5
                self.create_line(x1, y1, x1 + (x2 - x1) * f, y1 + (y2 - y1) * f,
                                  fill=t["success"], width=6, capstyle="round")
            else:
                self.create_line(x1, y1, x2, y2, fill=t["success"], width=6, capstyle="round")
                f = (frac - 0.5) / 0.5
                self.create_line(x2, y2, x2 + (x3 - x2) * f, y2 + (y3 - y2) * f,
                                  fill=t["success"], width=6, capstyle="round")
        if self._progress < 21:
            self._progress += 1
            self.after(28, self._animate)


def _open_file(path):
    try:
        system = platform.system()
        if system == "Windows":
            os.startfile(path)  # noqa
        elif system == "Darwin":
            subprocess.Popen(["open", path])
        else:
            subprocess.Popen(["xdg-open", path])
    except Exception:
        messagebox.showinfo("Receipt", f"Receipt saved at:\n{path}")


# --------------------------------------------------------------------------- #
# Payment Successful screen — hub for Save Customer / Skip / Close Table.
# --------------------------------------------------------------------------- #
class PaymentSuccessWindow(tk.Toplevel):
    def __init__(self, dashboard, order, grand_total, mode, pdf_path=None):
        super().__init__(dashboard)
        self.dashboard = dashboard
        self.order = order
        self.grand_total = grand_total
        self.mode = mode
        self.pdf_path = pdf_path
        self.db = Database.instance()

        self.customer = None  # set once Save Customer succeeds

        self.title("Payment Successful")
        utils.center_window(self, 440, 460)
        self.resizable(False, False)
        self.protocol("WM_DELETE_WINDOW", lambda: None)  # force explicit flow
        self.grab_set()
        t = utils.theme()
        self.configure(bg=t["bg"])
        utils.setup_ttk_style(self)

        self.body = tk.Frame(self, bg=t["bg"])
        self.body.pack(fill="both", expand=True)
        self._show_success_stage()

    # ------------------------------------------------------------------ #
    def _clear(self):
        for w in self.body.winfo_children():
            w.destroy()

    def _show_success_stage(self):
        self._clear()
        t = utils.theme()
        outer = utils.card(self.body, padx=0, pady=0)
        outer.pack(fill="both", expand=True, padx=16, pady=16)
        card = tk.Frame(outer, bg=t["surface"], padx=24, pady=24)
        card.pack(fill="both", expand=True)

        badge_wrap = tk.Frame(card, bg=t["surface"])
        badge_wrap.pack(pady=(4, 10))
        SuccessBadge(badge_wrap).pack()

        tk.Label(card, text="✅ Payment Successful", font=utils.FONT_TITLE, bg=t["surface"], fg=t["success"]).pack(pady=(4, 2))
        tk.Label(card, text="Thank you for dining with us!", font=utils.FONT_NORMAL, bg=t["surface"], fg=t["text"]).pack()
        tk.Label(card, text="Help us improve your experience by saving your details\nand sharing quick feedback.",
                 font=utils.FONT_SMALL, bg=t["surface"], fg=t["muted"], justify="center").pack(pady=(6, 18))

        utils.make_round_button(card, "Save Customer", self._open_save_customer,
                                 bg=t["success"], icon="👤", height=44).pack(fill="x", pady=(0, 8))
        utils.make_round_button(card, "Skip & Close Table", self._skip_and_close,
                                 variant="outline", fg=t["muted"], height=40).pack(fill="x")

        if self.pdf_path:
            utils.make_round_button(card, "Print Receipt", lambda: _open_file(self.pdf_path),
                                     variant="ghost", fg=t["primary"], icon="🖨", height=34).pack(fill="x", pady=(10, 0))

    def _show_close_table_stage(self):
        self._clear()
        t = utils.theme()
        outer = utils.card(self.body, padx=0, pady=0)
        outer.pack(fill="both", expand=True, padx=16, pady=16)
        card = tk.Frame(outer, bg=t["surface"], padx=24, pady=28)
        card.pack(fill="both", expand=True)

        tk.Label(card, text="🎉", font=("Segoe UI", 40), bg=t["surface"]).pack(pady=(8, 6))
        tk.Label(card, text="All done!", font=utils.FONT_TITLE, bg=t["surface"], fg=t["text"]).pack()
        tk.Label(card, text=f"Table {self.order['table_no']} is ready to be closed.",
                 font=utils.FONT_SMALL, bg=t["surface"], fg=t["muted"]).pack(pady=(4, 24))

        if self.pdf_path:
            utils.make_round_button(card, "Print Receipt", lambda: _open_file(self.pdf_path),
                                     variant="outline", fg=t["primary"], icon="🖨", height=38).pack(fill="x", pady=(0, 10))

        utils.make_round_button(card, "Close Table", self._close_table,
                                 bg=t["primary"], icon="✔", height=46).pack(fill="x")

    # ------------------------------------------------------------------ #
    def _open_save_customer(self):
        SaveCustomerDialog(self, self.order, self.grand_total, self.mode, self._on_customer_saved)

    def _on_customer_saved(self, customer):
        self.customer = customer
        FeedbackDialog(self, self.order, self.grand_total, self.mode, customer, self._on_feedback_done)

    def _on_feedback_done(self):
        self._show_close_table_stage()

    def _skip_and_close(self):
        self._close_table()

    def _close_table(self):
        self.db.tables.update_one(
            {"table_no": self.order["table_no"]},
            {"$set": {"status": "available", "current_order_id": None, "updatedAt": utils.now()}},
        )
        self.grab_release()
        self.destroy()
        if hasattr(self.dashboard, "_refresh_tables"):
            self.dashboard._refresh_tables()


# --------------------------------------------------------------------------- #
# Save Customer modal
# --------------------------------------------------------------------------- #
class SaveCustomerDialog(tk.Toplevel):
    def __init__(self, parent, order, grand_total, mode, on_saved):
        super().__init__(parent)
        self.parent = parent
        self.order = order
        self.grand_total = grand_total
        self.mode = mode
        self.on_saved = on_saved
        self.db = Database.instance()

        self.title("Save Customer")
        utils.center_window(self, 400, 560)
        self.resizable(False, False)
        self.grab_set()
        t = utils.theme()
        self.configure(bg=t["bg"])
        utils.setup_ttk_style(self)
        self._build_ui()

    def _field(self, parent, label, required=False):
        t = utils.theme()
        tk.Label(parent, text=label + (" *" if required else ""), bg=t["surface"], fg=t["muted"], font=utils.FONT_TINY).pack(anchor="w", pady=(10, 2))
        var = tk.StringVar()
        wrap, entry = utils.entry_field(parent, textvariable=var)
        wrap.pack(fill="x")
        return var

    def _build_ui(self):
        t = utils.theme()
        outer = utils.card(self, padx=0, pady=0)
        outer.pack(fill="both", expand=True, padx=14, pady=14)
        card = tk.Frame(outer, bg=t["surface"], padx=20, pady=16)
        card.pack(fill="both", expand=True)

        tk.Label(card, text="👤  Customer Information", font=utils.FONT_SUBTITLE, bg=t["surface"], fg=t["text"]).pack(anchor="w")
        tk.Label(card, text="Build your customer database for loyalty & marketing.",
                 font=utils.FONT_TINY, bg=t["surface"], fg=t["muted"]).pack(anchor="w", pady=(2, 0))

        self.name_var = self._field(card, "Customer Name", required=True)
        self.mobile_var = self._field(card, "Mobile Number", required=True)
        self.email_var = self._field(card, "Email (Optional)")
        self.birthday_var = self._field(card, "Birthday (Optional, DD-MM-YYYY)")
        self.notes_var = self._field(card, "Notes (Optional)")

        btn_row = tk.Frame(card, bg=t["surface"])
        btn_row.pack(fill="x", pady=(20, 0))
        utils.make_round_button(btn_row, "Save Customer", self.save, bg=t["success"], height=42).pack(fill="x", pady=(0, 8))
        utils.make_round_button(btn_row, "Cancel", self.destroy, variant="ghost", fg=t["muted"], height=36).pack(fill="x")

    def save(self):
        name = self.name_var.get().strip()
        mobile = self.mobile_var.get().strip()
        if not name:
            messagebox.showwarning("Missing", "Customer Name is required.", parent=self)
            return
        if not mobile:
            messagebox.showwarning("Missing", "Mobile Number is required.", parent=self)
            return

        items = list(self.db.order_items.find({"order_id": self.order["_id"]}))
        item_summaries = [{"name": it["name"], "qty": it["qty"]} for it in items]

        existing = self.db.customers.find_one({"mobile": mobile})
        if existing:
            update = models.apply_customer_visit(
                existing, order_amount=self.grand_total, payment_method=self.mode, items=item_summaries,
                email=self.email_var.get().strip(), birthday=self.birthday_var.get().strip(),
                notes=self.notes_var.get().strip(),
            )
            # Name can be corrected too, but never blanked out.
            if name:
                update["name"] = name
            self.db.customers.update_one({"_id": existing["_id"]}, {"$set": update})
            customer = self.db.customers.find_one({"_id": existing["_id"]})
        else:
            doc = models.new_customer_doc(
                name, mobile, email=self.email_var.get().strip(), birthday=self.birthday_var.get().strip(),
                notes=self.notes_var.get().strip(), order_amount=self.grand_total, payment_method=self.mode,
                items=item_summaries,
            )
            result = self.db.customers.insert_one(doc)
            customer = self.db.customers.find_one({"_id": result.inserted_id})

        self.db.orders.update_one({"_id": self.order["_id"]}, {"$set": {"customer_id": customer["_id"]}})

        utils.toast(self.parent, "Customer information saved successfully.", icon="✅")
        self.destroy()
        self.on_saved(customer)


# --------------------------------------------------------------------------- #
# Feedback modal — opens automatically right after Save Customer succeeds.
# --------------------------------------------------------------------------- #
class FeedbackDialog(tk.Toplevel):
    def __init__(self, parent, order, grand_total, mode, customer, on_done):
        super().__init__(parent)
        self.parent = parent
        self.order = order
        self.grand_total = grand_total
        self.mode = mode
        self.customer = customer
        self.on_done = on_done
        self.db = Database.instance()

        self.title("Customer Feedback")
        utils.center_window(self, 400, 420)
        self.resizable(False, False)
        self.grab_set()
        t = utils.theme()
        self.configure(bg=t["bg"])
        utils.setup_ttk_style(self)
        self._build_ui()

    def _build_ui(self):
        t = utils.theme()
        outer = utils.card(self, padx=0, pady=0)
        outer.pack(fill="both", expand=True, padx=14, pady=14)
        card = tk.Frame(outer, bg=t["surface"], padx=20, pady=20)
        card.pack(fill="both", expand=True)

        tk.Label(card, text="⭐  How was your experience?", font=utils.FONT_SUBTITLE, bg=t["surface"], fg=t["text"]).pack(anchor="w")
        tk.Label(card, text=f"{self.customer.get('name', '')}, we'd love your feedback.",
                 font=utils.FONT_TINY, bg=t["surface"], fg=t["muted"]).pack(anchor="w", pady=(2, 16))

        self.stars = StarRating(card, value=5)
        self.stars.pack(pady=(0, 16))

        tk.Label(card, text="COMMENT (OPTIONAL)", bg=t["surface"], fg=t["muted"], font=utils.FONT_TINY).pack(anchor="w")
        self.comment_text = tk.Text(card, height=4, font=utils.FONT_NORMAL, wrap="word", bd=1,
                                     relief="solid", highlightthickness=0, bg=t["surface_alt"], fg=t["text"])
        self.comment_text.pack(fill="x", pady=(4, 18))

        utils.make_round_button(card, "Submit Feedback", self.submit, bg=t["success"], icon="✓", height=42).pack(fill="x", pady=(0, 8))
        utils.make_round_button(card, "Skip", self.skip, variant="ghost", fg=t["muted"], height=34).pack(fill="x")

    def submit(self):
        rating = self.stars.get()
        comment = self.comment_text.get("1.0", "end").strip()
        waiter_id = self.order.get("waiter_id")
        waiter_name = self.order.get("waiter_name", "")

        doc = models.new_feedback_doc(
            customer_id=self.customer["_id"], order_id=self.order["_id"], table_no=self.order["table_no"],
            waiter_id=waiter_id, waiter_name=waiter_name, rating=rating, comment=comment,
            total_bill=self.grand_total, payment_method=self.mode,
        )
        result = self.db.feedback.insert_one(doc)

        rating_sum = self.customer.get("rating_sum", 0.0) + rating
        rating_count = self.customer.get("rating_count", 0) + 1
        history_entry = {
            "feedback_id": result.inserted_id, "rating": rating, "comment": comment, "date": doc["date"],
        }
        history = list(self.customer.get("feedback_history", [])) + [history_entry]
        self.db.customers.update_one({"_id": self.customer["_id"]}, {"$set": {
            "rating_sum": rating_sum, "rating_count": rating_count,
            "average_rating": rating_sum / rating_count if rating_count else 0.0,
            "feedback_history": history[-25:],
            "updatedAt": utils.now(),
        }})

        utils.toast(self.parent, "Thank you for your feedback ❤️", icon="❤️")
        self.destroy()
        self.on_done()

    def skip(self):
        self.destroy()
        self.on_done()
