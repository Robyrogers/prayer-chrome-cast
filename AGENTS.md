# Chrome-Cast Adhan Project

## Overview
Python 3.12.x project that casts Islamic prayer call (Adhan) audio to Chromecast devices on a schedule. Uses system cron for scheduling five daily prayers and fetches prayer times from aladhan.com API. Works with any Python package manager (uv, pip).

## Installation

```bash
# uv (recommended)
uv sync

# pip (fallback)
pip install -r requirements.txt
```

## Commands

```bash
# Play adhan to chromecast (uses local files)
python . --device-name "Living Room Speaker"

# Play fajr adhan (lower volume: 0.7)
python . --fajr

# Custom port for local server
python . --port 9000 --fajr

# Use remote URL instead of local file
python . --adhan "https://example.com/audio.mp3"

# Initialize cron jobs for prayer schedule
python . --setup --city Dortmund --country Germany --user biplobmac

# Remove all cron jobs
python . --cleanup --user biplobmac

# Refresh prayer times from API and update cron
python . --update --city Dortmund --country Germany
```

## CLI Flags

| Flag | Purpose | Default |
|------|---------|---------|
| `--device-name` | Chromecast friendly name | "Living Room Speaker" |
| `--adhan` | Audio file path or URL | "Azan_Mecca.mp3" |
| `--fajr-adhan` | Fajr audio file path or URL | "Fajr_Azan_Mecca.mp3" |
| `--port` | Local HTTP server port | 8000 |
| `--city` | City for prayer times | "Dortmund" |
| `--country` | Country for prayer times | "Germany" |
| `--user` | System user for cron | "biplobmac" |
| `--log` | Log file path | "~/logs/prayer.log" |
| `--python` | Python interpreter path | "/usr/bin/python" |

## File Descriptions

| File | Description |
|------|-------------|
| `__main__.py` | CLI entry point with argparse for --setup/--cleanup/--update/--fajr flags |
| `MediaCaster.py` | `MediaCaster` class (context manager) - discovers and casts audio to Chromecast |
| `server.py` | HTTP server for serving local audio files during playback |
| `PrayerSchedule.py` | `PrayerSchedule` class - fetches prayer times from aladhan.com API (method 3 = ISNA) |
| `scheduler.py` | Cron job management: `init_cron_job()`, `update_prayer_schedule()`, `clean_up_cron_jobs()` |
| `search.py` | Standalone utility to discover Chromecast devices on network |

## Dependencies

- `pychromecast` - Chromecast device discovery/control
- `python-crontab` - Cron job management
- `requests` - HTTP calls to aladhan.com API

## Testing & Code Quality

- No tests exist in this repo
- No lint/format/typecheck configuration

## Cron Behavior

- **Daily at 01:00** - Update prayer times from API
- **Five scheduled times** - Fajr, Dhuhr, Asr, Maghrib, Isha (pulled from API)

## Important Gotchas

- `DISCOVER_TIMEOUT = 5` seconds in MediaCaster.py - may need adjustment for slow networks
- Audio files can be local paths (served via local HTTP server) or remote URLs
- Log file is auto-rotated daily, keeping last 7 days