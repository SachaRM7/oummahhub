# OummahHub — Islamic Community Platform
# Copyright (c) 2026 Sacha Rbone
# MIT License
#
# This software is provided for the benefit of the Oummah (Muslim community).
# May Allah accept our efforts.

from __future__ import annotations

from dataclasses import dataclass
from datetime import date

ADHKAR = [
    "SubhanAllah — Glory be to Allah.",
    "Alhamdulillah — Praise be to Allah.",
    "Allahu Akbar — Allah is the Greatest.",
    "La ilaha illa Allah — None has the right to be worshipped except Allah.",
    "Astaghfirullah — I seek forgiveness from Allah.",
    "HasbunAllahu wa ni'mal wakeel — Allah is sufficient for us.",
    "La hawla wa la quwwata illa billah — No power except through Allah.",
    "Allahumma salli ʿala Muhammad — O Allah, send prayers upon Muhammad.",
    "Rabbi zidni ilma — My Lord, increase me in knowledge.",
    "Rabbi yassir wa la tuʿassir — My Lord, make it easy and do not make it difficult.",
    "Allahumma inni asʾaluka al-jannah — O Allah, I ask You for Paradise.",
    "Allahumma ajirni min an-nar — O Allah, save me from the Fire.",
    "Bismillah — In the name of Allah.",
    "Tawakkaltu ʿala Allah — I place my trust in Allah.",
    "Allahumma barik lana fima razaqtana — O Allah, bless what You have provided us.",
    "Ya Muqallib al-qulub, thabbit qalbi ʿala dinik — O Turner of hearts, keep my heart firm upon Your religion.",
    "Allahumma inni asʾaluka hubbak — O Allah, I ask You for Your love.",
    "SubhanAllahi wa bihamdihi — Glory and praise be to Allah.",
    "SubhanAllahi al-ʿAzim — Glory be to Allah, the Magnificent.",
    "Allahumma inni aʿudhu bika min al-hammi wal-huzn — O Allah, I seek refuge in You from worry and sadness.",
    "Allahumma inni asʾaluka ilman nafiʿan — O Allah, I ask You for beneficial knowledge.",
    "Rabbanaghfir lana wa li ikhwanina — Our Lord, forgive us and our brothers.",
    "Allahumma anta as-salam wa minka as-salam — O Allah, You are Peace and from You is peace.",
    "Allahumma inni asʾaluka husna al-khatimah — O Allah, I ask You for a good ending.",
    "Rabbana atina fid-dunya hasanah — Our Lord, grant us goodness in this world.",
    "Allahumma inni asʾaluka al-ʿafiyah — O Allah, I ask You for well-being.",
    "Ya Hayyu Ya Qayyum bi rahmatika astaghith — O Ever-Living, O Sustainer, by Your mercy I seek relief.",
    "Allahumma inni asʾaluka rizqan tayyiban — O Allah, I ask You for wholesome provision.",
    "Rabbi habli min ladunka rahmah — My Lord, grant me mercy from Yourself.",
    "Wa qul rabbi irhamhuma kama rabbayani saghira — My Lord, have mercy upon my parents as they raised me.",
]


@dataclass(slots=True)
class DhikrEntry:
    index: int
    text: str

    def format_message(self) -> str:
        return f"🌙 Daily Dhikr #{self.index + 1}\n{self.text}"


class DhikrService:
    def get_daily_dhikr(self, target_date: date | None = None) -> DhikrEntry:
        target_date = target_date or date.today()
        index = target_date.toordinal() % len(ADHKAR)
        return DhikrEntry(index=index, text=ADHKAR[index])

    def get_random_seeded_dhikr(self, seed: int) -> DhikrEntry:
        index = seed % len(ADHKAR)
        return DhikrEntry(index=index, text=ADHKAR[index])
