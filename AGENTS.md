# Chrome-Cast Adhan

Python 3.12.x project that casts adhan audio to Chromecast devices on a cron schedule.
Fetches prayer times from aladhan.com `/timingsByAddress` (method 3 = Muslim World League).

## Install

```
uv sync
pip install -r requirements.txt
```

## Commands

| Command | What it does |
|---------|-------------|
| `python .` | Play adhan (prompts for device, then address if missing) |
| `python . --fajr` | Play Fajr adhan at volume 0.3 |
| `python . --setup` | Init cron: 5 daily prayers + daily update at 01:00 |
| `python . --cleanup` | Remove all cron jobs (no prompts) |
| `python . --update` | Refresh prayer times from API and rewrite cron |

All modes accept `--device-name`, `--address`, `--port`, `--adhan`, `--fajr-adhan`, `--log`.

| Flag | Default |
|------|---------|
| `--device-name` | None (prompted) |
| `--adhan` | `assets/azan.mp3` |
| `--fajr-adhan` | `assets/fajr_azan.mp3` |
| `--port` | 8000 |
| `--address` | None (prompted) |
| `--log` | `log/prayer.log` |

## Gotchas

- **`DISCOVER_TIMEOUT = 5`** in `media.py` — may need bumping on slow networks
- **Port conflict crashes** — `AudioServer` has no retry/fallback if port is in use
- **Log rotation is every 7 days** (not daily). `TimedRotatingFileHandler(when="midnight", interval=7, backupCount=7)`
- **Cron commands always include `--address` and `--device-name`** — only `--port`, `--adhan`, `--fajr-adhan`, `--log` are omitted when at defaults
- **Prompt order differs by mode**: play → device then address; setup → address then device

## Architecture

- `__main__.py` — CLI entrypoint; dispatches to play/setup/cleanup/update modes
- `config.py` — argparse + dataclass config (no prompting; modes handle prompts)
- `media.py` — `MediaCaster` context manager (discovers device, starts local HTTP server, casts audio)
- `server.py` — ephemeral `AudioServer` (threaded HTTP server for local files during playback)
- `prayer.py` — `PrayerSchedule` fetches timings from aladhan.com API
- `scheduler.py` — cron management via `python-crontab`
- `search.py` — standalone device discovery utility (not imported by the app)
- `logger.py` — dual file+console logger with `TimedRotatingFileHandler`

## Cron behavior

- **Daily at 01:00**: runs `--update` to refresh prayer times from API
- **5 prayers**: Fajr (volume 0.3), Dhuhr, Asr, Maghrib, Isha
- User auto-detected via `pwd.getpwuid(getuid())` → `$USER` → `$USERNAME`

## Code quality

- No tests, no lint/format/typecheck config
