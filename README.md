# OummahHub — Islamic Community Platform

OummahHub is a self-hostable Telegram bot and local Python application that brings together prayer times, Hijri date utilities, Quran and hadith search, daily dhikr rotation, a lightweight community aid board, and health monitoring.

## What is included

- Prayer times via Aladhan API with a built-in deterministic fallback calculator
- Hijri date retrieval with API-backed conversion and a tabular fallback
- Local Quran and hadith search from JSON files
- Daily dhikr rotation with 30 phrases
- SQLite-backed aid board for requests and offers
- Health check module and cron-friendly shell scripts
- Telegram bot handlers plus a CLI mode for local verification

## Project layout

```text
.
├── bot.py
├── config.py
├── modules/
├── data/
├── scripts/
├── requirements.txt
└── tests/
```

## Setup

1. Create a virtual environment.
2. Install dependencies.
3. Copy the environment variables below into a `.env` file.
4. Run the CLI checks or launch the Telegram bot.

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
```

## Environment variables

```env
TELEGRAM_BOT_TOKEN=your_bot_token
TELEGRAM_CHAT_ID=-1003805395829
TELEGRAM_TOPIC_BOT=3
TELEGRAM_TOPIC_AGI=33
PRAYER_LOCATION_LAT=43.6047
PRAYER_LOCATION_LON=1.4442
PRAYER_LOCATION_CITY=Toulouse
OUMMAHUB_DATA_DIR=/root/.hermes/agents/coder/code/20260420/data
ALADHAN_METHOD=2
```

## Running locally without Telegram

```bash
python3 bot.py cli prayer
python3 bot.py cli hijri
python3 bot.py cli quran mercy
python3 bot.py cli hadith intention
python3 bot.py cli verse 1:1
python3 bot.py cli dhikr
python3 bot.py cli aid-list
python3 bot.py cli health
```

## Running the Telegram bot

```bash
python3 bot.py run-bot
```

## Cron-friendly scripts

```bash
./scripts/daily-prayer-times.sh
./scripts/daily-dhikr.sh
./scripts/oummahhub-health.sh
```

## Data files

Sample Quran and hadith files are included so the project works immediately. Replace them with fuller corpora later if desired.

## Tests

```bash
python3 -m unittest discover -s tests -v
```

## License

MIT. Source files include the OummahHub MIT header requested in the PRD.
