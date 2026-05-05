from dataclasses import dataclass
from typing import Dict, Optional
import requests
from datetime import date
from logger import get_logger

PRAYER_NAMES = ('Fajr', 'Dhuhr', 'Asr', 'Maghrib', 'Isha')

logger = get_logger(__name__)


@dataclass
class PrayerTime:
    hour: int
    minute: int


@dataclass
class Timings:
    fajr: PrayerTime
    dhuhr: PrayerTime
    asr: PrayerTime
    maghrib: PrayerTime
    isha: PrayerTime

    def items(self) -> Dict[str, PrayerTime]:
        return {
            'fajr': self.fajr,
            'dhuhr': self.dhuhr,
            'asr': self.asr,
            'maghrib': self.maghrib,
            'isha': self.isha
        }


class PrayerSchedule:
    def __init__(self, city: str, country: str) -> None:
        self._city = city
        self._country = country

    def _parse_time(self, time_str: str) -> PrayerTime:
        parts = time_str.strip().split()
        if len(parts) < 2:
            return PrayerTime(0, 0)

        hh_mm = parts[0]
        am_pm = parts[1].lower() if len(parts) > 1 else ""

        hh, mm = map(int, hh_mm.split(":"))

        if am_pm == "am" and hh == 12:
            hh = 0
        elif am_pm == "pm" and hh != 12:
            hh += 12

        return PrayerTime(hour=hh, minute=mm)

    def get_timings(self) -> Timings:
        today = date.today().strftime('%d-%m-%Y')
        logger.info(f"Fetching prayer times for {self._city}, {self._country}")

        response = requests.get(
            f"http://api.aladhan.com/v1/timingsByCity/{today}",
            {'city': self._city, 'country': self._country, 'method': 3}
        ).json()

        if response['code'] == 200:
            timings_data = response['data']['timings']
            timings = Timings(
                fajr=self._parse_time(timings_data['Fajr']),
                dhuhr=self._parse_time(timings_data['Dhuhr']),
                asr=self._parse_time(timings_data['Asr']),
                maghrib=self._parse_time(timings_data['Maghrib']),
                isha=self._parse_time(timings_data['Isha'])
            )
            logger.info(f"Successfully retrieved prayer times: {timings}")
            return timings
        else:
            logger.error(f"Failed to fetch prayer times from API: {response}")
            raise Exception('Failed to pull new Prayer Schedule from API')