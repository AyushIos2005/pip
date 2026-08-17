"""
customer_admin.py
Admin-side "Customers" and "Feedback Analytics" screens, plus the
aggregation helpers they render. Kept separate from admin.py so that
file stays focused on menu/sales/search/performance.
"""

import re
import datetime
import tkinter as tk
from tkinter import ttk, messagebox

import utils
from database import Database

import matplotlib
matplotlib.use("TkAgg")
from matplotlib.figure import Figure
from matplotlib.backends.backend_tkagg import FigureCanvasTkAgg

STOPWORDS = {
    "the", "and", "was", "were", "for", "with", "very", "this", "that", "food",
    "our", "but", "had", "have", "not", "you", "your", "are", "its", "it's",
    "just", "really", "some", "from", "they", "them", "their", "over", "all",
}


# --------------------------------------------------------------------------- #
# Aggregation helpers
# --------------------------------------------------------------------------- #
def get_feedback_summary():
    db = Database.instance()
    docs = list(db.feedback.find())
    total = len(docs)
    avg = sum(d["rating"] for d in docs) / total if total else 0.0
    dist = {i: 0 for i in range(1, 6)}
    for d in docs:
        dist[d["rating"]] = dist.get(d["rating"], 0) + 1
    positive = sum(v for k, v in dist.items() if k >= 4)
    negative = sum(v for k, v in dist.items() if k <= 2)
    neutral = total - positive - negative
    return {
        "total": total, "average": avg, "distribution": dist,
        "positive": positive, "negative": negative, "neutral": neutral, "docs": docs,
    }


def get_waiter_ratings():
    db = Database.instance()
    pipeline = [
        {"$group": {"_id": "$waiter_name", "avg_rating": {"$avg": "$rating"}, "count": {"$sum": 1}}},
        {"$sort": {"avg_rating": -1}},
    ]
    return list(db.feedback.aggregate(pipeline))


def get_feedback_trend(period="Weekly"):
    db = Database.instance()
    days = {"Daily": 1, "Weekly": 7, "Monthly": 30}.get(period, 7)
    since = datetime.datetime.now() - datetime.timedelta(days=days)
    fmt = "%d-%b"
    docs = list(db.feedback.find({"date": {"$gte": since}}))
    buckets = {}
    for d in docs:
        key = d["date"].strftime(fmt)
        buckets.setdefault(key, []).append(d["rating"])
    return {k: sum(v) / len(v) for k, v in buckets.items()}, len(docs)


def _top_words(comments, limit=6):
    counts = {}
    for c in comments:
        for word in re.findall(r"[A-Za-z']+", c.lower()):
            if len(word) < 4 or word in STOPWORDS:
                continue
            counts[word] = counts.get(word, 0) + 1
    ranked = sorted(counts.items(), key=lambda kv: kv[1], reverse=True)
    return [w for w, _ in ranked[:limit]]


def get_top_compliments_and_complaints():
    docs = get_feedback_summary()["docs"]
    positive_comments = [d["comment"] for d in docs if d["rating"] >= 4 and d.get("comment")]
    negative_comments = [d["comment"] for d in docs if d["rating"] <= 2 and d.get("comment")]
    return _top_words(positive_comments), _top_words(negative_comments)


