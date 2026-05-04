# Chrome-Cast Adhan Project

## Overview
Python 3.11 Pipenv project that casts Islamic prayer call (Adhan) audio to Chromecast devices on a schedule. Uses system cron for scheduling five daily prayers and fetches prayer times from aladhan.com API.

## Commands

```bash
# Play adhan to chromecast
pipenv start

# Play fajr adhan (lower volume: 0.7)
pipenv start -- --fajr

# Initialize cron jobs for prayer schedule
pipenv setup

# Remove all cron jobs
pipenv cleanup

# Refresh prayer times from API and update cron
pipenv update
```

**Direct Python alternatives:**
```bash
python .                    # same as pipenv start
python . --setup
python . --cleanup
python . --update
python . --fajr
```

## Required Environment Variables

| Variable | Purpose | Example |
|----------|---------|---------|
| `DEVICE_NAME` | Chromecast friendly name | "Living Room Speaker" |
| `ADHAN` | Regular adhan MP3 URL | https://... |
| `FAJR_ADHAN` | Fajr adhan MP3 URL | https://... |
| `CITY` | City for prayer times | "Dortmund" |
| `COUNTRY` | Country for prayer times | "Germany" |
| `USER` | System user for cron | "biplobmac" |
| `LOG` | Log file path | "/var/log/prayer.log" |
| `PYTHON` | Python interpreter path | "/usr/bin/python" |

## File Descriptions

| File | Description |
|------|-------------|
| `__main__.py` | CLI entry point with argparse for --setup/--cleanup/--update/--fajr flags |
| `MediaCaster.py` | `MediaCaster` class (context manager) - discovers and casts audio to Chromecast |
| `PrayerSchedule.py` | `PrayerSchedule` class - fetches prayer times from aladhan.com API (method 3 = ISNA) |
| `scheduler.py` | Cron job management: `init_cron_job()`, `update_prayer_schedule()`, `clean_up_cron_jobs()` |
| `search.py` | Standalone utility to discover Chromecast devices on network |

## Dependencies

- `pychromecast` - Chromecast device discovery/control
- `python-crontab` - Cron job management
- `requests` - HTTP calls to aladhan.com API (not in Pipfile but imported in PrayerSchedule.py)

## Testing & Code Quality

- No tests exist in this repo
- No lint/format/typecheck configuration

## Cron Behavior

- **Daily at 01:00** - Update prayer times from API
- **Five scheduled times** - Fajr, Dhuhr, Asr, Maghrib, Isha (pulled from API)

## Important Gotchas

- **`.env` is gitignored** - never commit secrets
- `DISCOVER_TIMEOUT = 5` seconds in MediaCaster.py - may need adjustment for slow networks
- Audio URLs must be direct MP3 links (not streaming pages)
- LOG path `/var/log/prayer.log` typically requires elevated permissions (sudo)