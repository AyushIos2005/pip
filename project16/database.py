"""
database.py
MongoDB connection layer (PyMongo) + sample-data seeding.

Set the connection string via the MONGO_URI environment variable, e.g.

    export MONGO_URI="mongodb+srv://user:pass@cluster0.mongodb.net"

If MONGO_URI is not set, it falls back to a local MongoDB instance at
mongodb://localhost:27017 (useful for development / testing).
"""

import os
import datetime
import pymongo
from pymongo.errors import ServerSelectionTimeoutError

import utils
import models

MONGO_URI = os.environ.get("MONGO_URI", "mongodb+srv://codehub1vgi_db_user:Vl1A2MklqP8jNeh1@waiter.prv6ajn.mongodb.net/")
DB_NAME = os.environ.get("MONGO_DB_NAME", "restaurant_pos")


class Database:
    """Singleton wrapper around the PyMongo client/collections."""

    _instance = None

    def __init__(self):
        self.client = pymongo.MongoClient(MONGO_URI, serverSelectionTimeoutMS=6000)
        self.db = self.client[DB_NAME]

        self.users = self.db.users
        self.tables = self.db.tables
        self.menu = self.db.menu
        self.orders = self.db.orders
        self.order_items = self.db.order_items
        self.payments = self.db.payments
        self.sales = self.db.sales
        self.settings = self.db.settings
        self.counters = self.db.counters
        self.customers = self.db.customers
        self.feedback = self.db.feedback

    @classmethod
    def instance(cls):
        if cls._instance is None:
            cls._instance = cls()
        return cls._instance

    # ------------------------------------------------------------------ #
    def test_connection(self):
        try:
            self.client.admin.command("ping")
            return True, "Connected"
        except ServerSelectionTimeoutError as e:
            return False, str(e)
        except Exception as e:  # pragma: no cover - defensive
            return False, str(e)

    def next_sequence(self, name: str) -> int:
        """Atomically increment and return a named counter (bill no, KOT no...)."""
        doc = self.counters.find_one_and_update(
            {"_id": name},
            {"$inc": {"seq": 1}},
            upsert=True,
            return_document=pymongo.ReturnDocument.AFTER,
        )
        return doc["seq"]

    # ------------------------------------------------------------------ #
    def seed_data(self):
        """Insert sample data on first run so the app is usable immediately."""
        if self.users.count_documents({}) == 0:
            self.users.insert_many([
                models.new_user_doc("admin", "admin123", "Admin", "admin"),
                models.new_user_doc("waiter", "waiter123", "Rahul Sharma", "waiter"),
                models.new_user_doc("waiter2", "waiter123", "Priya Das", "waiter"),
            ])

        if self.tables.count_documents({}) == 0:
            docs = []
            for i in range(1, 6):
                docs.append({
                    "table_no": i,
                    "status": "available",  # available | occupied | reserved
                    "current_order_id": None,
                    "createdAt": datetime.datetime.now(),
                    "updatedAt": datetime.datetime.now(),
                })
            self.tables.insert_many(docs)

        if self.menu.count_documents({}) == 0:
            sample_items = [
                ("Masala Chai", 40, "Beverages"),
                ("Cold Coffee", 90, "Beverages"),
                ("Fresh Lime Soda", 60, "Beverages"),
                ("Paneer Butter Masala", 220, "North Indian"),
                ("Dal Makhani", 180, "North Indian"),
                ("Butter Naan", 45, "North Indian"),
                ("Masala Dosa", 120, "South Indian"),
                ("Idli Sambhar", 90, "South Indian"),
                ("Medu Vada", 80, "South Indian"),
                ("Veg Hakka Noodles", 160, "Chinese"),
                ("Chilli Paneer", 190, "Chinese"),
                ("Manchow Soup", 110, "Chinese"),
                ("Margherita Pizza", 250, "Italian"),
                ("Alfredo Pasta", 230, "Italian"),
                ("Gulab Jamun", 70, "Desserts"),
                ("Chocolate Brownie", 130, "Desserts"),
            ]
            docs = [models.new_menu_item_doc(n, p, c) for n, p, c in sample_items]
            self.menu.insert_many(docs)

        if self.settings.count_documents({}) == 0:
            self.settings.insert_one({
                "_id": "global",
                "gst_percent": 5.0,
                "restaurant_name": utils.RESTAURANT_NAME,
                "restaurant_address": utils.RESTAURANT_ADDRESS,
                "gstin": utils.RESTAURANT_GSTIN,
                "phone": utils.RESTAURANT_PHONE,
                "upi_id": utils.UPI_ID,
                "updatedAt": datetime.datetime.now(),
            })

    def get_settings(self):
        s = self.settings.find_one({"_id": "global"})
        if not s:
            self.seed_data()
            s = self.settings.find_one({"_id": "global"})
        return s