# --------------------------------------------------------------------------- #
# Customers tab
# --------------------------------------------------------------------------- #
def build_customers_tab(admin_panel, tab):
    t = utils.theme()
    db = Database.instance()

    top = tk.Frame(tab, bg=t["bg"])
    top.pack(fill="x", padx=8, pady=8)
    tk.Label(top, text="Search (Name or Mobile)", bg=t["bg"], fg=t["muted"], font=utils.FONT_SMALL).pack(side="left")
    search_var = tk.StringVar()
    wrap, entry = utils.entry_field(top, textvariable=search_var)
    wrap.pack(side="left", padx=8)
    entry.configure(width=26)

    cols = ("name", "mobile", "visits", "spent", "avg_rating", "last_visit")
    tree = ttk.Treeview(tab, columns=cols, show="headings", height=18)
    headings = {"name": "Name", "mobile": "Mobile", "visits": "Visits", "spent": "Total Spent",
                "avg_rating": "Avg Rating", "last_visit": "Last Visit"}
    for c in cols:
        tree.heading(c, text=headings[c])
        tree.column(c, width=140)
    tree.pack(fill="both", expand=True, padx=8, pady=(0, 8))

    def refresh(*_):
        for row in tree.get_children():
            tree.delete(row)
        query = {}
        q = search_var.get().strip()
        if q:
            query = {"$or": [
                {"name": {"$regex": q, "$options": "i"}},
                {"mobile": {"$regex": q, "$options": "i"}},
            ]}
        for c in db.customers.find(query).sort("last_visit_date", -1).limit(300):
            tree.insert("", "end", iid=str(c["_id"]), values=(
                c.get("name", ""), c.get("mobile", ""), c.get("total_visits", 0),
                utils.format_currency(c.get("total_amount_spent", 0)),
                f"{c.get('average_rating', 0):.1f}" if c.get("rating_count") else "—",
                utils.format_date(c.get("last_visit_date")) if c.get("last_visit_date") else "—",
            ))

    def open_profile(event):
        sel = tree.selection()
        if not sel:
            return
        import bson
        customer = db.customers.find_one({"_id": bson.ObjectId(sel[0])})
        if customer:
            CustomerProfileWindow(admin_panel, customer)

    utils.make_round_button(top, "Search", refresh, bg=t["primary"], padx=14, pady=8).pack(side="left", padx=6)
    tk.Label(top, text="Double-click a row to view the full profile", bg=t["bg"], fg=t["muted"], font=utils.FONT_TINY).pack(side="right")
    tree.bind("<Double-1>", open_profile)
    search_var.trace_add("write", lambda *a: refresh())
    refresh()


class CustomerProfileWindow(tk.Toplevel):
    def __init__(self, parent, customer):
        super().__init__(parent)
        self.customer = customer
        self.db = Database.instance()
        self.title(f"Customer Profile - {customer.get('name', '')}")
        utils.center_window(self, 560, 640)
        t = utils.theme()
        self.configure(bg=t["bg"])
        utils.setup_ttk_style(self)
        self._build_ui()

    def _row(self, parent, label, value):
        t = utils.theme()
        r = tk.Frame(parent, bg=t["surface"])
        r.pack(fill="x", pady=3)
        tk.Label(r, text=label, bg=t["surface"], fg=t["muted"], font=utils.FONT_SMALL, width=22, anchor="w").pack(side="left")
        tk.Label(r, text=str(value), bg=t["surface"], fg=t["text"], font=utils.FONT_SMALL, anchor="w").pack(side="left")

    def _build_ui(self):
        t = utils.theme()
        c = self.customer
        outer = utils.card(self, padx=0, pady=0)
        outer.pack(fill="both", expand=True, padx=14, pady=14)
        body = tk.Frame(outer, bg=t["surface"], padx=20, pady=18)
        body.pack(fill="both", expand=True)

        tk.Label(body, text=f"👤  {c.get('name', '')}", font=utils.FONT_TITLE, bg=t["surface"], fg=t["text"]).pack(anchor="w")
        tk.Label(body, text=c.get("mobile", ""), font=utils.FONT_SMALL, bg=t["surface"], fg=t["muted"]).pack(anchor="w", pady=(0, 14))

        utils.section_header(body, "Overview", icon="📊").pack(anchor="w", fill="x", pady=(0, 8))
        self._row(body, "Email", c.get("email") or "—")
        self._row(body, "Birthday", c.get("birthday") or "—")
        self._row(body, "First Visit", utils.format_date(c.get("first_visit_date")) if c.get("first_visit_date") else "—")
        self._row(body, "Last Visit", utils.format_date(c.get("last_visit_date")) if c.get("last_visit_date") else "—")
        self._row(body, "Total Visits", c.get("total_visits", 0))
        self._row(body, "Total Orders", c.get("total_orders", 0))
        self._row(body, "Total Spent (CLV)", utils.format_currency(c.get("total_amount_spent", 0)))
        self._row(body, "Average Bill Value", utils.format_currency(c.get("average_bill_value", 0)))
        self._row(body, "Preferred Payment", c.get("preferred_payment_method") or "—")
        self._row(body, "Average Rating", f"{c.get('average_rating', 0):.1f} / 5" if c.get("rating_count") else "No ratings yet")
        if c.get("notes"):
            self._row(body, "Notes", c["notes"])

        fav = c.get("favorite_menu_items", {})
        if fav:
            utils.section_header(body, "Favorite Items", icon="🍽").pack(anchor="w", fill="x", pady=(16, 8))
            top_items = sorted(fav.items(), key=lambda kv: kv[1], reverse=True)[:5]
            tk.Label(body, text="  ·  ".join(f"{n} ({qty})" for n, qty in top_items),
                     font=utils.FONT_SMALL, bg=t["surface"], fg=t["text"], wraplength=480, justify="left").pack(anchor="w")

        history = c.get("feedback_history", [])
        utils.section_header(body, "Feedback History", icon="⭐").pack(anchor="w", fill="x", pady=(16, 8))
        if history:
            for h in reversed(history[-5:]):
                stars = "★" * h.get("rating", 0) + "☆" * (5 - h.get("rating", 0))
                row = tk.Frame(body, bg=t["surface"])
                row.pack(fill="x", pady=2)
                tk.Label(row, text=stars, font=utils.FONT_SMALL, bg=t["surface"], fg=t["accent"]).pack(anchor="w")
                if h.get("comment"):
                    tk.Label(row, text=h["comment"], font=utils.FONT_TINY, bg=t["surface"], fg=t["muted"],
                             wraplength=480, justify="left").pack(anchor="w")
        else:
            tk.Label(body, text="No feedback submitted yet.", font=utils.FONT_SMALL, bg=t["surface"], fg=t["muted"]).pack(anchor="w")


