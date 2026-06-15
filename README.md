# Chrome-Cast Adhan

Automatically casts adhan (Islamic call to prayer) to Chromecast devices on a cron schedule.

Fetches daily prayer times from the [aladhan.com API](https://aladhan.com/prayer-times-api) and plays adhan audio to any Chromecast on your network at the correct times. Set it once and forget it.

## Features

- Fetches accurate daily prayer times from aladhan.com (Muslim World League method)
- Plays adhan audio to any Chromecast device on your network
- Automatic daily schedule via cron — set it and forget it
- Fajr plays at reduced volume (0.3) by default
- Daily refresh of prayer times at 01:00
- Custom audio files for regular and Fajr adhan

## Prerequisites

- Python 3.12+
- A Chromecast device on the same Wi-Fi network
- `uv` or `pip` for installation
- macOS or Linux (requires cron)

## Installation

```bash
git clone <repo-url>
cd chrome-cast

uv sync
# or
pip install -r requirements.txt
```

Place your adhan audio files in `assets/`:

| File | Purpose |
|------|---------|
| `assets/azan.mp3` | Regular adhan (required) |
| `assets/fajr_azan.mp3` | Fajr adhan (optional, falls back to `azan.mp3`) |

## Quick Start

```bash
# 1. Play adhan once (interactive — selects device, asks for address)
python .

# 2. Set up daily cron schedule
python . --setup
```

## Usage

| Command | What it does |
|---------|-------------|
| `python .` | Play adhan once (prompts for device, then address) |
| `python . --fajr` | Play Fajr adhan at reduced volume (0.3) |
| `python . --setup` | Set up cron: 5 daily prayers + daily update at 01:00 |
| `python . --update` | Refresh prayer times from API and rewrite cron |
| `python . --cleanup` | Remove all cron jobs (no prompts) |

### Interactive play

```bash
python .
```

You'll be prompted to select a Chromecast device from a list, then enter your address (e.g. "Dortmund, Germany").

### Set up automatic scheduling

```bash
python . --setup
```

This creates cron jobs for all 5 daily prayers plus a daily update job at 01:00 to refresh prayer times.

### Update prayer times manually

```bash
python . --update
```

Refetches prayer times and rewrites the cron schedule.

### Remove all cron jobs

```bash
python . --cleanup
```

## Configuration

All modes accept these flags:

| Flag | Default | Description |
|------|---------|-------------|
| `--device-name` | (prompted) | Chromecast device name, e.g. `"Living Room Speaker"` |
| `--address` | (prompted) | City/address for prayer times, e.g. `"Dortmund, Germany"` |
| `--port` | `8000` | Port for local audio HTTP server |
| `--adhan` | `assets/azan.mp3` | Regular adhan audio file |
| `--fajr-adhan` | `assets/fajr_azan.mp3` | Fajr adhan audio file |
| `--log` | `log/prayer.log` | Log file path |

### Non-interactive usage

Skip prompts by passing flags directly:

```bash
python . --device-name "Living Room Speaker" --address "Dortmund, Germany"
python . --setup --device-name "Living Room Speaker" --address "Dortmund, Germany"
python . --update --device-name "Living Room Speaker" --address "Dortmund, Germany"
```

## How It Works

1. **Prayer times** are fetched from `api.aladhan.com/v1/timingsByAddress` using method 3 (Muslim World League).
2. **Audio playback** starts a temporary HTTP server on your machine that streams the adhan file to the Chromecast.
3. **Cron scheduling** creates one job per prayer, each tagged with a comment like `Fajr Prayer`, `Dhuhr Prayer`, etc. A daily update job runs at 01:00 to refresh the schedule.
4. **Cron jobs** use the exact Python interpreter that was active during setup and set a `DIR` environment variable pointing to the project root.

## Limitations

- **Port conflict**: The HTTP server uses port 8000. If it's already in use, the app crashes — no fallback or retry.
- **Slow devices**: The 5-second discovery timeout may miss slow-responding Chromecasts. Edit `DISCOVER_TIMEOUT` in `media.py` if needed.
- **Same network required**: Chromecast must be on the same LAN as the machine running the script — no remote casting.
- **macOS/Linux only**: Scheduling relies on cron, which is not available on Windows.
- **Log rotation**: Logs rotate every 7 days, not daily (configured in `logger.py`).
- **Silent defaults**: `--update` without `--device-name` silently defaults to `"Living Room Speaker"`.
- **No tests**: The project has no test suite and minimal error handling.

## Project Structure

| File | Purpose |
|------|---------|
| `__main__.py` | CLI entrypoint; dispatches to play/setup/cleanup/update modes |
| `config.py` | Argument parsing and configuration dataclasses |
| `media.py` | Chromecast discovery, connection, and audio casting |
| `server.py` | Ephemeral HTTP server to stream local audio files |
| `prayer.py` | Fetches and parses prayer times from aladhan.com |
| `scheduler.py` | Cron job management via python-crontab |
| `logger.py` | Dual file + console logger |
| `search.py` | Standalone utility to discover Chromecasts on the network |

## License

MIT © 2024 Md Ryad Ahmed Biplob
