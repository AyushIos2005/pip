"""
reports.py
----------
Generates exportable reports (CSV, PDF, TXT) summarizing speed test
history. PDF reports include the app logo, generation date, a
download/upload trend graph rendered via matplotlib, a results table,
and a footer - built with reportlab's Platypus layout engine.
"""

from __future__ import annotations

import os
from datetime import datetime
from typing import Optional

import matplotlib
matplotlib.use("Agg")  # Headless rendering - required before pyplot import
import matplotlib.pyplot as plt
import pandas as pd
from reportlab.lib import colors
from reportlab.lib.pagesizes import A4
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import cm
from reportlab.platypus import (
    Image,
    Paragraph,
    SimpleDocTemplate,
    Spacer,
    Table,
    TableStyle,
)

from utils import ASSETS_DIR, REPORTS_DIR, get_logger

logger = get_logger(__name__)


class ReportGenerator:
    """Builds CSV, TXT, and PDF export reports from a history DataFrame."""

    def __init__(self, output_dir: Optional[str] = None) -> None:
        self.output_dir = output_dir or REPORTS_DIR
        os.makedirs(self.output_dir, exist_ok=True)

    # ------------------------------------------------------------------
    # CSV
    # ------------------------------------------------------------------
    def export_csv(self, df: pd.DataFrame, filename: Optional[str] = None) -> str:
        """Export the given DataFrame to a timestamped CSV file."""
        filename = filename or f"speedtest_report_{self._timestamp()}.csv"
        path = os.path.join(self.output_dir, filename)
        df.to_csv(path, index=False)
        logger.info("CSV report saved to %s", path)
        return path

    # ------------------------------------------------------------------
    # TXT
    # ------------------------------------------------------------------
    def export_txt(self, df: pd.DataFrame, filename: Optional[str] = None) -> str:
        """Export the given DataFrame as a plain-text formatted report."""
        filename = filename or f"speedtest_report_{self._timestamp()}.txt"
        path = os.path.join(self.output_dir, filename)

        lines = [
            "=" * 60,
            "  INTERNET SPEED TESTER PRO - REPORT",
            f"  Generated: {datetime.now().strftime('%d-%m-%Y %H:%M:%S')}",
            "=" * 60,
            "",
        ]
        if df.empty:
            lines.append("No history records available.")
        else:
            for _, row in df.iterrows():
                lines.append(
                    f"[{row.get('Date', '')} {row.get('Time', '')}] "
                    f"Down: {row.get('Download', 0)} Mbps | "
                    f"Up: {row.get('Upload', 0)} Mbps | "
                    f"Ping: {row.get('Ping', 0)} ms | "
                    f"Jitter: {row.get('Jitter', 0)} ms | "
                    f"ISP: {row.get('ISP', '')} | "
                    f"Server: {row.get('Server', '')} | "
                    f"IP: {row.get('IP', '')}"
                )
            lines.append("")
            lines.append(f"Total Records: {len(df)}")
            lines.append(f"Average Download: {df['Download'].mean():.2f} Mbps")
            lines.append(f"Average Upload: {df['Upload'].mean():.2f} Mbps")
            lines.append(f"Average Ping: {df['Ping'].mean():.2f} ms")

        with open(path, "w", encoding="utf-8") as f:
            f.write("\n".join(lines))

        logger.info("TXT report saved to %s", path)
        return path

    # ------------------------------------------------------------------
    # PDF
    # ------------------------------------------------------------------
    def export_pdf(self, df: pd.DataFrame, filename: Optional[str] = None) -> str:
        """
        Export the given DataFrame as a polished PDF report containing
        a logo, generation date, a trend graph, a results table, and
        a footer.
        """
        filename = filename or f"speedtest_report_{self._timestamp()}.pdf"
        path = os.path.join(self.output_dir, filename)

        doc = SimpleDocTemplate(
            path,
            pagesize=A4,
            topMargin=1.5 * cm,
            bottomMargin=1.5 * cm,
            leftMargin=1.5 * cm,
            rightMargin=1.5 * cm,
        )

        styles = getSampleStyleSheet()
        title_style = ParagraphStyle(
            "TitleStyle", parent=styles["Title"], textColor=colors.HexColor("#2563EB")
        )
        normal_style = styles["Normal"]
        footer_style = ParagraphStyle(
            "FooterStyle", parent=styles["Normal"], fontSize=8, textColor=colors.grey
        )

        elements = []

        # Logo (optional - only included if present in assets/)
        logo_path = os.path.join(ASSETS_DIR, "logo.png")
        if os.path.exists(logo_path):
            elements.append(Image(logo_path, width=3 * cm, height=3 * cm))
            elements.append(Spacer(1, 0.3 * cm))

        elements.append(Paragraph("Internet Speed Tester Pro - Report", title_style))
        elements.append(
            Paragraph(
                f"Generated on {datetime.now().strftime('%d-%m-%Y %H:%M:%S')}",
                normal_style,
            )
        )
        elements.append(Spacer(1, 0.5 * cm))

        # Trend graph
        if not df.empty and {"Download", "Upload"}.issubset(df.columns):
            graph_path = self._build_trend_graph(df)
            if graph_path:
                elements.append(Image(graph_path, width=16 * cm, height=7 * cm))
                elements.append(Spacer(1, 0.5 * cm))

        # Results table
        elements.append(Paragraph("Test Results", styles["Heading2"]))
        elements.append(Spacer(1, 0.2 * cm))
        elements.append(self._build_table(df))
        elements.append(Spacer(1, 0.8 * cm))

        # Footer
        elements.append(
            Paragraph(
                "Generated by Internet Speed Tester Pro | https://github.com/yourusername/internet-speed-tester-pro",
                footer_style,
            )
        )

        doc.build(elements)
        logger.info("PDF report saved to %s", path)
        return path

    def _build_table(self, df: pd.DataFrame) -> Table:
        """Build a styled reportlab Table from a history DataFrame."""
        if df.empty:
            data = [["No history records available."]]
            table = Table(data)
            table.setStyle(TableStyle([("TEXTCOLOR", (0, 0), (-1, -1), colors.grey)]))
            return table

        display_df = df.tail(25)  # Keep PDF readable - most recent 25 rows
        data = [list(display_df.columns)] + display_df.astype(str).values.tolist()

        table = Table(data, repeatRows=1)
        table.setStyle(
            TableStyle(
                [
                    ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#2563EB")),
                    ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
                    ("FONTSIZE", (0, 0), (-1, -1), 7),
                    ("GRID", (0, 0), (-1, -1), 0.5, colors.HexColor("#E2E8F0")),
                    ("ROWBACKGROUNDS", (0, 1), (-1, -1), [colors.white, colors.HexColor("#F1F5F9")]),
                    ("ALIGN", (0, 0), (-1, -1), "CENTER"),
                    ("VALIGN", (0, 0), (-1, -1), "MIDDLE"),
                ]
            )
        )
        return table

    def _build_trend_graph(self, df: pd.DataFrame) -> Optional[str]:
        """Render a download/upload trend line chart to a temp PNG file."""
        try:
            fig, ax = plt.subplots(figsize=(8, 3.2), dpi=150)
            ax.plot(df["Download"].tail(30).values, label="Download (Mbps)", color="#2563EB", linewidth=2)
            ax.plot(df["Upload"].tail(30).values, label="Upload (Mbps)", color="#10B981", linewidth=2)
            ax.set_title("Speed Trend (Most Recent Tests)")
            ax.set_ylabel("Mbps")
            ax.legend(loc="upper right", fontsize=8)
            ax.grid(alpha=0.3)
            fig.tight_layout()

            graph_path = os.path.join(self.output_dir, "_trend_graph_tmp.png")
            fig.savefig(graph_path)
            plt.close(fig)
            return graph_path
        except Exception as exc:  # noqa: BLE001
            logger.warning("Failed to build trend graph: %s", exc)
            return None

    @staticmethod
    def _timestamp() -> str:
        return datetime.now().strftime("%Y%m%d_%H%M%S")
