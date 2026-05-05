import re
from dataclasses import dataclass
from typing import Dict
import requests
from datetime import date
from logger import get_logger

PRAYER_NAMES = ('Fajr', 'Dhuhr', 'Asr', 'Maghrib', 'Isha')

logger = get_logger(__name__)


@dataclass
class PrayerTime:
    hour: int
    minute: int


class PrayerSchedule:
    def __init__(self, city: str, country: str) -> None:
        self._city = city
        self._country = country

    def _parse_time(self, time_str: str) -> PrayerTime:
        time_str = time_str.strip()
        logger.debug(f"Parsing time string: '{time_str}'")

        # Try 12-hour format with AM/PM (e.g., "5:15 AM", "1:30 PM")
        match = re.match(r'(\d{1,2}):(\d{2})\s*(AM|PM)', time_str, re.IGNORECASE)
        if match:
            hh = int(match.group(1))
            mm = int(match.group(2))
            period = match.group(3).upper()
            if period == 'PM' and hh != 12:
                hh += 12
            elif period == 'AM' and hh == 12:
                hh = 0
            logger.debug(f"Parsed 12-hour: {hh}:{mm}")
            return PrayerTime(hour=hh, minute=mm)

        # Try 24-hour format (e.g., "05:15", "13:30")
        try:
            hh, mm = map(int, time_str.split(':'))
            logger.debug(f"Parsed 24-hour: {hh}:{mm}")
            return PrayerTime(hour=hh, minute=mm)
        except ValueError:
            pass

        # Try format without leading zero (e.g., "5:15")
        match = re.match(r'(\d):(\d{2})', time_str)
        if match:
            hh = int(match.group(1))
            mm = int(match.group(2))
            logger.debug(f"Parsed short format: {hh}:{mm}")
            return PrayerTime(hour=hh, minute=mm)

        logger.warning(f"Could not parse time: '{time_str}', defaulting to 00:00")
        return PrayerTime(hour=0, minute=0)

    def get_timings(self) -> Dict[str, PrayerTime]:
        today = date.today().strftime('%d-%m-%Y')
        logger.info(f"Fetching prayer times for {self._city}, {self._country}")

        response = requests.get(
            f"http://api.aladhan.com/v1/timingsByCity/{today}",
            {'city': self._city, 'country': self._country, 'method': 3}
        ).json()

        if response['code'] == 200:
            timings_data = response['data']['timings']
            logger.debug(f"Raw API timings: {timings_data}")
            timings = {
                'fajr': self._parse_time(timings_data['Fajr']),
                'dhuhr': self._parse_time(timings_data['Dhuhr']),
                'asr': self._parse_time(timings_data['Asr']),
                'maghrib': self._parse_time(timings_data['Maghrib']),
                'isha': self._parse_time(timings_data['Isha'])
            }
            logger.info(f"Successfully retrieved prayer times: {timings}")
            return timings
        else:
            logger.error(f"Failed to fetch prayer times from API: {response}")
            raise Exception('Failed to pull new Prayer Schedule from API')