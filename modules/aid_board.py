# OummahHub — Islamic Community Platform
# Copyright (c) 2026 Sacha Rbone
# MIT License
#
# This software is provided for the benefit of the Oummah (Muslim community).
# May Allah accept our efforts.

from __future__ import annotations

import sqlite3
from dataclasses import dataclass
from pathlib import Path


@dataclass(slots=True)
class AidEntry:
    entry_id: int
    entry_type: str
    description: str
    amount: str
    requester: str
    city: str
    status: str
    created_at: str

    def format_message(self) -> str:
        amount_part = f" | Amount: {self.amount}" if self.amount else ""
        city_part = f" | City: {self.city}" if self.city else ""
        return (
            f"#{self.entry_id} [{self.entry_type}] {self.description}{amount_part}{city_part} "
            f"| By: {self.requester} | Status: {self.status} | Created: {self.created_at}"
        )


class AidBoardService:
    def __init__(self, db_path: Path) -> None:
        self.db_path = db_path
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self._ensure_schema()

    def _connect(self) -> sqlite3.Connection:
        return sqlite3.connect(self.db_path)

    def _ensure_schema(self) -> None:
        with self._connect() as conn:
            conn.execute(
                "CREATE TABLE IF NOT EXISTS aid_entries (id INTEGER PRIMARY KEY AUTOINCREMENT, entry_type TEXT NOT NULL, description TEXT NOT NULL, amount TEXT DEFAULT '', requester TEXT NOT NULL, city TEXT DEFAULT '', status TEXT NOT NULL DEFAULT 'pending', created_at TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP)"
            )
            conn.commit()

    def create_entry(self, entry_type: str, description: str, requester: str, amount: str = "", city: str = "") -> AidEntry:
        with self._connect() as conn:
            cursor = conn.execute(
                "INSERT INTO aid_entries (entry_type, description, amount, requester, city) VALUES (?, ?, ?, ?, ?)",
                (entry_type, description.strip(), amount.strip(), requester.strip(), city.strip()),
            )
            conn.commit()
            entry_id = int(cursor.lastrowid)
        return self.get_entry(entry_id)

    def get_entry(self, entry_id: int) -> AidEntry:
        with self._connect() as conn:
            row = conn.execute(
                "SELECT id, entry_type, description, amount, requester, city, status, created_at FROM aid_entries WHERE id = ?",
                (entry_id,),
            ).fetchone()
        if row is None:
            raise KeyError(f"Aid entry {entry_id} not found")
        return AidEntry(*row)

    def list_active_entries(self) -> list[AidEntry]:
        with self._connect() as conn:
            rows = conn.execute(
                "SELECT id, entry_type, description, amount, requester, city, status, created_at FROM aid_entries WHERE status = 'pending' ORDER BY id ASC"
            ).fetchall()
        return [AidEntry(*row) for row in rows]

    def close_entry(self, entry_id: int) -> AidEntry:
        with self._connect() as conn:
            conn.execute("UPDATE aid_entries SET status = ? WHERE id = ?", ("closed", entry_id))
            conn.commit()
        return self.get_entry(entry_id)
