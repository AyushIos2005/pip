"""
speed_test.py
-------------
Encapsulates all interaction with the `speedtest-cli` library inside a
dedicated worker thread so the Tkinter GUI never blocks. Progress and
completion are reported back to the caller through callback functions
which are invoked from the worker thread - callers (dashboard.py) are
responsible for marshalling any GUI updates back onto the main thread
via `root.after(...)`.
"""

from __future__ import annotations

import threading
import time
from dataclasses import dataclass
from typing import Callable, Optional

import speedtest

from utils import bytes_to_mbps, get_logger, safe_float

logger = get_logger(__name__)


@dataclass
class SpeedTestResult:
    """Immutable snapshot of a completed speed test."""

    download_mbps: float
    upload_mbps: float
    ping_ms: float
    jitter_ms: float
    server_name: str
    server_country: str
    isp: str
    public_ip: str
    network_type: str
    duration_seconds: float


# Callback signatures:
#   on_status(stage: str) -> None            e.g. "Connecting...", "Testing Download..."
#   on_progress(percent: float) -> None       0.0 - 100.0
#   on_complete(result: SpeedTestResult) -> None
#   on_error(message: str) -> None
StatusCallback = Callable[[str], None]
ProgressCallback = Callable[[float], None]
CompleteCallback = Callable[[SpeedTestResult], None]
ErrorCallback = Callable[[str], None]


class SpeedTestWorker:
    """
    Runs a full download/upload/ping speed test on a background
    thread. A new SpeedTestWorker should be created for each test run.
    """

    def __init__(
        self,
        on_status: StatusCallback,
        on_progress: ProgressCallback,
        on_complete: CompleteCallback,
        on_error: ErrorCallback,
    ) -> None:
        self._on_status = on_status
        self._on_progress = on_progress
        self._on_complete = on_complete
        self._on_error = on_error
        self._thread: Optional[threading.Thread] = None
        self._cancelled = threading.Event()

    def start(self) -> None:
        """Start the speed test on a new daemon background thread."""
        self._cancelled.clear()
        self._thread = threading.Thread(target=self._run, daemon=True, name="SpeedTestWorker")
        self._thread.start()

    def cancel(self) -> None:
        """Signal the worker thread to stop reporting further updates."""
        self._cancelled.set()

    # ------------------------------------------------------------------
    # Internal worker logic (executes on the background thread)
    # ------------------------------------------------------------------
    def _run(self) -> None:
        start_time = time.time()
        try:
            self._emit_status("Connecting...")
            self._emit_progress(5)
            client = speedtest.Speedtest(secure=True)

            self._emit_status("Finding Best Server...")
            self._emit_progress(15)
            client.get_servers()
            best_server = client.get_best_server()

            self._emit_status("Testing Download...")
            self._emit_progress(30)
            download_bps = client.download(threads=None, callback=self._download_progress_hook)

            self._emit_status("Testing Upload...")
            self._emit_progress(65)
            upload_bps = client.upload(threads=None, pre_allocate=True, callback=self._upload_progress_hook)

            self._emit_progress(95)
            results = client.results.dict()

            duration = time.time() - start_time

            result = SpeedTestResult(
                download_mbps=bytes_to_mbps(download_bps) if download_bps else safe_float(results.get("download")) / 1_000_000,
                upload_mbps=bytes_to_mbps(upload_bps) if upload_bps else safe_float(results.get("upload")) / 1_000_000,
                ping_ms=safe_float(best_server.get("latency", results.get("ping", 0))),
                jitter_ms=safe_float(results.get("jitter", 0.0)) or self._estimate_jitter(results),
                server_name=str(best_server.get("sponsor", "Unknown Server")),
                server_country=str(best_server.get("country", "Unknown")),
                isp=str(results.get("client", {}).get("isp", "Unknown ISP")),
                public_ip=str(results.get("client", {}).get("ip", "0.0.0.0")),
                network_type="Broadband",
                duration_seconds=duration,
            )

            self._emit_status("Completed")
            self._emit_progress(100)
            if not self._cancelled.is_set():
                self._on_complete(result)

        except speedtest.ConfigRetrievalError:
            logger.exception("Speedtest configuration retrieval failed")
            self._on_error("Could not reach speed test servers. Check your internet connection.")
        except Exception as exc:  # noqa: BLE001 - surface any failure to the UI safely
            logger.exception("Speed test failed")
            self._on_error(f"Speed test failed: {exc}")

    def _download_progress_hook(self, current, total, start=None, end=None) -> None:
        if self._cancelled.is_set():
            return
        fraction = (current / total) if total else 0
        self._emit_progress(30 + fraction * 35)  # 30% -> 65%

    def _upload_progress_hook(self, current, total, start=None, end=None) -> None:
        if self._cancelled.is_set():
            return
        fraction = (current / total) if total else 0
        self._emit_progress(65 + fraction * 30)  # 65% -> 95%

    @staticmethod
    def _estimate_jitter(results: dict) -> float:
        """Fallback jitter estimate if the library does not provide one."""
        ping = safe_float(results.get("ping", 0.0))
        return round(ping * 0.05, 2)

    def _emit_status(self, message: str) -> None:
        if not self._cancelled.is_set():
            self._on_status(message)

    def _emit_progress(self, percent: float) -> None:
        if not self._cancelled.is_set():
            self._on_progress(min(max(percent, 0), 100))
