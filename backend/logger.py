"""
DevDock Logger Module
Maintains daily TXT logs and handles structured log entries.
"""

import logging
import os
from datetime import datetime
from pathlib import Path
from typing import Optional

from config import LOGS_DIR, WEEKLY_REPORTS_DIR

# Configure standard Python logging
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(name)s: %(message)s",
    handlers=[
        logging.StreamHandler(),
    ],
)


class DevDockLogger:
    """Writes structured daily log files for DevDock activity."""

    def __init__(self):
        LOGS_DIR.mkdir(parents=True, exist_ok=True)
        WEEKLY_REPORTS_DIR.mkdir(parents=True, exist_ok=True)

    def _get_log_path(self, dt: Optional[datetime] = None) -> Path:
        """Returns the path to today's log file, creating directories as needed."""
        dt = dt or datetime.now()
        year_dir = LOGS_DIR / str(dt.year) / dt.strftime("%B")
        year_dir.mkdir(parents=True, exist_ok=True)
        return year_dir / f"{dt.strftime('%Y-%m-%d')}.txt"

    def log_entry(
        self,
        filename: str,
        extension: str,
        category: str,
        original_location: str,
        new_location: str,
        action: str,
        status: str,
        rule_based: bool,
        confidence: Optional[int] = None,
        reason: Optional[str] = None,
        error: Optional[str] = None,
    ) -> None:
        """Write a structured log entry to today's log file."""
        now = datetime.now()
        log_path = self._get_log_path(now)

        separator = "─" * 70
        entry = (
            f"\n{separator}\n"
            f"Timestamp        : {now.strftime('%Y-%m-%d %H:%M:%S')}\n"
            f"Filename         : {filename}\n"
            f"Extension        : {extension or 'N/A'}\n"
            f"Category         : {category}\n"
            f"Original Location: {original_location}\n"
            f"New Location     : {new_location or 'N/A'}\n"
            f"Action           : {action}\n"
            f"Status           : {status}\n"
            f"Classification   : {'Rule-Based' if rule_based else 'AI (Groq)'}\n"
        )
        if confidence is not None:
            entry += f"Confidence       : {confidence}%\n"
        if reason:
            entry += f"Reason           : {reason}\n"
        if error:
            entry += f"Error            : {error}\n"
        entry += f"{separator}\n"

        try:
            with open(log_path, "a", encoding="utf-8") as f:
                f.write(entry)
        except Exception as e:
            logging.getLogger(__name__).error(f"Failed to write log: {e}")

    def log_startup(self) -> None:
        log_path = self._get_log_path()
        now = datetime.now()
        header = (
            f"\n{'═' * 70}\n"
            f"  DevDock Started — {now.strftime('%Y-%m-%d %H:%M:%S')}\n"
            f"{'═' * 70}\n"
        )
        try:
            with open(log_path, "a", encoding="utf-8") as f:
                f.write(header)
        except Exception as e:
            logging.getLogger(__name__).error(f"Failed to write startup log: {e}")

    def log_error(self, message: str, context: Optional[str] = None) -> None:
        log_path = self._get_log_path()
        now = datetime.now()
        entry = (
            f"\n[ERROR] {now.strftime('%Y-%m-%d %H:%M:%S')}\n"
            f"  Message : {message}\n"
        )
        if context:
            entry += f"  Context : {context}\n"
        try:
            with open(log_path, "a", encoding="utf-8") as f:
                f.write(entry)
        except Exception as ex:
            logging.getLogger(__name__).error(f"Failed to write error log: {ex}")

    def generate_weekly_report(self, stats: dict) -> Path:
        """Generate a weekly TXT report and return the file path."""
        now = datetime.now()
        report_name = f"weekly_report_{now.strftime('%Y-%W')}.txt"
        report_path = WEEKLY_REPORTS_DIR / report_name

        cat_dist = stats.get("category_distribution", [])
        cat_lines = "\n".join(
            f"  {r['category']:30s}: {r['cnt']}" for r in cat_dist[:15]
        ) or "  No data"

        largest = stats.get("largest_files", [])
        largest_lines = "\n".join(
            f"  {r['filename'][:40]:40s}: {r['file_size'] / 1024 / 1024:.2f} MB"
            for r in largest[:5]
        ) or "  No data"

        content = f"""
{'═' * 70}
  DevDock Weekly Report — Week {now.strftime('%W')}, {now.strftime('%Y')}
  Generated: {now.strftime('%Y-%m-%d %H:%M:%S')}
{'═' * 70}

SUMMARY
{'─' * 40}
  Total Files Organized : {stats.get('total', 0)}
  Today's Files         : {stats.get('today', 0)}
  AI Classified         : {stats.get('ai_classified', 0)}
  Duplicate Files       : {stats.get('duplicates', 0)}
  Sensitive Files       : {stats.get('sensitive', 0)}
  Total Storage Managed : {stats.get('total_size_bytes', 0) / 1024 / 1024:.2f} MB

CATEGORY BREAKDOWN
{'─' * 40}
{cat_lines}

LARGEST FILES
{'─' * 40}
{largest_lines}

{'═' * 70}
"""
        try:
            with open(report_path, "w", encoding="utf-8") as f:
                f.write(content)
        except Exception as e:
            logging.getLogger(__name__).error(f"Failed to write weekly report: {e}")

        return report_path

    def get_log_files(self) -> list:
        """Return a sorted list of all log file paths."""
        logs = []
        if LOGS_DIR.exists():
            for f in LOGS_DIR.rglob("*.txt"):
                logs.append(str(f))
        return sorted(logs, reverse=True)

    def read_log(self, log_path: str) -> str:
        """Read and return contents of a log file."""
        try:
            with open(log_path, "r", encoding="utf-8") as f:
                return f.read()
        except Exception as e:
            return f"Error reading log: {e}"


# Singleton logger
devdock_logger = DevDockLogger()
