from typing import Literal
import requests

PRAYER = ('fajr', 'dhuhr', 'asr', 'maghrib', 'isha')

class PrayerSchedule:
    def __init__(self, api_key: str):
        self.__api_key = api_key
    
    def __get_24hr_time(self, time: str) -> tuple[int, int]:
        hh_mm, am_pm = time.split(" ")
        hh, mm = hh_mm.split(":")
        hh, mm = int(hh), int(mm)
        
        if am_pm == "am":
            if hh == 12:
                hh = 0
        else:
            if hh != 12:
                hh += 12
            
        return (hh, mm)

    def get_timings(self, location: str = "dortmund") -> dict[Literal['fajr', 'dhuhr', 'asr', 'maghrib', 'isha'], tuple[int, int]]:
        response = requests.get(f"https://muslimsalat.com/{location}/daily.json", {'key': self.__api_key})
        prayer_timings = response.json()['items'][0]

        return { prayer: self.__get_24hr_time(prayer_timings[prayer]) for prayer in PRAYER }