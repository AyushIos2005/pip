"""
admin.py
Admin panel: menu CRUD, sales overview, best sellers, bill/order search,
waiter performance and access to detailed reports.
"""

import tkinter as tk
from tkinter import ttk, messagebox
import datetime

import utils
import models
from database import Database
from menu import CATEGORIES


class AdminPanel(tk.Toplevel):
    def __init__(self, parent, user):
        super().__init__(parent)
        self.parent = parent
        self.user = user
        self.db = Database.instance()
        self.title(f"{utils.RESTAURANT_NAME} - Admin Panel")
        utils.center_window(self, 1080, 700)
        t = utils.theme()
        self.configure(bg=t["bg"])
        utils.setup_ttk_style(self)

        header = tk.Frame(self, bg=t["surface"], height=56)
        header.pack(fill="x")
        header.pack_propagate(False)
        tk.Frame(self, bg=t["border"], height=1).pack(fill="x")
        tk.Label(header, text="⚙  Admin Panel", font=utils.FONT_SUBTITLE, bg=t["surface"], fg=t["text"]).pack(side="left", padx=20)

        nb = ttk.Notebook(self)
        nb.pack(fill="both", expand=True, padx=12, pady=12)

        self.menu_tab = tk.Frame(nb, bg=t["bg"])
        self.sales_tab = tk.Frame(nb, bg=t["bg"])
        self.search_tab = tk.Frame(nb, bg=t["bg"])
        self.perf_tab = tk.Frame(nb, bg=t["bg"])
        self.customers_tab = tk.Frame(nb, bg=t["bg"])
        self.feedback_tab = tk.Frame(nb, bg=t["bg"])

        nb.add(self.menu_tab, text="  Menu Management  ")
        nb.add(self.sales_tab, text="  Sales Overview  ")
        nb.add(self.search_tab, text="  Search Bills / Orders  ")
        nb.add(self.perf_tab, text="  Waiter Performance  ")
        nb.add(self.customers_tab, text="  👥 Customers  ")
        nb.add(self.feedback_tab, text="  ⭐ Feedback Analytics  ")

        self._build_menu_tab()
        self._build_sales_tab()
        self._build_search_tab()
        self._build_perf_tab()
        self._build_customers_tab()
        self._build_feedback_tab()

    # ------------------------------------------------------------------ #
    # Menu Management
    # ------------------------------------------------------------------ #
    def _build_menu_tab(self):
        t = utils.theme()
        left = tk.Frame(self.menu_tab, bg=t["bg"])
        left.pack(side="left", fill="both", expand=True, padx=(8, 6), pady=8)

        cols = ("name", "price", "category", "status")
        self.menu_tree = ttk.Treeview(left, columns=cols, show="headings", height=20)
        for c in cols:
            self.menu_tree.heading(c, text=c.title())
            self.menu_tree.column(c, width=120)
        self.menu_tree.pack(fill="both", expand=True)
        self.menu_tree.bind("<<TreeviewSelect>>", self._on_menu_select)

        right_outer = utils.card(self.menu_tab, padx=0, pady=0)
        right_outer.configure(width=290)
        right_outer.pack(side="right", fill="y", padx=(6, 8), pady=8)
        right_outer.pack_propagate(False)
        right = tk.Frame(right_outer, bg=t["surface"], padx=16, pady=16)
        right.pack(fill="both", expand=True)

        tk.Label(right, text="Item Details", font=utils.FONT_SUBTITLE, bg=t["surface"], fg=t["text"]).pack(anchor="w", pady=(0, 10))

        tk.Label(right, text="ITEM NAME", bg=t["surface"], fg=t["muted"], font=utils.FONT_TINY).pack(anchor="w")
        self.name_var = tk.StringVar()
        w, _ = utils.entry_field(right, textvariable=self.name_var)
        w.pack(fill="x", pady=(2, 10))

        tk.Label(right, text="PRICE (₹)", bg=t["surface"], fg=t["muted"], font=utils.FONT_TINY).pack(anchor="w")
        self.price_var = tk.DoubleVar(value=0.0)
        w, _ = utils.entry_field(right, textvariable=self.price_var)
        w.pack(fill="x", pady=(2, 10))

        tk.Label(right, text="CATEGORY", bg=t["surface"], fg=t["muted"], font=utils.FONT_TINY).pack(anchor="w")
        self.category_var = tk.StringVar(value=CATEGORIES[1])
        ttk.Combobox(right, textvariable=self.category_var, values=CATEGORIES[1:], state="readonly").pack(fill="x", pady=(2, 10), ipady=4)

        tk.Label(right, text="IMAGE PATH (OPTIONAL)", bg=t["surface"], fg=t["muted"], font=utils.FONT_TINY).pack(anchor="w")
        self.image_var = tk.StringVar()
        w, _ = utils.entry_field(right, textvariable=self.image_var)
        w.pack(fill="x", pady=(2, 16))

        utils.make_round_button(right, "Add Item", self.add_menu_item, bg=t["success"], height=36).pack(fill="x", pady=3)
        utils.make_round_button(right, "Update Selected", self.update_menu_item, bg=t["primary"], height=36).pack(fill="x", pady=3)
        utils.make_round_button(right, "Delete Selected", self.delete_menu_item, bg=t["danger"], height=36).pack(fill="x", pady=3)
        utils.make_round_button(right, "Clear Form", self.clear_menu_form, variant="ghost", fg=t["muted"], height=32).pack(fill="x", pady=3)

        self._selected_item_id = None
        self._refresh_menu_tree()

    def _refresh_menu_tree(self):
        for row in self.menu_tree.get_children():
            self.menu_tree.delete(row)
        for item in self.db.menu.find().sort("name", 1):
            self.menu_tree.insert("", "end", iid=str(item["_id"]),
                                   values=(item["name"], f"{item['price']:.2f}", item["category"], item["status"]))

    def _on_menu_select(self, event):
        sel = self.menu_tree.selection()
        if not sel:
            return
        item_id = sel[0]
        import bson
        item = self.db.menu.find_one({"_id": bson.ObjectId(item_id)})
        if item:
            self._selected_item_id = item["_id"]
            self.name_var.set(item["name"])
            self.price_var.set(item["price"])
            self.category_var.set(item["category"])
            self.image_var.set(item.get("image_path", ""))

    def add_menu_item(self):
        if not self.name_var.get().strip():
            messagebox.showwarning("Missing", "Enter an item name.")
            return
        doc = models.new_menu_item_doc(self.name_var.get().strip(), self.price_var.get(),
                                        self.category_var.get(), self.image_var.get().strip())
        self.db.menu.insert_one(doc)
        self.clear_menu_form()
        self._refresh_menu_tree()

    def update_menu_item(self):
        if not self._selected_item_id:
            messagebox.showwarning("No selection", "Select an item to update.")
            return
        self.db.menu.update_one({"_id": self._selected_item_id}, {"$set": {
            "name": self.name_var.get().strip(), "price": float(self.price_var.get()),
            "category": self.category_var.get(), "image_path": self.image_var.get().strip(),
            "updatedAt": utils.now(),
        }})
        self._refresh_menu_tree()

    def delete_menu_item(self):
        if not self._selected_item_id:
            messagebox.showwarning("No selection", "Select an item to delete.")
            return
        if messagebox.askyesno("Confirm", "Delete this menu item?"):
            self.db.menu.update_one({"_id": self._selected_item_id}, {"$set": {"status": "inactive", "updatedAt": utils.now()}})
            self.clear_menu_form()
            self._refresh_menu_tree()

    def clear_menu_form(self):
        self._selected_item_id = None
        self.name_var.set("")
        self.price_var.set(0.0)
        self.category_var.set(CATEGORIES[1])
        self.image_var.set("")

    # ------------------------------------------------------------------ #
    # Sales Overview
    # ------------------------------------------------------------------ #
    def _build_sales_tab(self):
        t = utils.theme()
        top = tk.Frame(self.sales_tab, bg=t["bg"])
        top.pack(fill="x", padx=8, pady=8)

        today = datetime.datetime.now().replace(hour=0, minute=0, second=0, microsecond=0)
        month_start = today.replace(day=1)

        today_total = sum(s["amount"] for s in self.db.sales.find({"createdAt": {"$gte": today}, "status": "completed"}))
        month_total = sum(s["amount"] for s in self.db.sales.find({"createdAt": {"$gte": month_start}, "status": "completed"}))

        for label, value, color in [("Today's Sales", today_total, t["primary"]), ("Monthly Sales", month_total, t["success"])]:
            box_outer = utils.card(top, accent=color, padx=0, pady=0)
            box_outer.pack(side="left", padx=6)
            box = tk.Frame(box_outer, bg=t["surface"], padx=22, pady=14)
            box.pack()
            tk.Label(box, text=label, font=utils.FONT_SMALL, bg=t["surface"], fg=t["muted"]).pack()
            tk.Label(box, text=utils.format_currency(value), font=utils.FONT_TITLE, bg=t["surface"], fg=t["text"]).pack()

        tk.Label(top, text="", bg=t["bg"]).pack(side="left", expand=True, fill="x")
        for label in ("Daily", "Weekly", "Monthly", "Yearly"):
            utils.make_round_button(top, label, lambda p=label: self.open_report(p), variant="outline", padx=12, pady=8).pack(side="left", padx=3)

        utils.section_header(self.sales_tab, "Best Selling Items", icon="🏆").pack(anchor="w", fill="x", padx=8, pady=(14, 8))
        cols = ("name", "qty")
        tree = ttk.Treeview(self.sales_tab, columns=cols, show="headings", height=10)
        tree.heading("name", text="Item")
        tree.heading("qty", text="Qty Sold")
        tree.pack(fill="x", padx=8)
        from reports import get_best_sellers
        for row in get_best_sellers():
            tree.insert("", "end", values=(row["_id"], row["qty"]))

    def open_report(self, period):
        from reports import ReportWindow
        ReportWindow(self, period)

    # ------------------------------------------------------------------ #
    # Search Bills / Orders
    # ------------------------------------------------------------------ #
    def _build_search_tab(self):
        t = utils.theme()
        top = tk.Frame(self.search_tab, bg=t["bg"])
        top.pack(fill="x", padx=8, pady=8)

        tk.Label(top, text="Table No", bg=t["bg"], font=utils.FONT_SMALL, fg=t["muted"]).pack(side="left")
        self.search_table_var = tk.StringVar()
        w, e = utils.entry_field(top, textvariable=self.search_table_var)
        w.pack(side="left", padx=6)
        e.configure(width=6)

        tk.Label(top, text="Waiter", bg=t["bg"], font=utils.FONT_SMALL, fg=t["muted"]).pack(side="left", padx=(14, 0))
        self.search_waiter_var = tk.StringVar()
        w, e = utils.entry_field(top, textvariable=self.search_waiter_var)
        w.pack(side="left", padx=6)
        e.configure(width=16)

        utils.make_round_button(top, "Search", self._run_search, bg=t["primary"], padx=14, pady=8).pack(side="left", padx=12)

        cols = ("bill_no", "table_no", "waiter_name", "amount", "mode", "paid_at")
        self.search_tree = ttk.Treeview(self.search_tab, columns=cols, show="headings", height=20)
        for c in cols:
            self.search_tree.heading(c, text=c.replace("_", " ").title())
            self.search_tree.column(c, width=130)
        self.search_tree.pack(fill="both", expand=True, padx=8, pady=8)
        self._run_search()

    def _run_search(self):
        for row in self.search_tree.get_children():
            self.search_tree.delete(row)
        query = {}
        if self.search_table_var.get().strip():
            try:
                query["table_no"] = int(self.search_table_var.get().strip())
            except ValueError:
                pass
        if self.search_waiter_var.get().strip():
            query["waiter_name"] = {"$regex": self.search_waiter_var.get().strip(), "$options": "i"}

        for p in self.db.payments.find(query).sort("paid_at", -1).limit(200):
            self.search_tree.insert("", "end", values=(
                p["bill_no"], p["table_no"], p["waiter_name"],
                utils.format_currency(p["amount"]), p["mode"], utils.format_datetime(p["paid_at"]),
            ))

    # ------------------------------------------------------------------ #
    # Waiter Performance
    # ------------------------------------------------------------------ #
    def _build_perf_tab(self):
        t = utils.theme()
        utils.section_header(self.perf_tab, "Waiter Performance", icon="📈").pack(anchor="w", fill="x", padx=8, pady=8)
        cols = ("waiter", "orders", "total_sales")
        tree = ttk.Treeview(self.perf_tab, columns=cols, show="headings", height=20)
        tree.heading("waiter", text="Waiter")
        tree.heading("orders", text="Orders")
        tree.heading("total_sales", text="Total Sales")
        tree.pack(fill="both", expand=True, padx=8, pady=8)
        from reports import get_waiter_performance
        for row in get_waiter_performance():
            tree.insert("", "end", values=(row["_id"], row["orders"], utils.format_currency(row["total_sales"])))

    # ------------------------------------------------------------------ #
    # Customers / Feedback Analytics
    # ------------------------------------------------------------------ #
    def _build_customers_tab(self):
        from customer_admin import build_customers_tab
        build_customers_tab(self, self.customers_tab)

    def _build_feedback_tab(self):
        from customer_admin import build_feedback_tab
        build_feedback_tab(self, self.feedback_tab)
