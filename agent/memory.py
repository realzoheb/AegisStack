"""
Memory Manager - Persistent conversation and project memory using SQLite.
"""

import sqlite3
import os
import json
from datetime import datetime
from typing import List, Dict, Optional

DB_PATH = os.path.join(os.path.dirname(__file__), "..", "data", "memory.db")


class MemoryManager:
    def __init__(self, db_path: str = DB_PATH):
        self.db_path = os.path.abspath(db_path)
        os.makedirs(os.path.dirname(self.db_path), exist_ok=True)
        self._init_db()

    def _init_db(self):
        """Initialize the SQLite database schema."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("""
                CREATE TABLE IF NOT EXISTS messages (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    role TEXT NOT NULL,
                    content TEXT NOT NULL,
                    timestamp TEXT NOT NULL
                )
            """)
            conn.execute("""
                CREATE TABLE IF NOT EXISTS reports (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    report_type TEXT NOT NULL,
                    title TEXT,
                    content TEXT NOT NULL,
                    timestamp TEXT NOT NULL
                )
            """)
            conn.execute("""
                CREATE TABLE IF NOT EXISTS notes (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    key TEXT UNIQUE NOT NULL,
                    value TEXT NOT NULL,
                    updated_at TEXT NOT NULL
                )
            """)
            conn.commit()

    def save_message(self, role: str, content: str):
        """Save a conversation message."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                "INSERT INTO messages (role, content, timestamp) VALUES (?, ?, ?)",
                (role, content, datetime.now().isoformat())
            )
            conn.commit()

    def get_recent_messages(self, limit: int = 20) -> List[Dict]:
        """Retrieve recent conversation messages."""
        with sqlite3.connect(self.db_path) as conn:
            rows = conn.execute(
                "SELECT role, content, timestamp FROM messages ORDER BY id DESC LIMIT ?",
                (limit,)
            ).fetchall()
        return [{"role": r[0], "content": r[1], "timestamp": r[2]} for r in reversed(rows)]

    def save_report(self, report_type: str, content: str, title: str = ""):
        """Save a generated report."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                "INSERT INTO reports (report_type, title, content, timestamp) VALUES (?, ?, ?, ?)",
                (report_type, title, content, datetime.now().isoformat())
            )
            conn.commit()

    def get_reports(self, report_type: Optional[str] = None) -> List[Dict]:
        """Retrieve saved reports, optionally filtered by type."""
        with sqlite3.connect(self.db_path) as conn:
            if report_type:
                rows = conn.execute(
                    "SELECT id, report_type, title, content, timestamp FROM reports WHERE report_type=? ORDER BY id DESC",
                    (report_type,)
                ).fetchall()
            else:
                rows = conn.execute(
                    "SELECT id, report_type, title, content, timestamp FROM reports ORDER BY id DESC"
                ).fetchall()
        return [{"id": r[0], "type": r[1], "title": r[2], "content": r[3], "timestamp": r[4]} for r in rows]

    def set_note(self, key: str, value: str):
        """Set a persistent key-value note."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute(
                "INSERT INTO notes (key, value, updated_at) VALUES (?, ?, ?) "
                "ON CONFLICT(key) DO UPDATE SET value=excluded.value, updated_at=excluded.updated_at",
                (key, value, datetime.now().isoformat())
            )
            conn.commit()

    def get_note(self, key: str) -> Optional[str]:
        """Get a persistent note by key."""
        with sqlite3.connect(self.db_path) as conn:
            row = conn.execute("SELECT value FROM notes WHERE key=?", (key,)).fetchone()
        return row[0] if row else None

    def clear_messages(self):
        """Clear all conversation messages."""
        with sqlite3.connect(self.db_path) as conn:
            conn.execute("DELETE FROM messages")
            conn.commit()

    def stats(self) -> Dict:
        """Return memory statistics."""
        with sqlite3.connect(self.db_path) as conn:
            msg_count = conn.execute("SELECT COUNT(*) FROM messages").fetchone()[0]
            report_count = conn.execute("SELECT COUNT(*) FROM reports").fetchone()[0]
            note_count = conn.execute("SELECT COUNT(*) FROM notes").fetchone()[0]
        return {
            "messages": msg_count,
            "reports": report_count,
            "notes": note_count,
            "db_path": self.db_path
        }
