"""
menu.py
Order screen: category chips + menu grid on the left, live cart on the
right. Opened when a waiter clicks a table on the dashboard.
"""

import tkinter as tk
from tkinter import messagebox
import os

import utils
import models
from database import Database

try:
    from PIL import Image, ImageTk
    PIL_OK = True
except ImportError:
    PIL_OK = False

CATEGORIES = ["All", "Beverages", "North Indian", "South Indian", "Chinese", "Italian", "Desserts"]


class OrderWindow(tk.Toplevel):
    def __init__(self, parent, table_no, user):
        super().__init__(parent)
        self.parent = parent
        self.table_no = table_no
        self.user = user
        self.db = Database.instance()
        self.title(f"Table {table_no} - Order")
        utils.center_window(self, 1140, 700)
        self.minsize(980, 620)
        t = utils.theme()
        self.configure(bg=t["bg"])
        utils.setup_ttk_style(self)

        self.cart = {}  # menu_item_id(str) -> {"item": doc, "qty": int}
        self.qty_vars = {}
        self.current_category = "All"

        self._load_existing_order()
        self._build_ui()
        self._render_menu()
        self._render_cart()

    # ------------------------------------------------------------------ #
    def _load_existing_order(self):
        """If this table already has an open order, resume it (existing cart)."""
        self.order = self.db.orders.find_one({
            "table_no": self.table_no,
            "status": {"$in": ["pending", "preparing", "ready"]},
        })
        if self.order:
            items = self.db.order_items.find({"order_id": self.order["_id"]})
            for it in items:
                self.cart[str(it["menu_item_id"])] = {
                    "item": {"_id": it["menu_item_id"], "name": it["name"], "price": it["price"]},
                    "qty": it["qty"],
                }

    # ------------------------------------------------------------------ #
    def _build_ui(self):
        t = utils.theme()
        top = tk.Frame(self, bg=t["surface"], height=60)
        top.pack(fill="x")
        top.pack_propagate(False)
        tk.Frame(self, bg=t["border"], height=1).pack(fill="x")

        left_top = tk.Frame(top, bg=t["surface"])
        left_top.pack(side="left", padx=18)
        tk.Label(left_top, text=f"Table {self.table_no}", font=utils.FONT_SUBTITLE, bg=t["surface"], fg=t["text"]).pack(anchor="w")
        tk.Label(left_top, text=f"Waiter · {self.user['full_name']}", font=utils.FONT_TINY, bg=t["surface"], fg=t["muted"]).pack(anchor="w")

        search_wrap, self.search_entry = utils.entry_field(top, font=utils.FONT_NORMAL)
        search_wrap.pack(side="right", padx=18, pady=12, ipadx=2)
        self.search_var = tk.StringVar()
        self.search_entry.configure(textvariable=self.search_var, width=22)
        self.search_entry.bind("<KeyRelease>", lambda e: self._render_menu())
        # placeholder-ish label
        tk.Label(top, text="🔍", bg=t["surface"], fg=t["muted"], font=utils.FONT_NORMAL).pack(side="right", pady=12)

        body = tk.Frame(self, bg=t["bg"])
        body.pack(fill="both", expand=True)

        # ---- Left: categories + menu grid ----
        left = tk.Frame(body, bg=t["bg"])
        left.pack(side="left", fill="both", expand=True, padx=(16, 8), pady=16)

        cat_bar = tk.Frame(left, bg=t["bg"])
        cat_bar.pack(fill="x", pady=(0, 12))
        self.cat_buttons = {}
        for cat in CATEGORIES:
            active = cat == "All"
            b = utils.make_round_button(
                cat_bar, cat, lambda c=cat: self._select_category(c),
                bg=t["primary"] if active else t["surface_alt"],
                fg="white" if active else t["muted"],
                variant="solid", radius=16, padx=14, pady=7, font=utils.FONT_SMALL,
            )
            b.pack(side="left", padx=3)
            self.cat_buttons[cat] = b

        canvas_wrap = tk.Frame(left, bg=t["bg"])
        canvas_wrap.pack(fill="both", expand=True)
        self.canvas = tk.Canvas(canvas_wrap, bg=t["bg"], highlightthickness=0)
        scroll = tk.Scrollbar(canvas_wrap, orient="vertical", command=self.canvas.yview)
        self.menu_frame = tk.Frame(self.canvas, bg=t["bg"])
        self.menu_frame.bind("<Configure>", lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")))
        self.canvas.create_window((0, 0), window=self.menu_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=scroll.set)
        self.canvas.pack(side="left", fill="both", expand=True)
        scroll.pack(side="right", fill="y")
        self.canvas.bind_all("<MouseWheel>", lambda e: self.canvas.yview_scroll(int(-e.delta / 120), "units"))

        # ---- Right: cart ----
        right = utils.card(body, padx=0, pady=0)
        right.configure(width=340)
        right.pack(side="right", fill="y", padx=(8, 16), pady=16)
        right.pack_propagate(False)

        # NOTE: the bottom action bar (total + buttons) is packed with
        # side="bottom" BEFORE the scrollable cart list. In tkinter, pack()
        # reserves space in the order widgets are packed, regardless of
        # side — so packing it first guarantees it always gets its slice of
        # height. Packing it last (as before) let the expand=True cart
        # canvas claim all the space first, squeezing the total/buttons
        # down to zero height (they existed, just invisible).
        bottom = tk.Frame(right, bg=t["surface"])
        bottom.pack(fill="x", side="bottom", padx=16, pady=16)
        tk.Frame(bottom, bg=t["border"], height=1).pack(fill="x", pady=(0, 12))

        self.total_label = tk.Label(bottom, text="Total: ₹0.00", font=utils.FONT_TITLE, bg=t["surface"], fg=t["primary"])
        self.total_label.pack(anchor="w", pady=(0, 12))

        utils.make_round_button(bottom, "Send to Kitchen", self.send_to_kitchen, bg=t["success"], icon="👨‍🍳", height=40).pack(fill="x", pady=3)
        utils.make_round_button(bottom, "Save Order", self.save_order, bg=t["primary"], height=40).pack(fill="x", pady=3)
        utils.make_round_button(bottom, "Generate Bill", self.generate_bill, bg=t["accent"], fg="#1E1E1E", height=40).pack(fill="x", pady=3)
        utils.make_round_button(bottom, "Clear Cart", self.clear_cart, variant="ghost", fg=t["danger"], height=36).pack(fill="x", pady=3)

        cart_head = tk.Frame(right, bg=t["surface"])
        cart_head.pack(fill="x", padx=16, pady=(16, 8))
        tk.Label(cart_head, text="🛒  Current Order", font=utils.FONT_SUBTITLE, bg=t["surface"], fg=t["text"]).pack(anchor="w")
        tk.Frame(right, bg=t["border"], height=1).pack(fill="x", padx=16)

        self.cart_canvas = tk.Canvas(right, bg=t["surface"], highlightthickness=0)
        cart_scroll = tk.Scrollbar(right, orient="vertical", command=self.cart_canvas.yview)
        self.cart_items_frame = tk.Frame(self.cart_canvas, bg=t["surface"])
        self.cart_items_frame.bind("<Configure>", lambda e: self.cart_canvas.configure(scrollregion=self.cart_canvas.bbox("all")))
        self.cart_canvas.create_window((0, 0), window=self.cart_items_frame, anchor="nw", width=300)
        self.cart_canvas.configure(yscrollcommand=cart_scroll.set)
        self.cart_canvas.pack(side="left", fill="both", expand=True, padx=(16, 0), pady=8)
        cart_scroll.pack(side="left", fill="y", pady=8)

    def _select_category(self, cat):
        t = utils.theme()
        self.current_category = cat
        for c, b in self.cat_buttons.items():
            active = c == cat
            b.bg_normal = t["primary"] if active else t["surface_alt"]
            b.bg_hover = utils.mix(b.bg_normal, "#000000", 0.12)
            b.bg_press = utils.mix(b.bg_normal, "#000000", 0.22)
            b.fg_color = "white" if active else t["muted"]
            b._draw(b.bg_normal)
        self._render_menu()

    # ------------------------------------------------------------------ #
    def _render_menu(self):
        for w in self.menu_frame.winfo_children():
            w.destroy()

        t = utils.theme()
        query = {"status": "active"}
        if self.current_category != "All":
            query["category"] = self.current_category
        search = self.search_var.get().strip()
        if search:
            query["name"] = {"$regex": search, "$options": "i"}

        items = list(self.db.menu.find(query).sort("name", 1))
        cols = 3
        for idx, item in enumerate(items):
            r, c = divmod(idx, cols)
            outer = utils.card(self.menu_frame, padx=0, pady=0)
            outer.configure(width=224, height=210)
            outer.grid(row=r, column=c, padx=8, pady=8)
            outer.pack_propagate(False)

            img_shown = False
            if PIL_OK and item.get("image_path") and os.path.exists(item["image_path"]):
                try:
                    img = Image.open(item["image_path"]).resize((72, 72))
                    photo = ImageTk.PhotoImage(img)
                    lbl = tk.Label(outer, image=photo, bg=t["surface"])
                    lbl.image = photo
                    lbl.pack(pady=(14, 4))
                    img_shown = True
                except Exception:
                    img_shown = False
            if not img_shown:
                ph = tk.Canvas(outer, width=56, height=56, bg=t["surface"], highlightthickness=0, bd=0)
                ph.pack(pady=(14, 6))
                ph.create_oval(2, 2, 54, 54, fill=t["primary_soft"], outline="")
                ph.create_text(28, 28, text=item["name"][:2].upper(), font=("Segoe UI", 15, "bold"), fill=t["primary"])

            tk.Label(outer, text=item["name"], font=utils.FONT_NORMAL, bg=t["surface"], fg=t["text"], wraplength=195).pack()
            tk.Label(outer, text=utils.format_currency(item["price"]), font=utils.FONT_SMALL, bg=t["surface"], fg=t["muted"]).pack(pady=(0, 8))

            qty_frame = tk.Frame(outer, bg=t["surface"])
            qty_frame.pack()
            key = f"new_{item['_id']}"
            self.qty_vars[key] = tk.IntVar(value=1)
            utils.make_round_button(qty_frame, "–", lambda k=key: self._bump(k, -1), variant="outline",
                                     width=28, height=28, radius=8, font=utils.FONT_SMALL, padx=0, pady=0).pack(side="left")
            tk.Label(qty_frame, textvariable=self.qty_vars[key], width=3, bg=t["surface"], fg=t["text"], font=utils.FONT_SMALL).pack(side="left")
            utils.make_round_button(qty_frame, "+", lambda k=key: self._bump(k, 1), variant="outline",
                                     width=28, height=28, radius=8, font=utils.FONT_SMALL, padx=0, pady=0).pack(side="left")

            utils.make_round_button(
                outer, "Add to Cart", lambda it=item, k=key: self._add_to_cart(it, k),
                bg=t["primary"], padx=8, pady=6, font=utils.FONT_SMALL, height=32
            ).pack(pady=(8, 12))

    def _bump(self, key, delta):
        var = self.qty_vars[key]
        var.set(max(1, var.get() + delta))

    def _add_to_cart(self, item, key):
        qty = self.qty_vars[key].get()
        item_id = str(item["_id"])
        if item_id in self.cart:
            self.cart[item_id]["qty"] += qty
        else:
            self.cart[item_id] = {"item": item, "qty": qty}
        self._render_cart()

    # ------------------------------------------------------------------ #
    def _render_cart(self):
        for w in self.cart_items_frame.winfo_children():
            w.destroy()
        t = utils.theme()
        total = 0.0
        if not self.cart:
            tk.Label(self.cart_items_frame, text="Cart is empty.\nAdd items from the menu.",
                      font=utils.FONT_SMALL, bg=t["surface"], fg=t["muted"], justify="left").pack(anchor="w", pady=20)
        for item_id, data in self.cart.items():
            item, qty = data["item"], data["qty"]
            line_total = item["price"] * qty
            total += line_total

            row = tk.Frame(self.cart_items_frame, bg=t["surface_alt"], pady=8, padx=8)
            row.pack(fill="x", pady=4)
            tk.Label(row, text=item["name"], font=utils.FONT_SMALL, bg=t["surface_alt"], fg=t["text"], wraplength=150, anchor="w").pack(anchor="w")
            sub = tk.Frame(row, bg=t["surface_alt"])
            sub.pack(fill="x", pady=(6, 0))
            utils.make_round_button(sub, "–", lambda k=item_id: self._cart_qty(k, -1), variant="outline",
                                     width=24, height=24, radius=7, font=utils.FONT_TINY, padx=0, pady=0).pack(side="left")
            tk.Label(sub, text=str(qty), width=3, bg=t["surface_alt"], fg=t["text"], font=utils.FONT_SMALL).pack(side="left")
            utils.make_round_button(sub, "+", lambda k=item_id: self._cart_qty(k, 1), variant="outline",
                                     width=24, height=24, radius=7, font=utils.FONT_TINY, padx=0, pady=0).pack(side="left")
            tk.Label(sub, text=utils.format_currency(line_total), font=utils.FONT_SMALL, bg=t["surface_alt"], fg=t["muted"]).pack(side="left", padx=8)
            utils.make_round_button(sub, "✕", lambda k=item_id: self._remove_item(k), variant="ghost", fg=t["danger"],
                                     width=24, height=24, radius=7, font=utils.FONT_TINY, padx=0, pady=0).pack(side="right")

        self.total_label.config(text=f"Total: {utils.format_currency(total)}")
        self.cart_total = total

    def _cart_qty(self, item_id, delta):
        if item_id not in self.cart:
            return
        self.cart[item_id]["qty"] += delta
        if self.cart[item_id]["qty"] <= 0:
            del self.cart[item_id]
        self._render_cart()

    def _remove_item(self, item_id):
        self.cart.pop(item_id, None)
        self._render_cart()

    def clear_cart(self):
        if messagebox.askyesno("Clear Cart", "Remove all items from the cart?"):
            self.cart.clear()
            self._render_cart()

    # ------------------------------------------------------------------ #
    def _persist_order(self, status):
        """Create or update the order + order_items documents."""
        if not self.cart:
            messagebox.showwarning("Empty Cart", "Add at least one item before saving.")
            return None

        if self.order is None:
            kot_no = self.db.next_sequence("kot")
            order_doc = models.new_order_doc(self.table_no, self.user["_id"], self.user["full_name"], kot_no)
            order_doc["status"] = status
            result = self.db.orders.insert_one(order_doc)
            self.order = self.db.orders.find_one({"_id": result.inserted_id})
        else:
            self.db.orders.update_one({"_id": self.order["_id"]}, {"$set": {"status": status, "updatedAt": utils.now()}})

        # Replace order_items with current cart contents
        self.db.order_items.delete_many({"order_id": self.order["_id"]})
        docs = [
            models.new_order_item_doc(self.order["_id"], data["item"]["_id"], data["item"]["name"], data["item"]["price"], data["qty"])
            for data in self.cart.values()
        ]
        if docs:
            self.db.order_items.insert_many(docs)

        self.db.tables.update_one(
            {"table_no": self.table_no},
            {"$set": {"status": "occupied", "current_order_id": self.order["_id"], "updatedAt": utils.now()}},
        )
        return self.order

    def save_order(self):
        order = self._persist_order(self.order["status"] if self.order else "pending")
        if order:
            messagebox.showinfo("Saved", "Order saved successfully.")

    def send_to_kitchen(self):
        order = self._persist_order("pending")
        if order:
            messagebox.showinfo("Sent", f"Order sent to kitchen (KOT #{order['kot_no']}).")
            if hasattr(self.parent, "_refresh_tables"):
                self.parent._refresh_tables()

    def generate_bill(self):
        order = self._persist_order(self.order["status"] if self.order else "pending")
        if not order:
            return
        from billing import BillingWindow
        BillingWindow(self, order)