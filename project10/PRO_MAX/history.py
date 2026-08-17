"""
history.py
----------
Manages the persistent record of past speed test results stored in
history/history.csv. Uses pandas for convenient search, sort and
filter operations, while writing/reading through plain CSV so the
file stays human-readable and portable.
"""

from __future__ import annotations

import csv
import os
from dataclasses import asdict, dataclass
from typing import List, Optional

import pandas as pd

from speed_test import SpeedTestResult
from utils import HISTORY_DIR, current_date_str, current_time_str, get_logger

logger = get_logger(__name__)

HISTORY_COLUMNS = [
    "Date",
    "Time",
    "Download",
    "Upload",
    "Ping",
    "Jitter",
    "ISP",
    "Server",
    "IP",
]


@dataclass
class HistoryRecord:
    """Single row of speed test history."""

    Date: str
    Time: str
    Download: float
    Upload: float
    Ping: float
    Jitter: float
    ISP: str
    Server: str
    IP: str


class HistoryManager:
    """Reads, writes, searches, and exports the speed test history CSV."""

    def __init__(self, file_path: Optional[str] = None, max_records: int = 1000) -> None:
        self.file_path = file_path or os.path.join(HISTORY_DIR, "history.csv")
        self.max_records = max_records
        self._ensure_file_exists()

    def _ensure_file_exists(self) -> None:
        """Create the CSV file with a header row if it does not exist."""
        os.makedirs(os.path.dirname(self.file_path), exist_ok=True)
        if not os.path.exists(self.file_path):
            with open(self.file_path, mode="w", newline="", encoding="utf-8") as f:
                writer = csv.writer(f)
                writer.writerow(HISTORY_COLUMNS)

    def add_result(self, result: SpeedTestResult) -> HistoryRecord:
        """Append a completed speed test result as a new history row."""
        record = HistoryRecord(
            Date=current_date_str(),
            Time=current_time_str(),
            Download=round(result.download_mbps, 2),
            Upload=round(result.upload_mbps, 2),
            Ping=round(result.ping_ms, 2),
            Jitter=round(result.jitter_ms, 2),
            ISP=result.isp,
            Server=result.server_name,
            IP=result.public_ip,
        )
        with open(self.file_path, mode="a", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(list(asdict(record).values()))
        self._trim_if_needed()
        logger.info("History record added: %s", record)
        return record

    def _trim_if_needed(self) -> None:
        """Keep the history file within max_records by dropping oldest rows."""
        df = self.load_dataframe()
        if len(df) > self.max_records:
            df = df.tail(self.max_records)
            df.to_csv(self.file_path, index=False)

    def load_dataframe(self) -> pd.DataFrame:
        """Load the full history as a pandas DataFrame."""
        try:
            return pd.read_csv(self.file_path)
        except pd.errors.EmptyDataError:
            return pd.DataFrame(columns=HISTORY_COLUMNS)

    def load_records(self) -> List[HistoryRecord]:
        """Load the full history as a list of HistoryRecord objects."""
        df = self.load_dataframe()
        return [HistoryRecord(**row) for row in df.to_dict(orient="records")]

    def search(self, keyword: str) -> pd.DataFrame:
        """Case-insensitive search across ISP, Server, and IP columns."""
        df = self.load_dataframe()
        if not keyword:
            return df
        keyword_lower = keyword.lower()
        mask = (
            df["ISP"].astype(str).str.lower().str.contains(keyword_lower)
            | df["Server"].astype(str).str.lower().str.contains(keyword_lower)
            | df["IP"].astype(str).str.lower().str.contains(keyword_lower)
        )
        return df[mask]

    def sort(self, column: str, ascending: bool = True) -> pd.DataFrame:
        """Sort the history by the given column name."""
        df = self.load_dataframe()
        if column not in df.columns:
            return df
        return df.sort_values(by=column, ascending=ascending)

    def delete_record(self, index: int) -> bool:
        """Delete a single record by its row index (0-based)."""
        df = self.load_dataframe()
        if index < 0 or index >= len(df):
            return False
        df = df.drop(df.index[index])
        df.to_csv(self.file_path, index=False)
        logger.info("History record at index %d deleted", index)
        return True

    def clear_all(self) -> None:
        """Delete every history record, keeping only the header row."""
        with open(self.file_path, mode="w", newline="", encoding="utf-8") as f:
            writer = csv.writer(f)
            writer.writerow(HISTORY_COLUMNS)
        logger.info("History cleared")

    def export_csv(self, destination_path: str) -> str:
        """Export the current history to a chosen CSV path."""
        df = self.load_dataframe()
        df.to_csv(destination_path, index=False)
        logger.info("History exported to CSV: %s", destination_path)
        return destination_path
