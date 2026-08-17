"""
kitchen.py
Kitchen Order Ticket (KOT) screen. New orders sent from the waiter's
Order Screen appear here automatically (polling refresh every 3s, since
Tkinter has no native push/socket channel). Staff progress each ticket
through Pending -> Preparing -> Ready.
"""

import tkinter as tk

import utils
from database import Database

STATUS_FLOW = ["pending", "preparing", "ready"]
STATUS_LABEL = {"pending": "Pending", "preparing": "Preparing", "ready": "Ready"}
STATUS_COLOR = {"pending": "warning", "preparing": "primary", "ready": "success"}


class KitchenWindow(tk.Toplevel):
    def __init__(self, parent):
        super().__init__(parent)
        self.parent = parent
        self.db = Database.instance()
        self.title(f"{utils.RESTAURANT_NAME} - Kitchen Display")
        utils.center_window(self, 1040, 660)
        t = utils.theme()
        self.configure(bg=t["bg"])
        utils.setup_ttk_style(self)

        top = tk.Frame(self, bg=t["surface"], height=60)
        top.pack(fill="x")
        top.pack_propagate(False)
        tk.Frame(self, bg=t["border"], height=1).pack(fill="x")
        tk.Label(top, text="👨‍🍳  Kitchen Order Tickets", font=utils.FONT_SUBTITLE, bg=t["surface"], fg=t["text"]).pack(side="left", padx=20)
        self.count_label = tk.Label(top, text="", font=utils.FONT_SMALL, bg=t["surface"], fg=t["muted"])
        self.count_label.pack(side="right", padx=20)

        self.canvas = tk.Canvas(self, bg=t["bg"], highlightthickness=0)
        scroll = tk.Scrollbar(self, orient="vertical", command=self.canvas.yview)
        self.grid_frame = tk.Frame(self.canvas, bg=t["bg"])
        self.grid_frame.bind("<Configure>", lambda e: self.canvas.configure(scrollregion=self.canvas.bbox("all")))
        self.canvas.create_window((0, 0), window=self.grid_frame, anchor="nw")
        self.canvas.configure(yscrollcommand=scroll.set)
        self.canvas.pack(side="left", fill="both", expand=True, padx=14, pady=14)
        scroll.pack(side="right", fill="y")

        self._refresh_kots()

    def _refresh_kots(self):
        if not self.winfo_exists():
            return
        for w in self.grid_frame.winfo_children():
            w.destroy()

        t = utils.theme()
        orders = list(self.db.orders.find({"status": {"$in": STATUS_FLOW}}).sort("kot_no", -1))
        self.count_label.config(text=f"{len(orders)} active ticket(s)")
        cols = 3
        for idx, order in enumerate(orders):
            r, c = divmod(idx, cols)
            color = t[STATUS_COLOR[order["status"]]]
            ticket = utils.card(self.grid_frame, accent=color, padx=0, pady=0)
            ticket.configure(width=300)
            ticket.grid(row=r, column=c, padx=8, pady=8, sticky="n")

            header = tk.Frame(ticket, bg=t["surface"], padx=12, pady=10)
            header.pack(fill="x")
            tk.Label(header, text=f"KOT #{order['kot_no']}", font=utils.FONT_SUBTITLE, bg=t["surface"], fg=t["text"]).pack(side="left")
            utils.Pill(header, STATUS_LABEL[order["status"]], color=color).pack(side="right")

            body = tk.Frame(ticket, bg=t["surface"], padx=12, pady=4)
            body.pack(fill="x")
            tk.Label(body, text=f"Table {order['table_no']}  ·  {order['waiter_name']}", font=utils.FONT_SMALL, bg=t["surface"], fg=t["muted"]).pack(anchor="w")
            tk.Label(body, text=f"{utils.format_date(order['createdAt'])}  {utils.format_time(order['createdAt'])}",
                     font=utils.FONT_TINY, bg=t["surface"], fg=t["muted"]).pack(anchor="w", pady=(0, 8))
            tk.Frame(body, bg=t["border"], height=1).pack(fill="x", pady=(0, 8))

            items = list(self.db.order_items.find({"order_id": order["_id"]}))
            for it in items:
                row = tk.Frame(body, bg=t["surface"])
                row.pack(fill="x", pady=1)
                tk.Label(row, text=it["name"], font=utils.FONT_SMALL, bg=t["surface"], fg=t["text"], anchor="w").pack(side="left")
                tk.Label(row, text=f"×{it['qty']}", font=utils.FONT_SMALL, bg=t["surface"], fg=t["primary"]).pack(side="right")

            btn_row = tk.Frame(ticket, bg=t["surface"], padx=12, pady=10)
            btn_row.pack(fill="x")
            self._add_status_buttons(btn_row, order)

        if not orders:
            tk.Label(self.grid_frame, text="No active kitchen tickets.", font=utils.FONT_NORMAL, bg=t["bg"], fg=t["muted"]).pack(pady=40)

        self.after(3000, self._refresh_kots)

    def _add_status_buttons(self, parent, order):
        t = utils.theme()
        current = order["status"]

        def advance(new_status):
            update = {"status": new_status, "updatedAt": utils.now()}
            if new_status == "ready":
                update["notified"] = False
            self.db.orders.update_one({"_id": order["_id"]}, {"$set": update})
            self._refresh_kots()

        if current == "pending":
            utils.make_round_button(parent, "Accept", lambda: advance("preparing"), bg=t["primary"], padx=8, pady=6, font=utils.FONT_SMALL, height=32).pack(side="left", padx=3)
        if current in ("pending", "preparing"):
            utils.make_round_button(parent, "Preparing", lambda: advance("preparing"), bg=t["warning"], fg="#1E1E1E", padx=8, pady=6, font=utils.FONT_SMALL, height=32).pack(side="left", padx=3)
        if current in ("pending", "preparing"):
            utils.make_round_button(parent, "Ready", lambda: advance("ready"), bg=t["success"], padx=8, pady=6, font=utils.FONT_SMALL, height=32).pack(side="left", padx=3)
        if current == "ready":
            tk.Label(parent, text="✔ Ready for pickup", bg=t["surface"], fg=t["success"], font=utils.FONT_SMALL).pack(side="left", padx=4)
