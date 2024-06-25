from os import getcwd, getenv
from typing import Literal
from PrayerSchedule import PrayerSchedule

DEFAULT_PYTHON = f"{getcwd()}/.venv/bin/python"
USER = getenv('USER')
PYTHON = getenv('PYTHON', DEFAULT_PYTHON)
CITY = getenv('CITY')
COUNTRY = getenv('COUNTRY')

def generate_cron_job_string(
        cron_schedule: str, 
        script_location: str,
        flags: str = "", 
        user: str = "ryad_pi", 
        python: str = DEFAULT_PYTHON
    ) -> str:
    return f"{cron_schedule} {user} {python} {script_location} {flags}"

def get_prayer_schedule_and_generate_cron_jobs():
    prayer_schedule = PrayerSchedule(CITY, COUNTRY)
    timings = prayer_schedule.get_timings()
    for prayer, time in timings.items():
        create_prayer_call_job(prayer, time)
    

def create_prayer_call_job(prayer: str, time: dict[Literal['hh', 'mm'], int]):
    script_location = f"{getcwd()}/"
    if prayer == 'Fajr':
        print(generate_cron_job_string(f"{time['mm']} {time['hh']} * * *", script_location, "--fajr", user=USER, python=PYTHON))
    else:
        print(generate_cron_job_string(f"{time['mm']} {time['hh']} * * *", script_location, user=USER, python=PYTHON))

if __name__ == '__main__':
    get_prayer_schedule_and_generate_cron_jobs()