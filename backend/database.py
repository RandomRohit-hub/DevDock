"""
DevDock Database Module
SQLite-backed persistence layer for all file records.
"""

import sqlite3
import logging
import hashlib
from pathlib import Path
from typing import Any, Dict, List, Optional, Tuple
from datetime import datetime
from contextlib import contextmanager

from config import DB_FILE

logger = logging.getLogger(__name__)


class DatabaseManager:
    """Thread-safe SQLite database manager for DevDock."""

    def __init__(self, db_path: Path = DB_FILE):
        self.db_path = db_path
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._init_db()

    @contextmanager
    def _conn(self):
        conn = sqlite3.connect(str(self.db_path), check_same_thread=False)
        conn.row_factory = sqlite3.Row
        conn.execute("PRAGMA journal_mode=WAL")
        conn.execute("PRAGMA foreign_keys=ON")
        try:
            yield conn
            conn.commit()
        except Exception:
            conn.rollback()
            raise
        finally:
            conn.close()

    def _init_db(self) -> None:
        """Create all required tables if they don't exist."""
        with self._conn() as conn:
            conn.executescript("""
                CREATE TABLE IF NOT EXISTS file_records (
                    id              INTEGER PRIMARY KEY AUTOINCREMENT,
                    filename        TEXT NOT NULL,
                    extension       TEXT,
                    sha256_hash     TEXT,
                    category        TEXT,
                    original_path   TEXT NOT NULL,
                    destination_path TEXT,
                    timestamp       TEXT NOT NULL,
                    ai_used         INTEGER DEFAULT 0,
                    confidence      INTEGER,
                    reason          TEXT,
                    status          TEXT DEFAULT 'organized',
                    rule_based      INTEGER DEFAULT 1,
                    is_sensitive    INTEGER DEFAULT 0,
                    is_duplicate    INTEGER DEFAULT 0,
                    duplicate_of    TEXT,
                    file_size       INTEGER DEFAULT 0,
                    restored        INTEGER DEFAULT 0
                );

                CREATE TABLE IF NOT EXISTS custom_rules (
                    id          INTEGER PRIMARY KEY AUTOINCREMENT,
                    name        TEXT NOT NULL,
                    condition   TEXT NOT NULL,
                    value       TEXT NOT NULL,
                    destination TEXT NOT NULL,
                    enabled     INTEGER DEFAULT 1,
                    created_at  TEXT NOT NULL
                );

                CREATE TABLE IF NOT EXISTS duplicate_groups (
                    id          INTEGER PRIMARY KEY AUTOINCREMENT,
                    sha256_hash TEXT NOT NULL UNIQUE,
                    count       INTEGER DEFAULT 2,
                    detected_at TEXT NOT NULL
                );

                CREATE TABLE IF NOT EXISTS activity_log (
                    id          INTEGER PRIMARY KEY AUTOINCREMENT,
                    timestamp   TEXT NOT NULL,
                    action      TEXT NOT NULL,
                    filename    TEXT,
                    details     TEXT,
                    status      TEXT DEFAULT 'success'
                );

                CREATE INDEX IF NOT EXISTS idx_records_hash ON file_records(sha256_hash);
                CREATE INDEX IF NOT EXISTS idx_records_timestamp ON file_records(timestamp);
                CREATE INDEX IF NOT EXISTS idx_records_category ON file_records(category);
                CREATE INDEX IF NOT EXISTS idx_records_filename ON file_records(filename);
            """)
        logger.info("Database initialized at %s", self.db_path)

    # ─── File Records ─────────────────────────────────────────────────────────

    def insert_record(self, record: Dict[str, Any]) -> int:
        """Insert a new file record and return its ID."""
        sql = """
            INSERT INTO file_records
                (filename, extension, sha256_hash, category, original_path,
                 destination_path, timestamp, ai_used, confidence, reason,
                 status, rule_based, is_sensitive, is_duplicate, duplicate_of,
                 file_size)
            VALUES
                (:filename, :extension, :sha256_hash, :category, :original_path,
                 :destination_path, :timestamp, :ai_used, :confidence, :reason,
                 :status, :rule_based, :is_sensitive, :is_duplicate, :duplicate_of,
                 :file_size)
        """
        with self._conn() as conn:
            cursor = conn.execute(sql, record)
            return cursor.lastrowid

    def get_record_by_id(self, record_id: int) -> Optional[Dict]:
        with self._conn() as conn:
            row = conn.execute(
                "SELECT * FROM file_records WHERE id = ?", (record_id,)
            ).fetchone()
            return dict(row) if row else None

    def get_records(
        self,
        limit: int = 100,
        offset: int = 0,
        category: Optional[str] = None,
        search: Optional[str] = None,
        date_from: Optional[str] = None,
        date_to: Optional[str] = None,
        ai_only: bool = False,
        duplicates_only: bool = False,
        sensitive_only: bool = False,
    ) -> List[Dict]:
        conditions, params = [], []
        if category:
            conditions.append("category LIKE ?")
            params.append(f"%{category}%")
        if search:
            conditions.append("(filename LIKE ? OR category LIKE ? OR original_path LIKE ?)")
            params.extend([f"%{search}%"] * 3)
        if date_from:
            conditions.append("timestamp >= ?")
            params.append(date_from)
        if date_to:
            conditions.append("timestamp <= ?")
            params.append(date_to)
        if ai_only:
            conditions.append("ai_used = 1")
        if duplicates_only:
            conditions.append("is_duplicate = 1")
        if sensitive_only:
            conditions.append("is_sensitive = 1")

        where = ("WHERE " + " AND ".join(conditions)) if conditions else ""
        sql = f"SELECT * FROM file_records {where} ORDER BY timestamp DESC LIMIT ? OFFSET ?"
        params.extend([limit, offset])

        with self._conn() as conn:
            rows = conn.execute(sql, params).fetchall()
            return [dict(r) for r in rows]

    def get_record_by_hash(self, sha256: str) -> Optional[Dict]:
        with self._conn() as conn:
            row = conn.execute(
                "SELECT * FROM file_records WHERE sha256_hash = ?", (sha256,)
            ).fetchone()
            return dict(row) if row else None

    def update_record_status(self, record_id: int, status: str, destination: Optional[str] = None) -> None:
        with self._conn() as conn:
            if destination:
                conn.execute(
                    "UPDATE file_records SET status=?, destination_path=? WHERE id=?",
                    (status, destination, record_id),
                )
            else:
                conn.execute(
                    "UPDATE file_records SET status=? WHERE id=?",
                    (status, record_id),
                )

    def mark_restored(self, record_id: int) -> None:
        with self._conn() as conn:
            conn.execute("UPDATE file_records SET restored=1, status='restored' WHERE id=?", (record_id,))

    def count_records(self) -> int:
        with self._conn() as conn:
            return conn.execute("SELECT COUNT(*) FROM file_records").fetchone()[0]

    # ─── Statistics ───────────────────────────────────────────────────────────

    def get_stats(self) -> Dict[str, Any]:
        with self._conn() as conn:
            total = conn.execute("SELECT COUNT(*) FROM file_records").fetchone()[0]
            today = datetime.now().strftime("%Y-%m-%d")
            today_count = conn.execute(
                "SELECT COUNT(*) FROM file_records WHERE timestamp LIKE ?", (f"{today}%",)
            ).fetchone()[0]
            ai_count = conn.execute(
                "SELECT COUNT(*) FROM file_records WHERE ai_used=1"
            ).fetchone()[0]
            duplicate_count = conn.execute(
                "SELECT COUNT(*) FROM file_records WHERE is_duplicate=1"
            ).fetchone()[0]
            sensitive_count = conn.execute(
                "SELECT COUNT(*) FROM file_records WHERE is_sensitive=1"
            ).fetchone()[0]
            category_dist = conn.execute(
                "SELECT category, COUNT(*) as cnt FROM file_records GROUP BY category ORDER BY cnt DESC LIMIT 20"
            ).fetchall()
            total_size = conn.execute(
                "SELECT SUM(file_size) FROM file_records"
            ).fetchone()[0] or 0
            largest_files = conn.execute(
                "SELECT filename, category, file_size FROM file_records ORDER BY file_size DESC LIMIT 10"
            ).fetchall()
            weekly = conn.execute(
                "SELECT DATE(timestamp) as day, COUNT(*) as cnt FROM file_records "
                "WHERE timestamp >= DATE('now','-7 days') GROUP BY day ORDER BY day"
            ).fetchall()
            monthly = conn.execute(
                "SELECT strftime('%Y-%m', timestamp) as month, COUNT(*) as cnt "
                "FROM file_records GROUP BY month ORDER BY month DESC LIMIT 12"
            ).fetchall()

        return {
            "total": total,
            "today": today_count,
            "ai_classified": ai_count,
            "duplicates": duplicate_count,
            "sensitive": sensitive_count,
            "total_size_bytes": total_size,
            "category_distribution": [dict(r) for r in category_dist],
            "largest_files": [dict(r) for r in largest_files],
            "weekly_activity": [dict(r) for r in weekly],
            "monthly_activity": [dict(r) for r in monthly],
        }

    # ─── Custom Rules ─────────────────────────────────────────────────────────

    def get_custom_rules(self) -> List[Dict]:
        with self._conn() as conn:
            rows = conn.execute("SELECT * FROM custom_rules WHERE enabled=1 ORDER BY id").fetchall()
            return [dict(r) for r in rows]

    def add_custom_rule(self, name: str, condition: str, value: str, destination: str) -> int:
        with self._conn() as conn:
            cursor = conn.execute(
                "INSERT INTO custom_rules (name, condition, value, destination, created_at) VALUES (?,?,?,?,?)",
                (name, condition, value, destination, datetime.now().isoformat()),
            )
            return cursor.lastrowid

    def delete_custom_rule(self, rule_id: int) -> None:
        with self._conn() as conn:
            conn.execute("DELETE FROM custom_rules WHERE id=?", (rule_id,))

    def toggle_custom_rule(self, rule_id: int, enabled: bool) -> None:
        with self._conn() as conn:
            conn.execute("UPDATE custom_rules SET enabled=? WHERE id=?", (int(enabled), rule_id))

    # ─── Activity Log ─────────────────────────────────────────────────────────

    def log_activity(self, action: str, filename: Optional[str] = None,
                     details: Optional[str] = None, status: str = "success") -> None:
        with self._conn() as conn:
            conn.execute(
                "INSERT INTO activity_log (timestamp, action, filename, details, status) VALUES (?,?,?,?,?)",
                (datetime.now().isoformat(), action, filename, details, status),
            )

    def get_recent_activity(self, limit: int = 50) -> List[Dict]:
        with self._conn() as conn:
            rows = conn.execute(
                "SELECT * FROM activity_log ORDER BY timestamp DESC LIMIT ?", (limit,)
            ).fetchall()
            return [dict(r) for r in rows]

    # ─── Duplicate Groups ─────────────────────────────────────────────────────

    def register_duplicate(self, sha256: str) -> None:
        with self._conn() as conn:
            existing = conn.execute(
                "SELECT id FROM duplicate_groups WHERE sha256_hash=?", (sha256,)
            ).fetchone()
            if existing:
                conn.execute(
                    "UPDATE duplicate_groups SET count=count+1 WHERE sha256_hash=?", (sha256,)
                )
            else:
                conn.execute(
                    "INSERT INTO duplicate_groups (sha256_hash, count, detected_at) VALUES (?,?,?)",
                    (sha256, 2, datetime.now().isoformat()),
                )

    def get_duplicate_groups(self) -> List[Dict]:
        with self._conn() as conn:
            rows = conn.execute(
                "SELECT dg.*, GROUP_CONCAT(fr.filename, ' | ') as filenames "
                "FROM duplicate_groups dg "
                "LEFT JOIN file_records fr ON fr.sha256_hash=dg.sha256_hash "
                "GROUP BY dg.sha256_hash ORDER BY dg.count DESC"
            ).fetchall()
            return [dict(r) for r in rows]


# Singleton database instance
db = DatabaseManager()
