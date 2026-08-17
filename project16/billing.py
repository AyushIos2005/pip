"""
billing.py
Billing screen: computes subtotal / GST / discount / grand total for an
order, then generates a professional PDF receipt (ReportLab) and stores
the payment record in MongoDB.
"""

import os
import tkinter as tk
from tkinter import messagebox

import utils
from database import Database

from reportlab.lib.pagesizes import A5
from reportlab.lib.units import mm
from reportlab.lib import colors
from reportlab.pdfgen import canvas as pdfcanvas


class BillingWindow(tk.Toplevel):
    def __init__(self, parent, order):
        super().__init__(parent)
        self.parent = parent
        self.order = order
        self.db = Database.instance()
        self.title(f"Bill - Table {order['table_no']}")
        utils.center_window(self, 480, 660)
        self.resizable(False, False)
        t = utils.theme()
        self.configure(bg=t["bg"])
        utils.setup_ttk_style(self)

        self.items = list(self.db.order_items.find({"order_id": order["_id"]}))
        self.settings = self.db.get_settings()
        self._build_ui()

    def _build_ui(self):
        t = utils.theme()
        outer = utils.card(self, padx=0, pady=0)
        outer.pack(fill="both", expand=True, padx=16, pady=16)
        card = tk.Frame(outer, bg=t["surface"], padx=20, pady=20)
        card.pack(fill="both", expand=True)

        tk.Label(card, text="🧾  " + utils.RESTAURANT_NAME, font=utils.FONT_SUBTITLE, bg=t["surface"], fg=t["text"]).pack(anchor="w")
        tk.Label(card, text=f"Table {self.order['table_no']}  ·  Waiter: {self.order['waiter_name']}",
                 font=utils.FONT_SMALL, bg=t["surface"], fg=t["muted"]).pack(anchor="w", pady=(0, 12))

        list_frame = tk.Frame(card, bg=t["surface"])
        list_frame.pack(fill="x", pady=4)
        subtotal = 0.0
        for it in self.items:
            line_total = it["price"] * it["qty"]
            subtotal += line_total
            row = tk.Frame(list_frame, bg=t["surface"])
            row.pack(fill="x", pady=2)
            tk.Label(row, text=f"{it['name']}  ×{it['qty']}", font=utils.FONT_SMALL, bg=t["surface"], fg=t["text"]).pack(side="left")
            tk.Label(row, text=utils.format_currency(line_total), font=utils.FONT_SMALL, bg=t["surface"], fg=t["text"]).pack(side="right")
        self.subtotal = subtotal

        tk.Frame(card, bg=t["border"], height=1).pack(fill="x", pady=14)

        gst_row = tk.Frame(card, bg=t["surface"])
        gst_row.pack(fill="x", pady=6)
        tk.Label(gst_row, text="GST %", bg=t["surface"], fg=t["text"], font=utils.FONT_SMALL).pack(side="left")
        self.gst_var = tk.DoubleVar(value=self.settings.get("gst_percent", 5.0))
        gst_wrap, gst_entry = utils.entry_field(gst_row, textvariable=self.gst_var, justify="right")
        gst_wrap.pack(side="right")
        gst_entry.configure(width=6)

        disc_row = tk.Frame(card, bg=t["surface"])
        disc_row.pack(fill="x", pady=6)
        tk.Label(disc_row, text="Discount (₹)", bg=t["surface"], fg=t["text"], font=utils.FONT_SMALL).pack(side="left")
        self.discount_var = tk.DoubleVar(value=0.0)
        disc_wrap, disc_entry = utils.entry_field(disc_row, textvariable=self.discount_var, justify="right")
        disc_wrap.pack(side="right")
        disc_entry.configure(width=6)

        total_card = tk.Frame(card, bg=t["primary_soft"], padx=14, pady=12)
        total_card.pack(fill="x", pady=16)
        self.total_label = tk.Label(total_card, text="", font=utils.FONT_TITLE, bg=t["primary_soft"], fg=t["primary"])
        self.total_label.pack()
        self._recalc()

        self.gst_var.trace_add("write", lambda *a: self._recalc())
        self.discount_var.trace_add("write", lambda *a: self._recalc())

        utils.make_round_button(card, "Proceed to Payment", self.proceed_payment, bg=t["success"], icon="💳", height=42).pack(fill="x", pady=6)

    def _recalc(self):
        try:
            gst_amt = self.subtotal * (self.gst_var.get() / 100.0)
        except tk.TclError:
            gst_amt = 0.0
        try:
            discount = self.discount_var.get()
        except tk.TclError:
            discount = 0.0
        self.grand_total = max(0.0, self.subtotal + gst_amt - discount)
        self.total_label.config(text=f"Grand Total: {utils.format_currency(self.grand_total)}")

    def proceed_payment(self):
        from payment import PaymentDialog
        PaymentDialog(self, self.grand_total, self._on_paid)

    def _on_paid(self, mode):
        bill_no = self.db.next_sequence("bill")
        pdf_path = self._generate_pdf(bill_no, mode)

        import models
        payment_doc = models.new_payment_doc(self.order["_id"], bill_no, self.grand_total, mode, self.order["table_no"], self.order["waiter_name"])
        payment_doc["pdf_path"] = pdf_path
        payment_doc["gst_percent"] = self.gst_var.get()
        payment_doc["discount"] = self.discount_var.get()
        payment_doc["subtotal"] = self.subtotal
        self.db.payments.insert_one(payment_doc)

        self.db.orders.update_one({"_id": self.order["_id"]}, {"$set": {
            "status": "paid", "bill_no": bill_no, "gst_percent": self.gst_var.get(),
            "discount": self.discount_var.get(), "updatedAt": utils.now(),
        }})
        # NOTE: the table is intentionally left "occupied" here — it is only
        # freed once the waiter finishes (or skips) the post-payment
        # Save Customer / Feedback flow and taps "Close Table".
        self.db.sales.insert_one({
            "order_id": self.order["_id"], "bill_no": bill_no, "table_no": self.order["table_no"],
            "waiter_name": self.order["waiter_name"], "amount": self.grand_total, "mode": mode,
            "status": "completed", "createdAt": utils.now(), "updatedAt": utils.now(),
        })

        dashboard = self.parent.parent if hasattr(self.parent, "parent") else self.parent
        order_window = self.parent
        self.destroy()
        if hasattr(order_window, "destroy"):
            order_window.destroy()

        from customer_feedback import PaymentSuccessWindow
        PaymentSuccessWindow(dashboard, self.order, self.grand_total, mode, pdf_path=pdf_path)

    def _generate_pdf(self, bill_no, mode):
        os.makedirs(utils.RECEIPTS_DIR, exist_ok=True)
        path = os.path.join(utils.RECEIPTS_DIR, f"bill_{bill_no}.pdf")
        c = pdfcanvas.Canvas(path, pagesize=A5)
        width, height = A5
        y = height - 15 * mm

        c.setFont("Helvetica-Bold", 14)
        c.drawCentredString(width / 2, y, utils.RESTAURANT_NAME)
        y -= 6 * mm
        c.setFont("Helvetica", 8)
        c.drawCentredString(width / 2, y, utils.RESTAURANT_ADDRESS)
        y -= 4.5 * mm
        c.drawCentredString(width / 2, y, f"GSTIN: {utils.RESTAURANT_GSTIN}  |  Ph: {utils.RESTAURANT_PHONE}")
        y -= 6 * mm
        c.line(10 * mm, y, width - 10 * mm, y)
        y -= 6 * mm

        c.setFont("Helvetica", 9)
        c.drawString(10 * mm, y, f"Bill No: {bill_no}")
        c.drawRightString(width - 10 * mm, y, f"Table: {self.order['table_no']}")
        y -= 5 * mm
        c.drawString(10 * mm, y, f"Waiter: {self.order['waiter_name']}")
        c.drawRightString(width - 10 * mm, y, utils.format_date())
        y -= 5 * mm
        c.drawString(10 * mm, y, f"Time: {utils.format_time()}")
        y -= 6 * mm
        c.line(10 * mm, y, width - 10 * mm, y)
        y -= 6 * mm

        c.setFont("Helvetica-Bold", 9)
        c.drawString(10 * mm, y, "Item")
        c.drawString(55 * mm, y, "Qty")
        c.drawString(68 * mm, y, "Price")
        c.drawRightString(width - 10 * mm, y, "Amount")
        y -= 5 * mm
        c.setFont("Helvetica", 9)
        for it in self.items:
            c.drawString(10 * mm, y, it["name"][:28])
            c.drawString(55 * mm, y, str(it["qty"]))
            c.drawString(68 * mm, y, f"{it['price']:.2f}")
            c.drawRightString(width - 10 * mm, y, f"{it['price'] * it['qty']:.2f}")
            y -= 5 * mm

        y -= 2 * mm
        c.line(10 * mm, y, width - 10 * mm, y)
        y -= 6 * mm

        gst_pct = self.gst_var.get()
        gst_amt = self.subtotal * gst_pct / 100.0
        discount = self.discount_var.get()

        for label, val in [
            ("Subtotal", self.subtotal),
            (f"GST ({gst_pct:.1f}%)", gst_amt),
            ("Discount", -discount),
        ]:
            c.setFont("Helvetica", 9)
            c.drawString(10 * mm, y, label)
            c.drawRightString(width - 10 * mm, y, f"{val:.2f}")
            y -= 5 * mm

        c.setFont("Helvetica-Bold", 11)
        c.drawString(10 * mm, y, "Grand Total")
        c.drawRightString(width - 10 * mm, y, utils.format_currency_pdf(self.grand_total))
        y -= 6 * mm
        c.setFont("Helvetica", 9)
        c.drawString(10 * mm, y, f"Payment Mode: {mode}")
        c.drawRightString(width - 10 * mm, y, f"Paid at {utils.format_time()}")
        y -= 8 * mm

        c.setFont("Helvetica-Oblique", 8)
        c.drawCentredString(width / 2, y, "Thank you for dining with us!")
        c.showPage()
        c.save()
        return path
