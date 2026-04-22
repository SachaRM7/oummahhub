# OummahHub — Islamic Community Platform
# Copyright (c) 2026 Sacha Rbone
# MIT License
#
# This software is provided for the benefit of the Oummah (Muslim community).
# May Allah accept our efforts.

from __future__ import annotations

import math
from dataclasses import dataclass
from datetime import date

import httpx


@dataclass(slots=True)
class PrayerTimesResult:
    city: str
    gregorian_date: str
    hijri_date: str
    timings: dict[str, str]
    source: str

    def format_message(self) -> str:
        ordered = ["Fajr", "Dhuhr", "Asr", "Maghrib", "Isha"]
        body = "\n".join(f"{name}: {self.timings[name]}" for name in ordered)
        return f"🕌 Prayer Times for {self.city} — {self.hijri_date}\n{body}\nSource: {self.source}"


class PrayerTimeService:
    def __init__(self, latitude: float, longitude: float, city: str, method: int = 2, client: httpx.AsyncClient | None = None) -> None:
        self.latitude = latitude
        self.longitude = longitude
        self.city = city
        self.method = method
        self._client = client

    async def get_today_prayer_times(self, target_date: date | None = None) -> PrayerTimesResult:
        target_date = target_date or date.today()
        try:
            api_result = await self._fetch_from_api(target_date)
            if api_result is not None:
                return api_result
        except Exception:
            pass
        return self._fallback_times(target_date)

    async def _fetch_from_api(self, target_date: date) -> PrayerTimesResult | None:
        close_client = False
        client = self._client
        if client is None:
            client = httpx.AsyncClient(timeout=10.0)
            close_client = True
        try:
            response = await client.get(
                "https://api.aladhan.com/v1/timings",
                params={
                    "latitude": self.latitude,
                    "longitude": self.longitude,
                    "method": self.method,
                    "date": target_date.strftime("%d-%m-%Y"),
                },
                follow_redirects=True,
            )
            response.raise_for_status()
            payload = response.json().get("data", {})
            timings = payload.get("timings", {})
            hijri = payload.get("date", {}).get("hijri", {})
            hijri_date = " ".join(filter(None, [hijri.get("day"), hijri.get("month", {}).get("en"), hijri.get("year")]))
            cleaned = {
                "Fajr": self._clean_time(timings.get("Fajr", "05:00")),
                "Dhuhr": self._clean_time(timings.get("Dhuhr", "13:00")),
                "Asr": self._clean_time(timings.get("Asr", "17:00")),
                "Maghrib": self._clean_time(timings.get("Maghrib", "20:00")),
                "Isha": self._clean_time(timings.get("Isha", "21:30")),
            }
            return PrayerTimesResult(
                city=self.city,
                gregorian_date=target_date.isoformat(),
                hijri_date=hijri_date or "Hijri date unavailable",
                timings=cleaned,
                source="Aladhan API",
            )
        finally:
            if close_client:
                await client.aclose()

    def _fallback_times(self, target_date: date) -> PrayerTimesResult:
        day_of_year = target_date.timetuple().tm_yday
        seasonal_shift = math.cos(((day_of_year - 172) / 365.0) * 2 * math.pi)
        sunrise_minutes = 420 - int(55 * seasonal_shift)
        sunset_minutes = 1140 + int(80 * seasonal_shift)
        solar_noon = (sunrise_minutes + sunset_minutes) // 2
        fajr = sunrise_minutes - 95
        dhuhr = solar_noon + 4
        asr = dhuhr + max(180, (sunset_minutes - dhuhr) // 2)
        maghrib = sunset_minutes
        isha = sunset_minutes + 95
        timings = {
            "Fajr": self._minutes_to_time(fajr),
            "Dhuhr": self._minutes_to_time(dhuhr),
            "Asr": self._minutes_to_time(asr),
            "Maghrib": self._minutes_to_time(maghrib),
            "Isha": self._minutes_to_time(isha),
        }
        return PrayerTimesResult(
            city=self.city,
            gregorian_date=target_date.isoformat(),
            hijri_date=self._approximate_hijri_date(target_date),
            timings=timings,
            source="Deterministic fallback calculator",
        )

    @staticmethod
    def _clean_time(value: str) -> str:
        return value.split(" ")[0][:5]

    @staticmethod
    def _minutes_to_time(total_minutes: int) -> str:
        minutes = total_minutes % (24 * 60)
        return f"{minutes // 60:02d}:{minutes % 60:02d}"

    @staticmethod
    def _approximate_hijri_date(target_date: date) -> str:
        civil_epoch = date(622, 7, 19).toordinal()
        days = target_date.toordinal() - civil_epoch
        year = int((30 * days + 10646) / 10631)
        start_of_year = civil_epoch + (year - 1) * 354 + (3 + 11 * year) // 30
        day_of_year = days - (start_of_year - civil_epoch)
        month_lengths = [30, 29, 30, 29, 30, 29, 30, 29, 30, 29, 30, 29]
        month_names = [
            "Muharram",
            "Safar",
            "Rabi al-Awwal",
            "Rabi al-Thani",
            "Jumada al-Awwal",
            "Jumada al-Thani",
            "Rajab",
            "Sha'ban",
            "Ramadan",
            "Shawwal",
            "Dhu al-Qadah",
            "Dhu al-Hijjah",
        ]
        if ((11 * year + 14) % 30) < 11:
            month_lengths[-1] = 30
        month = 0
        while month < len(month_lengths) and day_of_year >= month_lengths[month]:
            day_of_year -= month_lengths[month]
            month += 1
        month = min(month, len(month_names) - 1)
        day = max(1, day_of_year + 1)
        return f"{day} {month_names[month]} {year}"
