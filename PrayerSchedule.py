from typing import Literal
import requests
from datetime import date
from logger import get_logger

PRAYER = ('Fajr', 'Dhuhr', 'Asr', 'Maghrib', 'Isha')

logger = get_logger(__name__)

class PrayerSchedule:
    def __init__(self, city: str, country: str):
        self.__city = city
        self.__country = country
    
    def __get_24hr_time(self, time: str) -> dict[Literal['hh', 'mm'], int]:
        hh_mm, *am_pm = time.split(" ")
        hh, mm = hh_mm.split(":")
        hh, mm = int(hh), int(mm)
        
        if am_pm == "am":
            if hh == 12:
                hh = 0
        elif am_pm == "pm":
            if hh != 12:
                hh += 12
            
        return {'hh': hh, 'mm': mm}

    def get_timings(self) -> dict[Literal['fajr', 'dhuhr', 'asr', 'maghrib', 'isha'], dict[Literal['hh', 'mm'], int]]:
        today = date.today().strftime('%d-%m-%Y')
        logger.info(f"Fetching prayer times for {self.__city}, {self.__country}")
        response = requests.get(f"http://api.aladhan.com/v1/timingsByCity/{today}", {'city': self.__city, 'country': self.__country, 'method': 3}).json()

        if response['code'] == 200:
            prayer_timings = response['data']['timings']
            timings = { prayer: self.__get_24hr_time(prayer_timings[prayer]) for prayer in PRAYER }
            logger.info(f"Successfully retrieved prayer times: {timings}")
            return timings
        else:
            logger.error(f"Failed to fetch prayer times from API: {response}")
            raise Exception('Failed to pull new Prayer Schedule from API')    