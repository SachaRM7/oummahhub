# OummahHub — Islamic Community Platform
# Copyright (c) 2026 Sacha Rbone
# MIT License
#
# This software is provided for the benefit of the Oummah (Muslim community).
# May Allah accept our efforts.

from __future__ import annotations

import json
from dataclasses import dataclass
from pathlib import Path


@dataclass(slots=True)
class SearchResult:
    source: str
    title: str
    arabic: str
    transliteration: str
    translation: str

    def format_message(self) -> str:
        parts = [self.title, self.arabic]
        if self.transliteration:
            parts.append(self.transliteration)
        if self.translation:
            parts.append(self.translation)
        parts.append(f"Source: {self.source}")
        return "\n".join(parts)


class QuranSearchService:
    def __init__(self, quran_path: Path, hadith_paths: list[Path]) -> None:
        self.quran_path = quran_path
        self.hadith_paths = hadith_paths
        self._quran_cache: list[dict] | None = None
        self._hadith_cache: list[dict] | None = None

    def search_quran(self, query: str, limit: int = 5) -> list[SearchResult]:
        query = query.strip().lower()
        results: list[SearchResult] = []
        for verse in self._load_quran():
            haystack = " ".join(str(verse.get(key, "")) for key in ("arabic", "transliteration", "translation")).lower()
            if query in haystack:
                results.append(
                    SearchResult(
                        source="Quran",
                        title=f"Surah {verse['surah']}:{verse['ayah']} — {verse.get('surah_name', 'Unknown')}",
                        arabic=verse.get("arabic", ""),
                        transliteration=verse.get("transliteration", ""),
                        translation=verse.get("translation", ""),
                    )
                )
            if len(results) >= limit:
                break
        return results

    def get_verse(self, reference: str) -> SearchResult | None:
        surah, _, ayah = reference.partition(":")
        if not surah or not ayah:
            return None
        for verse in self._load_quran():
            if str(verse.get("surah")) == surah and str(verse.get("ayah")) == ayah:
                return SearchResult(
                    source="Quran",
                    title=f"Surah {verse['surah']}:{verse['ayah']} — {verse.get('surah_name', 'Unknown')}",
                    arabic=verse.get("arabic", ""),
                    transliteration=verse.get("transliteration", ""),
                    translation=verse.get("translation", ""),
                )
        return None

    def search_hadith(self, query: str, limit: int = 5) -> list[SearchResult]:
        query = query.strip().lower()
        results: list[SearchResult] = []
        for item in self._load_hadith():
            haystack = " ".join(str(item.get(key, "")) for key in ("title", "text", "translation")).lower()
            if query in haystack:
                results.append(
                    SearchResult(
                        source=item.get("collection", "Hadith"),
                        title=item.get("title", "Hadith result"),
                        arabic=item.get("text", ""),
                        transliteration="",
                        translation=item.get("translation", ""),
                    )
                )
            if len(results) >= limit:
                break
        return results

    def _load_quran(self) -> list[dict]:
        if self._quran_cache is None:
            self._quran_cache = json.loads(self.quran_path.read_text(encoding="utf-8"))
        return self._quran_cache

    def _load_hadith(self) -> list[dict]:
        if self._hadith_cache is None:
            merged: list[dict] = []
            for path in self.hadith_paths:
                merged.extend(json.loads(path.read_text(encoding="utf-8")))
            self._hadith_cache = merged
        return self._hadith_cache
