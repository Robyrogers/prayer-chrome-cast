from typing import Literal
import requests
from datetime import date

PRAYER = ('Fajr', 'Dhuhr', 'Asr', 'Maghrib', 'Isha')

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
        response = requests.get(f"http://api.aladhan.com/v1/timingsByCity/{today}", {'city': self.__city, 'country': self.__country, 'method': 3}).json()
        
        if response['code'] == 200:
            prayer_timings = response['data']['timings']
            return { prayer: self.__get_24hr_time(prayer_timings[prayer]) for prayer in PRAYER }
        else:
            raise Exception('Failed to pull new Prayer Schedule from API')    