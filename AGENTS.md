# Chrome-Cast Adhan Project

## Overview
Python 3.12.x project that casts Islamic prayer call (Adhan) audio to Chromecast devices on a schedule. Uses system cron for scheduling five daily prayers and fetches prayer times from aladhan.com API (timingsByAddress endpoint). Works with any Python package manager (uv, pip).

## Installation

```bash
# uv (recommended)
uv sync

# pip (fallback)
pip install -r requirements.txt
```

## Commands

```bash
# Play adhan to chromecast (prompts for device and address if not provided)
python . --device-name "Living Room Speaker" --address "Dortmund, Germany"

# Play fajr adhan (lower volume: 0.3)
python . --fajr

# Custom port for local server
python . --port 9000 --fajr

# Use remote URL instead of local file
python . --adhan "https://example.com/audio.mp3"

# Initialize cron jobs for prayer schedule (prompts for address and device if not provided)
python . --setup --address "Dortmund, Germany"

# Remove all cron jobs (no prompts needed)
python . --cleanup

# Refresh prayer times from API and update cron (prompts for address if not provided)
python . --update --address "Dortmund, Germany"
```

## CLI Flags

| Flag | Purpose | Default |
|------|---------|---------|
| `--device-name` | Chromecast friendly name | None (prompted in play/setup modes) |
| `--adhan` | Audio file path or URL | "assets/azan.mp3" |
| `--fajr-adhan` | Fajr audio file path or URL | "assets/fajr_azan.mp3" |
| `--port` | Local HTTP server port | 8000 |
| `--address` | Location address (city, country) | None (prompted in play/setup/update modes) |
| `--log` | Log file path | "log/prayer.log" |
| `--fajr` | Play Fajr adhan (lower volume) | False |
| `--setup` | Initialize cron jobs | - |
| `--cleanup` | Remove all cron jobs | - |
| `--update` | Refresh prayer times from API | - |

## File Descriptions

| File | Description |
|------|-------------|
| `__main__.py` | CLI entry point with mode routing (play_mode, setup_mode, cleanup_mode, update_mode) |
| `config.py` | Dataclass-based configuration, CLI argument parsing (no prompts - handled by modes) |
| `media.py` | `MediaCaster` class (context manager) - discovers and casts audio to Chromecast, includes device discovery |
| `server.py` | HTTP server for serving local audio files during playback |
| `prayer.py` | `PrayerSchedule` class - fetches prayer times from aladhan.com API (timingsByAddress endpoint, method 3) |
| `scheduler.py` | Cron job management: `init_cron_job()`, `update_prayer_schedule()`, `clean_up_cron_jobs()`, `get_current_user()` |
| `logger.py` | Logging utility with daily rotating file handler |
| `search.py` | Standalone utility to discover Chromecast devices on network |
| `assets/` | Audio files directory (azan.mp3, fajr_azan.mp3) |

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
- User is auto-detected via `get_current_user()` (pwd module, falls back to USER env var)
- Cron commands include `--address` and `--device-name` flags only if explicitly provided (not defaults)

## Important Gotchas

- `DISCOVER_TIMEOUT = 5` seconds in media.py - may need adjustment for slow networks
- Audio files can be local paths (served via local HTTP server) or remote URLs
- Log file is auto-rotated daily, keeping last 7 days
- No global prompts in config.py - each mode handles its own prompts:
  - **play mode**: Prompts for device (if needed), then address (if needed)
  - **setup mode**: Prompts for address (if needed), then device (if needed)
  - **update mode**: Prompts for address (if needed)
  - **cleanup mode**: No prompts needed
- User is auto-detected for cron operations - no --user flag needed
- API endpoint changed from `/timingsByCity` to `/timingsByAddress` using combined address string (e.g., "Dortmund, Germany")