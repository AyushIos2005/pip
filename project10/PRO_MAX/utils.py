"""
utils.py
--------
General-purpose, dependency-light helper utilities shared across the
application: logging setup, filesystem helpers, formatting helpers,
network info lookups, and simple time/date helpers.

Keeping these here avoids duplicate code across dashboard.py,
speed_test.py, history.py and reports.py.
"""

from __future__ import annotations

import logging
import os
import socket
from datetime import datetime
from logging.handlers import RotatingFileHandler
from typing import Optional, Tuple

import requests


APP_ROOT = os.path.dirname(os.path.abspath(__file__))
LOG_DIR = os.path.join(APP_ROOT, "logs")
HISTORY_DIR = os.path.join(APP_ROOT, "history")
REPORTS_DIR = os.path.join(APP_ROOT, "reports")
ASSETS_DIR = os.path.join(APP_ROOT, "assets")


def ensure_directories() -> None:
    """Create all directories the application depends on, if missing."""
    for directory in (LOG_DIR, HISTORY_DIR, REPORTS_DIR, ASSETS_DIR):
        os.makedirs(directory, exist_ok=True)


def get_logger(name: str) -> logging.Logger:
    """
    Return a configured module-level logger that writes to both the
    console and a rotating log file under logs/app.log.
    """
    ensure_directories()
    logger = logging.getLogger(name)
    if logger.handlers:
        # Logger already configured (avoid duplicate handlers).
        return logger

    logger.setLevel(logging.DEBUG)

    formatter = logging.Formatter(
        fmt="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
    )

    console_handler = logging.StreamHandler()
    console_handler.setLevel(logging.INFO)
    console_handler.setFormatter(formatter)

    file_handler = RotatingFileHandler(
        os.path.join(LOG_DIR, "app.log"),
        maxBytes=1_000_000,
        backupCount=3,
        encoding="utf-8",
    )
    file_handler.setLevel(logging.DEBUG)
    file_handler.setFormatter(formatter)

    logger.addHandler(console_handler)
    logger.addHandler(file_handler)
    return logger


def format_speed(mbps: float, unit: str = "Mbps") -> str:
    """Format a speed value (given in Mbps) into the requested unit."""
    if unit == "Mbps":
        return f"{mbps:.2f} Mbps"
    if unit == "MBps":
        return f"{mbps / 8:.2f} MBps"
    if unit == "Kbps":
        return f"{mbps * 1000:.0f} Kbps"
    return f"{mbps:.2f} Mbps"


def format_ping(ping_ms: float) -> str:
    """Format a ping value in milliseconds."""
    return f"{ping_ms:.0f} ms"


def current_date_str() -> str:
    """Return today's date formatted as DD-MM-YYYY."""
    return datetime.now().strftime("%d-%m-%Y")


def current_time_str() -> str:
    """Return the current time formatted as HH:MM:SS."""
    return datetime.now().strftime("%H:%M:%S")


def is_connected(host: str = "8.8.8.8", port: int = 53, timeout: float = 3.0) -> bool:
    """
    Check internet connectivity by attempting a raw socket connection
    to a well-known DNS server. Fast and does not depend on HTTP.
    """
    try:
        socket.setdefaulttimeout(timeout)
        socket.socket(socket.AF_INET, socket.SOCK_STREAM).connect((host, port))
        return True
    except OSError:
        return False


def get_public_ip_and_isp() -> Tuple[Optional[str], Optional[str]]:
    """
    Look up the caller's public IP address and ISP name using a free
    JSON API. Returns (None, None) on any network failure so callers
    can degrade gracefully instead of crashing.
    """
    try:
        response = requests.get("https://ipinfo.io/json", timeout=5)
        response.raise_for_status()
        data = response.json()
        ip_address = data.get("ip")
        isp = data.get("org")
        return ip_address, isp
    except (requests.RequestException, ValueError):
        return None, None


def bytes_to_mbps(bytes_per_second: float) -> float:
    """Convert a raw bytes/second throughput value into Mbps."""
    return (bytes_per_second * 8) / 1_000_000


def safe_float(value, default: float = 0.0) -> float:
    """Convert a value to float, falling back to a default on failure."""
    try:
        return float(value)
    except (TypeError, ValueError):
        return default
