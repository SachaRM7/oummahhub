# OummahHub — Islamic Community Platform
# Copyright (c) 2026 Sacha Rbone
# MIT License
#
# This software is provided for the benefit of the Oummah (Muslim community).
# May Allah accept our efforts.

from __future__ import annotations

from dataclasses import dataclass
from datetime import date

import httpx

from .prayer_times import PrayerTimeService


@dataclass(slots=True)
class HijriDate:
    gregorian_date: str
    hijri_date: str
    source: str

    def format_message(self) -> str:
        return f"🗓️ Hijri date for {self.gregorian_date}: {self.hijri_date} ({self.source})"


class HijriCalendarService:
    def __init__(self, latitude: float, longitude: float, method: int = 2, client: httpx.AsyncClient | None = None) -> None:
        self.latitude = latitude
        self.longitude = longitude
        self.method = method
        self._client = client

    async def get_current_hijri_date(self, target_date: date | None = None) -> HijriDate:
        target_date = target_date or date.today()
        close_client = False
        client = self._client
        if client is None:
            client = httpx.AsyncClient(timeout=10.0)
            close_client = True
        try:
            response = await client.get(
                "https://api.aladhan.com/v1/gToH",
                params={"date": target_date.strftime("%d-%m-%Y")},
                follow_redirects=True,
            )
            response.raise_for_status()
            payload = response.json().get("data", {}).get("hijri", {})
            parts = [payload.get("day"), payload.get("month", {}).get("en"), payload.get("year")]
            hijri_date = " ".join(part for part in parts if part)
            if hijri_date:
                return HijriDate(target_date.isoformat(), hijri_date, "Aladhan API")
        except Exception:
            pass
        finally:
            if close_client:
                await client.aclose()
        fallback = PrayerTimeService._approximate_hijri_date(target_date)
        return HijriDate(target_date.isoformat(), fallback, "Tabular fallback")

    def get_upcoming_events(self, hijri_date: str) -> list[str]:
        events = {
            "Ramadan": "Ramadan is the month of fasting and Quran reflection.",
            "Shawwal": "Shawwal includes Eid al-Fitr at its beginning.",
            "Dhu al-Hijjah": "Dhu al-Hijjah includes Hajj and Eid al-Adha.",
            "Rajab": "Rajab is one of the sacred months.",
        }
        return [message for month, message in events.items() if month in hijri_date] or ["No major upcoming event detected in the lightweight MVP event map."]
