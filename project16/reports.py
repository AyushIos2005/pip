"""
reports.py
Sales aggregation helpers + a Matplotlib chart window, plus PDF / Excel
export of the currently displayed report.
"""

import os
import datetime
import tkinter as tk
from tkinter import messagebox

import utils
from database import Database

import matplotlib
matplotlib.use("TkAgg")
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

from reportlab.lib.pagesizes import A4
from reportlab.lib.units import mm
from reportlab.pdfgen import canvas as pdfcanvas

try:
    import openpyxl
    XLSX_OK = True
except ImportError:
    XLSX_OK = False

PERIODS = {
    "Daily": 1,
    "Weekly": 7,
    "Monthly": 30,
    "Yearly": 365,
}


def _date_bucket_format(period):
    return "%d-%b" if period in ("Daily", "Weekly") else "%b-%Y" if period == "Yearly" else "%d-%b"


def get_sales_data(period="Daily"):
    db = Database.instance()
    days = PERIODS.get(period, 1)
    since = datetime.datetime.now() - datetime.timedelta(days=days)
    fmt = _date_bucket_format(period)

    sales = list(db.sales.find({"createdAt": {"$gte": since}, "status": "completed"}))
    buckets = {}
    for s in sales:
        key = s["createdAt"].strftime(fmt)
        buckets[key] = buckets.get(key, 0.0) + s["amount"]
    return buckets, sales


def get_best_sellers(limit=10):
    db = Database.instance()
    pipeline = [
        {"$group": {"_id": "$name", "qty": {"$sum": "$qty"}}},
        {"$sort": {"qty": -1}},
        {"$limit": limit},
    ]
    return list(db.order_items.aggregate(pipeline))


def get_waiter_performance():
    db = Database.instance()
    pipeline = [
        {"$match": {"status": "completed"}},
        {"$group": {"_id": "$waiter_name", "total_sales": {"$sum": "$amount"}, "orders": {"$sum": 1}}},
        {"$sort": {"total_sales": -1}},
    ]
    return list(db.sales.aggregate(pipeline))


class ReportWindow(tk.Toplevel):
    def __init__(self, parent, period="Daily"):
        super().__init__(parent)
        self.period = period
        self.title(f"{period} Sales Report")
        utils.center_window(self, 780, 600)
        t = utils.theme()
        self.configure(bg=t["bg"])
        utils.setup_ttk_style(self)

        header = tk.Frame(self, bg=t["surface"], height=54)
        header.pack(fill="x")
        header.pack_propagate(False)
        tk.Frame(self, bg=t["border"], height=1).pack(fill="x")
        tk.Label(header, text=f"📊  {period} Sales Report", font=utils.FONT_SUBTITLE, bg=t["surface"], fg=t["text"]).pack(side="left", padx=18)

        top = tk.Frame(self, bg=t["bg"])
        top.pack(fill="x", padx=14, pady=12)

        for label in ("Daily", "Weekly", "Monthly", "Yearly"):
            active = label == self.period
            utils.make_round_button(top, label, lambda p=label: self._switch_period(p),
                                     bg=t["primary"] if active else t["surface_alt"],
                                     fg="white" if active else t["muted"],
                                     padx=12, pady=8, radius=16).pack(side="left", padx=3)

        utils.make_round_button(top, "Export Excel", self.export_excel, bg=t["success"], icon="📥", padx=12, pady=8).pack(side="right", padx=3)
        utils.make_round_button(top, "Export PDF", self.export_pdf, bg=t["accent"], fg="#1E1E1E", icon="📄", padx=12, pady=8).pack(side="right", padx=3)

        self.chart_frame = tk.Frame(self, bg=t["bg"])
        self.chart_frame.pack(fill="both", expand=True, padx=14, pady=10)
        self._draw_chart()

    def _switch_period(self, period):
        self.period = period
        self.title(f"{period} Sales Report")
        self._draw_chart()

    def _draw_chart(self):
        for w in self.chart_frame.winfo_children():
            w.destroy()
        self.buckets, self.sales = get_sales_data(self.period)

        t = utils.theme()
        face = t["surface"]
        fig = Figure(figsize=(7, 4.5), dpi=100, facecolor=face)
        ax = fig.add_subplot(111)
        ax.set_facecolor(face)
        if self.buckets:
            keys = list(self.buckets.keys())
            values = [self.buckets[k] for k in keys]
            ax.bar(keys, values, color=t["primary"], edgecolor=t["primary_dark"], linewidth=0.5, zorder=3)
        ax.set_title(f"{self.period} Sales (₹)", color=t["text"], fontweight="bold")
        ax.set_ylabel("Revenue (₹)", color=t["muted"])
        ax.tick_params(colors=t["muted"])
        for spine in ax.spines.values():
            spine.set_color(t["border"])
        ax.grid(axis="y", color=t["border"], linewidth=0.6, zorder=0)
        fig.autofmt_xdate(rotation=45)

        chart_card = utils.card(self.chart_frame, padx=0, pady=0)
        chart_card.pack(fill="both", expand=True)
        canvas = FigureCanvasTkAgg(fig, master=chart_card)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True, padx=10, pady=10)

        total = sum(self.buckets.values())
        summary = tk.Frame(self.chart_frame, bg=t["bg"])
        summary.pack(fill="x", pady=(10, 0))
        utils.Pill(summary, f"Total: {utils.format_currency(total)}", color=t["primary"]).pack(side="left", padx=4)
        utils.Pill(summary, f"Orders: {len(self.sales)}", color=t["success"]).pack(side="left", padx=4)

    def export_pdf(self):
        os.makedirs(utils.RECEIPTS_DIR, exist_ok=True)
        path = os.path.join(utils.RECEIPTS_DIR, f"report_{self.period.lower()}_{datetime.date.today()}.pdf")
        c = pdfcanvas.Canvas(path, pagesize=A4)
        width, height = A4
        y = height - 20 * mm
        c.setFont("Helvetica-Bold", 16)
        c.drawString(20 * mm, y, f"{utils.RESTAURANT_NAME} - {self.period} Sales Report")
        y -= 10 * mm
        c.setFont("Helvetica", 10)
        for key, val in self.buckets.items():
            c.drawString(20 * mm, y, key)
            c.drawRightString(width - 20 * mm, y, utils.format_currency_pdf(val))
            y -= 6 * mm
            if y < 20 * mm:
                c.showPage()
                y = height - 20 * mm
        c.showPage()
        c.save()
        messagebox.showinfo("Exported", f"PDF report saved to {path}")

    def export_excel(self):
        if not XLSX_OK:
            messagebox.showerror("Missing library", "Install 'openpyxl' to export Excel reports.")
            return
        os.makedirs(utils.RECEIPTS_DIR, exist_ok=True)
        path = os.path.join(utils.RECEIPTS_DIR, f"report_{self.period.lower()}_{datetime.date.today()}.xlsx")
        wb = openpyxl.Workbook()
        ws = wb.active
        ws.title = f"{self.period} Sales"
        ws.append(["Date", "Revenue (INR)"])
        for key, val in self.buckets.items():
            ws.append([key, round(val, 2)])
        wb.save(path)
        messagebox.showinfo("Exported", f"Excel report saved to {path}")
