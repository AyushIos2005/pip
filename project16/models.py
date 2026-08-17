"""
models.py
Lightweight document builders / validators for MongoDB collections.
MongoDB is schemaless, but we keep a consistent shape (createdAt,
updatedAt, status) for every document as required by the spec.
"""

import datetime
import utils


def _timestamps(existing=None):
    t = datetime.datetime.now()
    if existing:
        existing["updatedAt"] = t
        return existing
    return {"createdAt": t, "updatedAt": t}


def new_user_doc(username, password, full_name, role):
    doc = {
        "username": username,
        "password": utils.hash_password(password),
        "full_name": full_name,
        "role": role,  # "admin" | "waiter"
        "status": "active",
    }
    doc.update(_timestamps())
    return doc


def new_menu_item_doc(name, price, category, image_path="", stock=100, available=True):
    doc = {
        "name": name,
        "price": float(price),
        "category": category,
        "image_path": image_path,
        "stock": int(stock),
        "status": "active" if available else "inactive",
    }
    doc.update(_timestamps())
    return doc


def new_order_doc(table_no, waiter_id, waiter_name, kot_no):
    doc = {
        "table_no": table_no,
        "waiter_id": waiter_id,
        "waiter_name": waiter_name,
        "kot_no": kot_no,
        "status": "pending",  # pending -> preparing -> ready -> billed -> paid
        "notified": False,
        "bill_no": None,
        "gst_percent": 0.0,
        "discount": 0.0,
    }
    doc.update(_timestamps())
    return doc


def new_order_item_doc(order_id, menu_item_id, name, price, qty):
    doc = {
        "order_id": order_id,
        "menu_item_id": menu_item_id,
        "name": name,
        "price": float(price),
        "qty": int(qty),
        "status": "active",
    }
    doc.update(_timestamps())
    return doc


def new_payment_doc(order_id, bill_no, amount, mode, table_no, waiter_name):
    doc = {
        "order_id": order_id,
        "bill_no": bill_no,
        "amount": float(amount),
        "mode": mode,  # "Cash" | "UPI" | "Card"
        "table_no": table_no,
        "waiter_name": waiter_name,
        "status": "paid",
        "paid_at": datetime.datetime.now(),
    }
    doc.update(_timestamps())
    return doc


def new_customer_doc(name, mobile, email="", birthday="", notes="", order_amount=0.0,
                      payment_method=None, items=None):
    """Brand-new customer record, seeded with this first visit's stats."""
    now = datetime.datetime.now()
    doc = {
        "name": name.strip(),
        "mobile": mobile.strip(),
        "email": (email or "").strip(),
        "birthday": (birthday or "").strip(),
        "notes": (notes or "").strip(),
        "first_visit_date": now,
        "last_visit_date": now,
        "total_visits": 1,
        "total_orders": 1,
        "total_amount_spent": float(order_amount),
        "average_bill_value": float(order_amount),
        "favorite_menu_items": {},
        "payment_method_counts": {payment_method: 1} if payment_method else {},
        "preferred_payment_method": payment_method or "",
        "average_rating": 0.0,
        "rating_sum": 0.0,
        "rating_count": 0,
        "feedback_history": [],
    }
    for it in (items or []):
        doc["favorite_menu_items"][it["name"]] = doc["favorite_menu_items"].get(it["name"], 0) + it["qty"]
    doc.update(_timestamps())
    return doc


def apply_customer_visit(customer, order_amount=0.0, payment_method=None, items=None,
                          email=None, birthday=None, notes=None):
    """Return a $set dict that folds a new visit into an existing customer doc."""
    now = datetime.datetime.now()
    fav = dict(customer.get("favorite_menu_items", {}))
    for it in (items or []):
        fav[it["name"]] = fav.get(it["name"], 0) + it["qty"]

    pm_counts = dict(customer.get("payment_method_counts", {}))
    if payment_method:
        pm_counts[payment_method] = pm_counts.get(payment_method, 0) + 1
    preferred = max(pm_counts, key=pm_counts.get) if pm_counts else customer.get("preferred_payment_method", "")

    total_orders = customer.get("total_orders", 0) + 1
    total_spent = customer.get("total_amount_spent", 0.0) + float(order_amount)

    update = {
        "last_visit_date": now,
        "total_visits": customer.get("total_visits", 0) + 1,
        "total_orders": total_orders,
        "total_amount_spent": total_spent,
        "average_bill_value": total_spent / total_orders if total_orders else 0.0,
        "favorite_menu_items": fav,
        "payment_method_counts": pm_counts,
        "preferred_payment_method": preferred,
    }
    if email:
        update["email"] = email.strip()
    if birthday:
        update["birthday"] = birthday.strip()
    if notes:
        update["notes"] = notes.strip()
    update["updatedAt"] = now
    return update


def new_feedback_doc(customer_id, order_id, table_no, waiter_id, waiter_name, rating, comment,
                      total_bill, payment_method):
    doc = {
        "customer_id": customer_id,
        "order_id": order_id,
        "table_no": table_no,
        "waiter_id": waiter_id,
        "waiter_name": waiter_name,
        "rating": int(rating),
        "comment": (comment or "").strip(),
        "total_bill": float(total_bill),
        "payment_method": payment_method,
        "date": datetime.datetime.now(),
    }
    doc.update(_timestamps())
    return doc
