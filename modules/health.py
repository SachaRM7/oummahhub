# OummahHub — Islamic Community Platform
# Copyright (c) 2026 Sacha Rbone
# MIT License
#
# This software is provided for the benefit of the Oummah (Muslim community).
# May Allah accept our efforts.

from __future__ import annotations

import json
import sqlite3
from dataclasses import dataclass
from pathlib import Path

import httpx


@dataclass(slots=True)
class HealthItem:
    name: str
    ok: bool
    details: str


class HealthService:
    def __init__(self, quran_path: Path, hadith_paths: list[Path], aid_db_path: Path, client: httpx.AsyncClient | None = None) -> None:
        self.quran_path = quran_path
        self.hadith_paths = hadith_paths
        self.aid_db_path = aid_db_path
        self._client = client

    async def run(self) -> list[HealthItem]:
        return [
            await self._check_aladhan(),
            self._check_json_file(self.quran_path, "Quran corpus"),
            *[self._check_json_file(path, f"Hadith corpus ({path.stem})") for path in self.hadith_paths],
            self._check_database(),
        ]

    async def _check_aladhan(self) -> HealthItem:
        close_client = False
        client = self._client
        if client is None:
            client = httpx.AsyncClient(timeout=10.0)
            close_client = True
        try:
            response = await client.get(
                "https://api.aladhan.com/v1/timingsByCity",
                params={"city": "Toulouse", "country": "France", "method": 2},
                follow_redirects=True,
            )
            return HealthItem("Aladhan API", response.status_code == 200, f"HTTP {response.status_code}")
        except Exception as exc:
            return HealthItem("Aladhan API", False, str(exc))
        finally:
            if close_client:
                await client.aclose()

    def _check_json_file(self, path: Path, label: str) -> HealthItem:
        try:
            payload = json.loads(path.read_text(encoding="utf-8"))
            size = len(payload) if isinstance(payload, list) else 1
            return HealthItem(label, True, f"Loaded {size} records")
        except Exception as exc:
            return HealthItem(label, False, str(exc))

    def _check_database(self) -> HealthItem:
        try:
            with sqlite3.connect(self.aid_db_path) as conn:
                conn.execute("SELECT 1")
            return HealthItem("Aid database", True, "SQLite connection OK")
        except Exception as exc:
            return HealthItem("Aid database", False, str(exc))

    @staticmethod
    def format_report(items: list[HealthItem]) -> str:
        lines = ["🩺 OummahHub health report"]
        for item in items:
            icon = "✅" if item.ok else "❌"
            lines.append(f"{icon} {item.name}: {item.details}")
        return "\n".join(lines)
