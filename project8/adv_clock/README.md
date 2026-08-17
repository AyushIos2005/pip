# ⏱️ Smart Time Suite

A modern, modular desktop time-management application built entirely with **Python 3.12+** and **Tkinter**. Smart Time Suite bundles a live digital clock, a world clock, a stopwatch, a countdown timer, and a full-featured alarm manager into one clean dashboard — with five switchable color themes and persistent settings.

---

## 📋 Project Overview

Smart Time Suite is a single-window desktop dashboard with a sidebar navigation, a top bar, a status bar, and a swappable content area. Each time-related tool is implemented as an independent, reusable Tkinter frame (`ClockFrame`, `WorldClockFrame`, `Stopwatch`, `Timer`, `AlarmFrame`), following an object-oriented, modular architecture so each module can be developed, tested, and reused independently.

The app never blocks its GUI thread — all clocks, countdowns, and alarm checks are driven by Tkinter's non-blocking `after()` scheduler (with background threads only for sound playback), so the interface stays responsive at all times.

---

## ✨ Features

### 🕒 Digital Clock
- Live HH:MM:SS clock with a smooth blinking colon
- 12-hour / 24-hour toggle with AM/PM
- Full date display (day, date, month, year)

### 🌍 World Clock
- Simultaneous live clocks for Kolkata, London, New York, Dubai, Tokyo, and Sydney
- Powered by Python's built-in `zoneinfo` module — no external timezone dependency

### ⏱️ Stopwatch
- Start / Pause / Resume / Reset
- Lap recording with a scrollable lap list
- Millisecond precision (`00:00:00.000`)

### ⏳ Timer
- Countdown input for hours, minutes, and seconds
- Start / Pause / Resume / Reset
- Plays a sound, shows a desktop notification, and pops up an alert when finished
- Validates input and rejects invalid/negative durations

### ⏰ Alarm
- Create multiple alarms with a custom message
- Daily-repeating or one-time alarms
- Edit or delete existing alarms
- Snooze (5 minutes) or Dismiss when an alarm rings
- Alarms persist to `alarms.json` and survive corrupted/missing files gracefully

### 🎨 Themes
- Five instant, full-app themes: **Light, Dark, Blue, Green, Purple**
- Every widget (including the status bar, buttons, tables, and text) updates instantly

### ⚙️ Settings
- Stored in `settings.json`: theme, time format, notifications, hourly chime, alarm volume
- Automatically loaded at startup and saved on exit or on change

### 🔔 Notifications
- Desktop notifications via `plyer` (alarm ringing, timer finished)
- Gracefully falls back to console logging / system bell if `plyer` or the sound file is unavailable

### 🖱️ Extras
- Splash screen with fade-in/fade-out animation on startup
- Full menu bar (File, View, Theme, Help)
- Keyboard shortcuts for fast navigation
- Robust error handling for missing assets, invalid input, and corrupted files

---

## ⌨️ Keyboard Shortcuts

| Shortcut | Action |
|----------|--------|
| `Ctrl+1` | Clock |
| `Ctrl+2` | Stopwatch |
| `Ctrl+3` | Timer |
| `Ctrl+4` | Alarm |
| `Ctrl+5` | World Clock |
| `Ctrl+Q` | Exit |

---

## 📸 Screenshots

> Screenshots are stored in the `screenshots/` folder. Add your own captures here, e.g.:
>
> ![Dashboard - Dark Theme](screenshots/dashboard_dark.png)
> ![World Clock](screenshots/world_clock.png)
> ![Alarm Manager - Green Theme](screenshots/alarm_green.png)

---

## 🛠️ Installation

1. **Clone or download** this repository:
   ```bash
   git clone https://github.com/your-username/smart-time-suite.git
   cd smart-time-suite
   ```

2. **Create a virtual environment** (recommended):
   ```bash
   python -m venv venv
   venv\Scripts\activate      # Windows
   source venv/bin/activate   # macOS/Linux
   ```

3. **Install dependencies:**
   ```bash
   pip install -r requirements.txt
   ```

> **Note:** Tkinter ships with most standard Python installations. On some Linux distributions you may need to install it separately, e.g. `sudo apt install python3-tk`.

---

## 📦 Requirements

- Python 3.12 or higher
- Tkinter (bundled with standard Python installers on Windows/macOS)
- `plyer` — desktop notifications
- `playsound` — alarm/timer sound playback

See [`requirements.txt`](requirements.txt) for exact versions.

---

## ▶️ How to Run

From the project root:

```bash
python main.py
```

The app will show a splash screen for a few seconds, then open the main dashboard.

---

## 📁 Folder Structure

```
DigitalClock/
│
├── main.py              # Entry point: splash screen, dashboard, menu, settings
├── clock_module.py       # Digital Clock and World Clock frames
├── stopwatch.py           # Stopwatch module
├── timer.py                # Countdown Timer module
├── alarm.py                 # Alarm module (CRUD + JSON persistence)
├── themes.py                 # Theme palettes and ThemeManager
├── notifications.py           # Desktop notification + sound helpers
├── settings.json                # Persisted user settings
├── alarms.json                   # Persisted alarms (created at runtime)
├── requirements.txt               # Python dependencies
├── README.md                       # This file
│
├── assets/
│   ├── icon.ico             # App window icon (optional, falls back gracefully)
│   ├── splash.png            # Splash screen logo (optional)
│   ├── alarm.wav               # Alarm/timer sound (optional)
│   └── logo.png                  # App logo (optional)
│
└── screenshots/                     # Screenshots for this README
```

---

## 🚀 Future Improvements

- Custom alarm sounds per alarm
- Hourly chime implementation
- Pomodoro-style focus timer mode
- System tray minimization
- Export/import settings and alarms
- Localization / multi-language support
- Analog clock face option

---

## 📄 License

This project is released under the **MIT License**. You are free to use, modify, and distribute it with attribution.

---

## 👤 Developer

Built by the **Smart Time Suite Team**.
GitHub: [https://github.com/your-username/smart-time-suite](https://github.com/your-username/smart-time-suite)
