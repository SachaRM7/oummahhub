#!/usr/bin/env python3
# OummahHub — Islamic Community Platform
# Copyright (c) 2026 Sacha Rbone
# MIT License
#
# This software is provided for the benefit of the Oummah (Muslim community).
# May Allah accept our efforts.

from __future__ import annotations

import argparse
import asyncio

from telegram import Update
from telegram.ext import Application, ApplicationBuilder, CommandHandler, ContextTypes

from config import get_settings
from modules.aid_board import AidBoardService
from modules.dhikr import DhikrService
from modules.health import HealthService
from modules.hijri_calendar import HijriCalendarService
from modules.prayer_times import PrayerTimeService
from modules.quran_search import QuranSearchService

settings = get_settings()
prayer_service = PrayerTimeService(
    settings.prayer_location_lat,
    settings.prayer_location_lon,
    settings.prayer_location_city,
    settings.aladhan_method,
)
hijri_service = HijriCalendarService(
    settings.prayer_location_lat,
    settings.prayer_location_lon,
    settings.aladhan_method,
)
search_service = QuranSearchService(
    settings.quran_path,
    [settings.hadith_bukhari_path, settings.hadith_muslim_path],
)
dhikr_service = DhikrService()
aid_service = AidBoardService(settings.aid_db_path)
health_service = HealthService(
    settings.quran_path,
    [settings.hadith_bukhari_path, settings.hadith_muslim_path],
    settings.aid_db_path,
)


def _help_text() -> str:
    return (
        "OummahHub commands:\n"
        "/start or /help — show this message\n"
        "/prayer — today's prayer times\n"
        "/hijri — current Hijri date\n"
        "/quran <terms> — search Quran\n"
        "/hadith <terms> — search hadith\n"
        "/verse <surah:ayah> — fetch a verse\n"
        "/dhikr — daily dhikr\n"
        "/aid_list — active aid entries\n"
        "/aid_request <description> | <amount> | <city> — add request\n"
        "/aid_offer <description> | <amount> | <city> — add offer\n"
        "/aid_close <id> — close entry\n"
        "/health — run health check"
    )


async def start_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(_help_text())


async def prayer_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    result = await prayer_service.get_today_prayer_times()
    await update.message.reply_text(result.format_message())


async def hijri_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    hijri = await hijri_service.get_current_hijri_date()
    events = "\n".join(f"- {event}" for event in hijri_service.get_upcoming_events(hijri.hijri_date))
    await update.message.reply_text(f"{hijri.format_message()}\n{events}")


async def quran_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = " ".join(context.args).strip()
    if not query:
        await update.message.reply_text("Usage: /quran <search terms>")
        return
    results = search_service.search_quran(query)
    if not results:
        await update.message.reply_text("No Quran matches found.")
        return
    await update.message.reply_text("\n\n".join(item.format_message() for item in results))


async def hadith_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    query = " ".join(context.args).strip()
    if not query:
        await update.message.reply_text("Usage: /hadith <search terms>")
        return
    results = search_service.search_hadith(query)
    if not results:
        await update.message.reply_text("No hadith matches found.")
        return
    await update.message.reply_text("\n\n".join(item.format_message() for item in results))


async def verse_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    reference = " ".join(context.args).strip()
    result = search_service.get_verse(reference)
    if result is None:
        await update.message.reply_text("Usage: /verse <surah:ayah> and make sure the verse exists in the local corpus.")
        return
    await update.message.reply_text(result.format_message())


async def dhikr_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(dhikr_service.get_daily_dhikr().format_message())


async def aid_list_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    entries = aid_service.list_active_entries()
    message = "No active aid entries." if not entries else "\n".join(entry.format_message() for entry in entries)
    await update.message.reply_text(message)


async def aid_request_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    description, amount, city = _parse_aid_args(context.args)
    requester = update.effective_user.full_name if update.effective_user else "anonymous"
    entry = aid_service.create_entry("request", description, requester, amount, city)
    await update.message.reply_text(f"Aid request created and marked pending moderation:\n{entry.format_message()}")


async def aid_offer_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    description, amount, city = _parse_aid_args(context.args)
    requester = update.effective_user.full_name if update.effective_user else "anonymous"
    entry = aid_service.create_entry("offer", description, requester, amount, city)
    await update.message.reply_text(f"Aid offer created and marked pending moderation:\n{entry.format_message()}")


