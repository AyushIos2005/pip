# 🌐 Internet Speed Tester Pro

A production-quality, desktop **Internet Speed Testing application** built with **Python 3.12+**, featuring a modern dark-themed UI, animated circular speed gauge, live graphing, CSV history tracking, and multi-format report export (CSV / PDF / TXT).

![Python](https://img.shields.io/badge/Python-3.12%2B-blue)
![License](https://img.shields.io/badge/License-MIT-green)
![Platform](https://img.shields.io/badge/Platform-Windows%20%7C%20macOS%20%7C%20Linux-lightgrey)

---

## ✨ Features

- **Modern Dashboard UI** — Dark-themed, card-based layout with sidebar navigation, top bar, and status bar, built with `ttkbootstrap`.
- **Animated Splash Screen** — Branded loading screen with animated ellipsis and progress bar.
- **Animated Circular Speed Gauge** — Smooth needle interpolation drawn on a native Tkinter Canvas.
- **Live Speed Graph** — Matplotlib-powered download/upload trend chart embedded directly in the dashboard.
- **Full Speed Test Metrics** — Download, Upload, Ping, Jitter, Server, ISP, Public IP, and Test Duration.
- **Threaded, Non-Blocking Tests** — All network operations run on background threads; the GUI never freezes.
- **Persistent History** — Every test result is saved to `history/history.csv`, with search, sort, and delete support via a `pandas`-backed table.
- **Multi-Format Reports** — Export history as CSV, TXT, or a fully formatted PDF (logo, trend graph, results table, footer) via `reportlab`.
- **5 Built-in Themes** — Dark, Light, Blue, Green, Purple — switchable live from Settings or the Theme menu.
- **Desktop Notifications** — Alerts for test completion, disconnect/reconnect events, exports, and report generation via `plyer`.
- **Automatic Network Monitor** — Background polling detects connection loss/recovery in real time.
- **Keyboard Shortcuts** — `Ctrl+N` New Test · `Ctrl+S` Save · `Ctrl+E` Export · `Ctrl+Q` Quit · `F5` Run Test.
- **Clean MVC-Style Architecture** — Fully modular, typed, documented, and PEP8-compliant codebase with no global mutable state.

---

## 📸 Screenshots

> Place screenshots of the running application inside the `screenshots/` folder and reference them here, e.g.:
>
> `screenshots/dashboard.png`, `screenshots/history.png`, `screenshots/reports.png`

---

## 🛠️ Installation

### 1. Clone the repository
```bash
git clone https://github.com/yourusername/internet-speed-tester-pro.git
cd internet-speed-tester-pro
```

### 2. Create a virtual environment (recommended)
```bash
python -m venv venv
# Windows
venv\Scripts\activate
# macOS / Linux
source venv/bin/activate
```

### 3. Install dependencies
```bash
pip install -r requirements.txt
```

---

## ▶️ Run the Application

```bash
python main.py
```

The application will display a 3-second animated splash screen, then open the main dashboard.

---

## 📋 Requirements

- Python **3.12 or higher**
- Internet connection (for running speed tests and fetching public IP/ISP data)
- See `requirements.txt` for the full dependency list:
  - `ttkbootstrap`, `speedtest-cli`, `requests`, `matplotlib`, `pandas`, `reportlab`, `plyer`, `Pillow`

---

## 📁 Folder Structure

```text
InternetSpeedTester/
│
├── main.py                # App entry point + animated splash screen
├── dashboard.py            # Full UI layer: sidebar, cards, gauge, graph, views
├── speed_test.py            # Threaded speedtest-cli wrapper
├── history.py               # CSV history management (pandas)
├── reports.py                # CSV / PDF / TXT report generation
├── notifications.py           # Desktop notification wrapper (plyer)
├── themes.py                   # Color palettes, fonts, ThemeManager
├── settings.py                  # Typed settings loader/saver
├── utils.py                      # Logging, formatting, network helpers
├── settings.json                  # Default persisted configuration
├── requirements.txt
├── README.md
│
├── assets/                # icon.ico, splash.png, logo.png, background.png
├── reports/                # Generated CSV / PDF / TXT reports
├── history/                 # history.csv (auto-created)
└── screenshots/               # App screenshots for documentation
```

---

## 🧱 Architecture

The project follows an **MVC-inspired structure**:

| Layer | Responsibility | Files |
|---|---|---|
| **Model** | Data & business logic | `speed_test.py`, `history.py`, `reports.py`, `settings.py` |
| **View** | UI widgets & layout | `dashboard.py` (StatCard, SpeedGauge, LiveGraph, DashboardView, HistoryView, ReportsView, SettingsView, AboutView) |
| **Controller** | Wires user actions to the model, manages threading | `dashboard.py` (`MainWindow`), `main.py` |

All background work (speed tests, network monitoring) runs on daemon threads. Results are always marshalled back to the Tkinter main loop using `root.after(0, ...)` to keep the UI thread-safe.

---

## 🚀 Future Improvements

- [ ] Historical speed comparison charts (weekly / monthly averages)
- [ ] Multi-language localization support
- [ ] System tray integration with quick-test shortcut
- [ ] Scheduled/automatic recurring speed tests
- [ ] Cloud sync of history across devices
- [ ] Packaged installer (`.exe` via PyInstaller / Inno Setup)
- [ ] Dark/light auto-switching based on OS theme

---

## 📄 License

This project is licensed under the **MIT License** — free to use, modify, and distribute.

---

## 👤 Developer

Built by **Vikash**.
Contributions, issues, and feature requests are welcome — feel free to open an issue or submit a pull request on GitHub.