# --------------------------------------------------------------------------- #
# Feedback Analytics tab
# --------------------------------------------------------------------------- #
def build_feedback_tab(admin_panel, tab):
    t = utils.theme()
    summary = get_feedback_summary()

    top = tk.Frame(tab, bg=t["bg"])
    top.pack(fill="x", padx=8, pady=8)
    for label, value, color in [
        ("Total Feedback", summary["total"], t["primary"]),
        ("Average Rating", f"{summary['average']:.1f} / 5", t["accent"]),
        ("Positive", summary["positive"], t["success"]),
        ("Negative", summary["negative"], t["danger"]),
    ]:
        box_outer = utils.card(top, accent=color, padx=0, pady=0)
        box_outer.pack(side="left", padx=6)
        box = tk.Frame(box_outer, bg=t["surface"], padx=18, pady=12)
        box.pack()
        tk.Label(box, text=label, font=utils.FONT_TINY, bg=t["surface"], fg=t["muted"]).pack()
        tk.Label(box, text=str(value), font=utils.FONT_SUBTITLE, bg=t["surface"], fg=t["text"]).pack()

    nb = ttk.Notebook(tab)
    nb.pack(fill="both", expand=True, padx=8, pady=8)

    charts_tab = tk.Frame(nb, bg=t["bg"])
    recent_tab = tk.Frame(nb, bg=t["bg"])
    waiters_tab = tk.Frame(nb, bg=t["bg"])
    words_tab = tk.Frame(nb, bg=t["bg"])
    nb.add(charts_tab, text="  Rating Charts  ")
    nb.add(recent_tab, text="  Recent Feedback  ")
    nb.add(waiters_tab, text="  Waiter-wise  ")
    nb.add(words_tab, text="  Compliments / Complaints  ")

    _build_charts(charts_tab, summary)
    _build_recent(recent_tab, summary)
    _build_waiters(waiters_tab)
    _build_words(words_tab)