async def aid_close_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    if not context.args:
        await update.message.reply_text("Usage: /aid_close <id>")
        return
    entry = aid_service.close_entry(int(context.args[0]))
    await update.message.reply_text(f"Closed aid entry:\n{entry.format_message()}")


async def health_handler(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    report = await health_service.run()
    await update.message.reply_text(HealthService.format_report(report))


def _parse_aid_args(args: list[str]) -> tuple[str, str, str]:
    text = " ".join(args).strip()
    if not text:
        raise ValueError("Description is required")
    parts = [part.strip() for part in text.split("|")]
    description = parts[0]
    amount = parts[1] if len(parts) > 1 else ""
    city = parts[2] if len(parts) > 2 else ""
    if not description:
        raise ValueError("Description is required")
    return description, amount, city


def build_application() -> Application:
    if not settings.telegram_bot_token:
        raise RuntimeError("TELEGRAM_BOT_TOKEN is required to run the Telegram bot.")
    application = ApplicationBuilder().token(settings.telegram_bot_token).build()
    application.add_handler(CommandHandler(["start", "help"], start_handler))
    application.add_handler(CommandHandler("prayer", prayer_handler))
    application.add_handler(CommandHandler("hijri", hijri_handler))
    application.add_handler(CommandHandler("calendar", hijri_handler))
    application.add_handler(CommandHandler("quran", quran_handler))
    application.add_handler(CommandHandler("hadith", hadith_handler))
    application.add_handler(CommandHandler("verse", verse_handler))
    application.add_handler(CommandHandler("dhikr", dhikr_handler))
    application.add_handler(CommandHandler("aid_list", aid_list_handler))
    application.add_handler(CommandHandler("aid_request", aid_request_handler))
    application.add_handler(CommandHandler("aid_offer", aid_offer_handler))
    application.add_handler(CommandHandler("aid_close", aid_close_handler))
    application.add_handler(CommandHandler("health", health_handler))
    return application


async def run_cli(command: str, argument: str = "") -> str:
    if command == "prayer":
        return (await prayer_service.get_today_prayer_times()).format_message()
    if command == "hijri":
        hijri = await hijri_service.get_current_hijri_date()
        events = "\n".join(hijri_service.get_upcoming_events(hijri.hijri_date))
        return f"{hijri.format_message()}\n{events}"
    if command == "quran":
        results = search_service.search_quran(argument)
        return "\n\n".join(item.format_message() for item in results) if results else "No Quran matches found."
    if command == "hadith":
        results = search_service.search_hadith(argument)
        return "\n\n".join(item.format_message() for item in results) if results else "No hadith matches found."
    if command == "verse":
        verse = search_service.get_verse(argument)
        return verse.format_message() if verse else "Verse not found."
    if command == "dhikr":
        return dhikr_service.get_daily_dhikr().format_message()
    if command == "aid-list":
        entries = aid_service.list_active_entries()
        return "\n".join(item.format_message() for item in entries) if entries else "No active aid entries."
    if command == "health":
        return HealthService.format_report(await health_service.run())
    raise ValueError(f"Unknown CLI command: {command}")


def parse_args() -> argparse.Namespace:
    parser = argparse.ArgumentParser(description="OummahHub Telegram bot and CLI")
    subparsers = parser.add_subparsers(dest="mode", required=True)
    subparsers.add_parser("run-bot", help="Run the Telegram bot")
    cli_parser = subparsers.add_parser("cli", help="Run a local CLI command")
    cli_parser.add_argument("command", choices=["prayer", "hijri", "quran", "hadith", "verse", "dhikr", "aid-list", "health"])
    cli_parser.add_argument("argument", nargs="?", default="")
    return parser.parse_args()


def main() -> None:
    args = parse_args()
    if args.mode == "run-bot":
        application = build_application()
        application.run_polling(allowed_updates=Update.ALL_TYPES)
        return
    if args.mode == "cli":
        print(asyncio.run(run_cli(args.command, args.argument)))
        return
    raise RuntimeError("Unsupported mode")


if __name__ == "__main__":
    main()
