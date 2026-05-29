# OummahHub — Islamic Community Platform
# Copyright (c) 2026 Sacha Rbone
# MIT License
#
# This software is provided for the benefit of the Oummah (Muslim community).
# May Allah accept our efforts.

from __future__ import annotations

import asyncio
import tempfile
import unittest
from datetime import date
from pathlib import Path

from modules.aid_board import AidBoardService
from modules.dhikr import DhikrService
from modules.hijri_calendar import HijriCalendarService
from modules.prayer_times import PrayerTimeService
from modules.quran_search import QuranSearchService


class OummahHubTests(unittest.TestCase):
    def setUp(self) -> None:
        self.tmpdir = tempfile.TemporaryDirectory()
        data_dir = Path(self.tmpdir.name)
        (data_dir / "quran.json").write_text(
            "[{\"surah\": 1, \"ayah\": 1, \"surah_name\": \"Al-Fatihah\", \"arabic\": \"بِسْمِ اللَّهِ الرَّحْمَٰنِ الرَّحِيمِ\", \"transliteration\": \"Bismillahir Rahmanir Rahim\", \"translation\": \"In the name of Allah, the Entirely Merciful, the Especially Merciful.\"}]",
            encoding="utf-8",
        )
        (data_dir / "hadith_bukhari.json").write_text(
            "[{\"collection\": \"Bukhari\", \"title\": \"Intentions\", \"text\": \"إِنَّمَا الأَعْمَالُ بِالنِّيَّاتِ\", \"translation\": \"Actions are judged by intentions.\"}]",
            encoding="utf-8",
        )
        (data_dir / "hadith_muslim.json").write_text(
            "[{\"collection\": \"Muslim\", \"title\": \"Mercy\", \"text\": \"الرَّاحِمُونَ يَرْحَمُهُمُ الرَّحْمَنُ\", \"translation\": \"The merciful are shown mercy by the Most Merciful.\"}]",
            encoding="utf-8",
        )
        self.search_service = QuranSearchService(
            data_dir / "quran.json",
            [data_dir / "hadith_bukhari.json", data_dir / "hadith_muslim.json"],
        )
        self.aid_service = AidBoardService(data_dir / "aid.db")

    def tearDown(self) -> None:
        self.tmpdir.cleanup()

    def test_quran_search_returns_translation_match(self) -> None:
        results = self.search_service.search_quran("merciful")
        self.assertEqual(len(results), 1)
        self.assertIn("Al-Fatihah", results[0].title)

    def test_hadith_search_returns_bukhari_item(self) -> None:
        results = self.search_service.search_hadith("intentions")
        self.assertEqual(len(results), 1)
        self.assertEqual(results[0].source, "Bukhari")

    def test_verse_lookup_returns_exact_reference(self) -> None:
        result = self.search_service.get_verse("1:1")
        self.assertIsNotNone(result)
        assert result is not None
        self.assertIn("Al-Fatihah", result.title)

    def test_dhikr_is_deterministic_for_given_date(self) -> None:
        service = DhikrService()
        first = service.get_daily_dhikr(date(2026, 4, 22))
        second = service.get_daily_dhikr(date(2026, 4, 22))
        self.assertEqual(first.text, second.text)

    def test_aid_board_create_list_and_close(self) -> None:
        entry = self.aid_service.create_entry("request", "Need groceries", "Sister A", "40", "Toulouse")
        active = self.aid_service.list_active_entries()
        self.assertEqual(len(active), 1)
        self.assertEqual(active[0].entry_id, entry.entry_id)
        closed = self.aid_service.close_entry(entry.entry_id)
        self.assertEqual(closed.status, "closed")
        self.assertEqual(self.aid_service.list_active_entries(), [])

    def test_prayer_fallback_produces_ordered_timings(self) -> None:
        service = PrayerTimeService(43.6047, 1.4442, "Toulouse")
        fallback = service._fallback_times(date(2026, 4, 22))
        ordered = [fallback.timings[name] for name in ["Fajr", "Dhuhr", "Asr", "Maghrib", "Isha"]]
        self.assertEqual(sorted(ordered), ordered)

    def test_hijri_fallback_formats_date(self) -> None:
        service = HijriCalendarService(43.6047, 1.4442)
        result = asyncio.run(service.get_current_hijri_date(date(2026, 4, 22)))
        self.assertGreaterEqual(len(result.hijri_date.split()), 3)


if __name__ == "__main__":
    unittest.main()