def _build_charts(tab, summary):
    t = utils.theme()
    period_var = tk.StringVar(value="Weekly")
    top = tk.Frame(tab, bg=t["bg"])
    top.pack(fill="x", padx=8, pady=8)
    for label in ("Daily", "Weekly", "Monthly"):
        utils.make_round_button(top, label, lambda p=label: switch(p), variant="outline", padx=10, pady=6).pack(side="left", padx=3)

    chart_frame = tk.Frame(tab, bg=t["bg"])
    chart_frame.pack(fill="both", expand=True, padx=8, pady=4)

    def draw():
        for w in chart_frame.winfo_children():
            w.destroy()
        face = t["surface"]
        fig = Figure(figsize=(8, 4.2), dpi=100, facecolor=face)

        ax1 = fig.add_subplot(121)
        ax1.set_facecolor(face)
        dist = summary["distribution"]
        ax1.bar([str(k) for k in dist.keys()], list(dist.values()), color=t["accent"], zorder=3)
        ax1.set_title("Rating Distribution", color=t["text"], fontsize=10, fontweight="bold")
        ax1.set_xlabel("Stars", color=t["muted"])
        ax1.tick_params(colors=t["muted"])
        for spine in ax1.spines.values():
            spine.set_color(t["border"])

        ax2 = fig.add_subplot(122)
        ax2.set_facecolor(face)
        buckets, _n = get_feedback_trend(period_var.get())
        if buckets:
            keys = list(buckets.keys())
            ax2.plot(keys, [buckets[k] for k in keys], marker="o", color=t["primary"])
        ax2.set_ylim(0, 5.5)
        ax2.set_title(f"{period_var.get()} Avg Rating Trend", color=t["text"], fontsize=10, fontweight="bold")
        ax2.tick_params(colors=t["muted"])
        for spine in ax2.spines.values():
            spine.set_color(t["border"])
        fig.autofmt_xdate(rotation=40)
        fig.tight_layout()

        canvas = FigureCanvasTkAgg(fig, master=chart_frame)
        canvas.draw()
        canvas.get_tk_widget().pack(fill="both", expand=True)

    def switch(p):
        period_var.set(p)
        draw()

    draw()


def _build_recent(tab, summary):
    t = utils.theme()
    cols = ("customer", "rating", "comment", "waiter", "date")
    tree = ttk.Treeview(tab, columns=cols, show="headings", height=20)
    headings = {"customer": "Customer", "rating": "Rating", "comment": "Comment", "waiter": "Waiter", "date": "Date"}
    for c in cols:
        tree.heading(c, text=headings[c])
        tree.column(c, width=150 if c != "comment" else 260)
    tree.pack(fill="both", expand=True, padx=8, pady=8)

    db = Database.instance()
    docs = sorted(summary["docs"], key=lambda d: d["date"], reverse=True)[:100]
    for d in docs:
        customer = db.customers.find_one({"_id": d.get("customer_id")}) or {}
        tree.insert("", "end", values=(
            customer.get("name", "—"), "★" * d["rating"], (d.get("comment") or "")[:60],
            d.get("waiter_name", ""), utils.format_datetime(d["date"]),
        ))


def _build_waiters(tab):
    t = utils.theme()
    cols = ("waiter", "avg_rating", "count")
    tree = ttk.Treeview(tab, columns=cols, show="headings", height=20)
    tree.heading("waiter", text="Waiter")
    tree.heading("avg_rating", text="Avg Rating")
    tree.heading("count", text="Feedback Count")
    tree.pack(fill="both", expand=True, padx=8, pady=8)
    for row in get_waiter_ratings():
        tree.insert("", "end", values=(row["_id"] or "—", f"{row['avg_rating']:.1f}", row["count"]))


def _build_words(tab):
    t = utils.theme()
    compliments, complaints = get_top_compliments_and_complaints()

    wrap = tk.Frame(tab, bg=t["bg"])
    wrap.pack(fill="both", expand=True, padx=8, pady=8)

    for title, words, color in [("👍 Top Compliments", compliments, t["success"]), ("👎 Common Complaints", complaints, t["danger"])]:
        outer = utils.card(wrap, accent=color, padx=0, pady=0)
        outer.pack(fill="x", pady=8)
        box = tk.Frame(outer, bg=t["surface"], padx=16, pady=14)
        box.pack(fill="x")
        tk.Label(box, text=title, font=utils.FONT_SUBTITLE, bg=t["surface"], fg=t["text"]).pack(anchor="w", pady=(0, 8))
        if words:
            row = tk.Frame(box, bg=t["surface"])
            row.pack(anchor="w")
            for w in words:
                utils.Pill(row, w, color=color).pack(side="left", padx=4)
        else:
            tk.Label(box, text="Not enough comments yet.", font=utils.FONT_SMALL, bg=t["surface"], fg=t["muted"]).pack(anchor="w")
