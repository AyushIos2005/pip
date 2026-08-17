# Restaurant POS System

A desktop Restaurant Point-of-Sale (Waiter + Kitchen + Admin) application
built with **Python, Tkinter, and MongoDB**.

## Features

- **Login** — Admin / Waiter roles, MongoDB-backed, PBKDF2 password hashing.
- **Dashboard** — 5 tables colour-coded (Available / Occupied / Reserved),
  live clock, current date, logged-in waiter name, dark/light theme toggle.
- **Menu & Order Screen** — category tabs, search, quantity stepper, live cart
  with increase/decrease/remove, Save Order / Send to Kitchen / Generate Bill.
- **Kitchen Display (KOT)** — every order sent to kitchen appears automatically
  (3-second polling refresh). Accept → Preparing → Ready workflow. When an
  order is marked Ready, the waiter's dashboard shows a "Table X Order Ready"
  popup.
- **Billing** — configurable GST %, discount, auto-incrementing bill number,
  professional PDF receipt generated with ReportLab and saved to `receipts/`.
- **Payment** — Cash / UPI / Card. UPI generates a scannable QR code
  (`upi://pay` deep link) on the fly. Table auto-frees on successful payment.
- **Admin Panel** — Menu CRUD, today's/monthly sales, best sellers, bill &
  order search, waiter performance, Daily/Weekly/Monthly/Yearly reports with
  Matplotlib charts, export to PDF and Excel.
- **MongoDB Collections** — `users`, `tables`, `menu`, `orders`,
  `order_items`, `payments`, `sales`, `settings`, `counters` — every document
  carries `createdAt`, `updatedAt`, `status`.

## Setup

```bash
pip install -r requirements.txt
```

Set your MongoDB connection string (MongoDB Atlas or local):

```bash
# Linux / macOS
export MONGO_URI="mongodb+srv://<user>:<pass>@<cluster>.mongodb.net"

# Windows (PowerShell)
$env:MONGO_URI="mongodb+srv://<user>:<pass>@<cluster>.mongodb.net"
```

If `MONGO_URI` is not set, the app falls back to a local instance at
`mongodb://localhost:27017`.

Run the app:

```bash
python main.py
```

On first run the app automatically seeds sample data: 5 tables, 16 menu
items across 6 categories, global settings, and demo accounts:

| Role   | Username | Password  |
|--------|----------|-----------|
| Admin  | admin    | admin123  |
| Waiter | waiter   | waiter123 |
| Waiter | waiter2  | waiter123 |

## Project Structure

```
restaurant_pos/
├── main.py          # Splash screen + entry point
├── login.py         # Login window
├── dashboard.py      # Table grid, top bar, notifications
├── menu.py           # Order screen (menu grid + cart)
├── kitchen.py        # KOT display
├── billing.py         # Bill calculation + PDF generation
├── payment.py         # Cash / UPI (QR) / Card dialog
├── admin.py           # Admin panel (menu CRUD, sales, search, performance)
├── reports.py          # Sales aggregation, Matplotlib charts, PDF/Excel export
├── database.py          # MongoDB connection singleton + seeding
├── models.py             # Document builders (users, menu, orders, payments)
├── utils.py               # Theme, fonts, formatting, helpers
├── assets/images|icons|logo/  # Put menu item images / logo.png here (optional)
├── receipts/                    # Generated PDF bills & reports land here
├── database/                     # Reserved for local DB files/exports
└── requirements.txt
```

## Notes / Design Decisions

- **Navigation pattern**: each screen is its own `tk.Tk()`/`tk.Toplevel()`
  window (Login → Dashboard → Order/Kitchen/Admin). This keeps each module
  self-contained and easy to extend, at the cost of a fresh window per screen
  transition — a deliberate simplicity trade-off for a Tkinter desktop app.
- **"Automatic" KOT delivery**: Tkinter has no push/websocket channel, so the
  Kitchen Display and Dashboard notifications use a 3-second `after()` polling
  loop against MongoDB — new orders / status changes appear within 3 seconds
  without any manual refresh.
- **Images are optional**: if a menu item has no `image_path` or the file is
  missing, a coloured placeholder with the item's initials is shown instead
  of breaking the UI.
- **Dark/Light theme**: toggling the theme re-opens the current window with
  the new palette applied (all screens read colours from `utils.theme()` at
  build time).
- Passwords are stored as salted PBKDF2-HMAC-SHA256 hashes, never plaintext.

## Extending

- Add real menu photos to `assets/images/` and set `image_path` for each item
  via the Admin → Menu Management tab.
- Add `assets/logo/logo.png` to show your own logo instead of the emoji icon.
- Edit restaurant name/address/GSTIN/UPI ID at the top of `utils.py`, or update
  the `settings` document directly in MongoDB.
