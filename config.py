# OummahHub — Islamic Community Platform
# Copyright (c) 2026 Sacha Rbone
# MIT License
#
# This software is provided for the benefit of the Oummah (Muslim community).
# May Allah accept our efforts.

from __future__ import annotations

import os
from dataclasses import dataclass
from pathlib import Path

from dotenv import load_dotenv

load_dotenv()


@dataclass(slots=True)
class Settings:
    telegram_bot_token: str = os.getenv("TELEGRAM_BOT_TOKEN", "")
    telegram_chat_id: str = os.getenv("TELEGRAM_CHAT_ID", "-1003805395829")
    telegram_topic_bot: int = int(os.getenv("TELEGRAM_TOPIC_BOT", "3"))
    telegram_topic_agi: int = int(os.getenv("TELEGRAM_TOPIC_AGI", "33"))
    prayer_location_lat: float = float(os.getenv("PRAYER_LOCATION_LAT", "43.6047"))
    prayer_location_lon: float = float(os.getenv("PRAYER_LOCATION_LON", "1.4442"))
    prayer_location_city: str = os.getenv("PRAYER_LOCATION_CITY", "Toulouse")
    data_dir: Path = Path(os.getenv("OUMMAHUB_DATA_DIR", str(Path(__file__).resolve().parent / "data")))
    aladhan_method: int = int(os.getenv("ALADHAN_METHOD", "2"))

    @property
    def quran_path(self) -> Path:
        return self.data_dir / "quran.json"

    @property
    def hadith_bukhari_path(self) -> Path:
        return self.data_dir / "hadith_bukhari.json"

    @property
    def hadith_muslim_path(self) -> Path:
        return self.data_dir / "hadith_muslim.json"

    @property
    def aid_db_path(self) -> Path:
        return self.data_dir / "aid.db"

    def ensure_directories(self) -> None:
        self.data_dir.mkdir(parents=True, exist_ok=True)


def get_settings() -> Settings:
    settings = Settings()
    settings.ensure_directories()
    return settings
