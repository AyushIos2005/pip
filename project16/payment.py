"""
payment.py
Payment dialog: Cash / UPI / Card. For UPI, a QR code is generated
dynamically encoding a standard `upi://pay` deep link with the amount.
"""

import io
import tkinter as tk

import utils

try:
    import qrcode
    from PIL import ImageTk
    QR_OK = True
except ImportError:
    QR_OK = False


class PaymentDialog(tk.Toplevel):
    def __init__(self, parent, amount, on_success):
        super().__init__(parent)
        self.parent = parent
        self.amount = amount
        self.on_success = on_success
        self.title("Payment")
        utils.center_window(self, 400, 500)
        self.resizable(False, False)
        self.grab_set()
        t = utils.theme()
        self.configure(bg=t["bg"])
        utils.setup_ttk_style(self)
        self.mode_var = tk.StringVar(value="Cash")
        self.qr_label = None
        self._build_ui()

    def _build_ui(self):
        t = utils.theme()
        outer = utils.card(self, padx=0, pady=0)
        outer.pack(fill="both", expand=True, padx=14, pady=14)
        card = tk.Frame(outer, bg=t["surface"], padx=20, pady=20)
        card.pack(fill="both", expand=True)

        tk.Label(card, text="Select Payment Mode", font=utils.FONT_SUBTITLE, bg=t["surface"], fg=t["text"]).pack(anchor="w")
        amount_card = tk.Frame(card, bg=t["primary_soft"], pady=10)
        amount_card.pack(fill="x", pady=10)
        tk.Label(amount_card, text=utils.format_currency(self.amount), font=utils.FONT_TITLE, bg=t["primary_soft"], fg=t["primary"]).pack()

        seg = utils.segmented(card, ["Cash", "UPI", "Card"], self.mode_var, command=lambda m: self._on_mode_change(), width=100)
        seg.pack(fill="x", pady=8)

        self.qr_frame = tk.Frame(card, bg=t["surface"], height=190)
        self.qr_frame.pack(fill="x", pady=10)

        utils.make_round_button(card, "Confirm Payment", self.confirm, bg=t["success"], icon="✓", height=42).pack(fill="x", pady=(10, 6))
        utils.make_round_button(card, "Cancel", self.destroy, variant="ghost", fg=t["muted"], height=36).pack(fill="x")

    def _on_mode_change(self):
        for w in self.qr_frame.winfo_children():
            w.destroy()
        if self.mode_var.get() != "UPI":
            return
        t = utils.theme()
        if not QR_OK:
            tk.Label(self.qr_frame, text="Install 'qrcode' and 'pillow' to show a QR code.",
                     bg=t["surface"], fg=t["danger"], font=utils.FONT_SMALL, wraplength=300).pack()
            return

        upi_link = f"upi://pay?pa={utils.UPI_ID}&pn={utils.RESTAURANT_NAME.replace(' ', '%20')}&am={self.amount:.2f}&cu=INR"
        img = qrcode.make(upi_link)
        buf = io.BytesIO()
        img.save(buf, format="PNG")
        buf.seek(0)
        from PIL import Image
        pil_img = Image.open(buf).resize((160, 160))
        self._qr_photo = ImageTk.PhotoImage(pil_img)
        qr_card = tk.Frame(self.qr_frame, bg=t["surface_alt"], padx=12, pady=12)
        qr_card.pack()
        tk.Label(qr_card, image=self._qr_photo, bg=t["surface_alt"]).pack()
        tk.Label(self.qr_frame, text=f"Scan to pay {utils.UPI_ID}", font=utils.FONT_SMALL, bg=t["surface"], fg=t["muted"]).pack(pady=6)

    def confirm(self):
        mode = self.mode_var.get()
        self.destroy()
        self.on_success(mode)
