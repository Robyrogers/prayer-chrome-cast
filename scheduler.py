from os import getcwd, getenv
from typing import Literal
from PrayerSchedule import PrayerSchedule
from time import strftime

DEFAULT_PYTHON = f"{getcwd()}/.venv/bin/python"
USER = getenv('USER')
PYTHON = getenv('PYTHON', DEFAULT_PYTHON)
CITY = getenv('CITY')
COUNTRY = getenv('COUNTRY')
CRON_DIR = getenv('CRON_DIR', getcwd())

def generate_cron_job_string(
        cron_schedule: str, 
        script_location: str,
        flags: str = "", 
        user: str = "ryad_pi", 
        python: str = DEFAULT_PYTHON
    ) -> str:
    return f"{cron_schedule} {user} {python} {script_location} {flags}"

def setup_scheduler():
    script_location = f"{getcwd()}/scheduler.py"
    with open(f"{CRON_DIR}/PrayerScheduler", mode='w') as file:
        file.write(generate_cron_job_string("0 1 * * *", script_location, user=USER, python=PYTHON))
    get_prayer_schedule_and_generate_cron_jobs()
        
def get_prayer_schedule_and_generate_cron_jobs():
    prayer_schedule = PrayerSchedule(CITY, COUNTRY)
    timings = prayer_schedule.get_timings()
    with open(f"{CRON_DIR}/DailyPrayerScheduler", mode='w') as file:
        file.write(f"# Updated {strftime('%Y-%m-%d %H-%M')}\n")
        for prayer, time in timings.items():
            file.write(f"{create_prayer_call_job(prayer, time)}\n") 
    

def create_prayer_call_job(prayer: str, time: dict[Literal['hh', 'mm'], int]):
    script_location = f"{getcwd()}/"
    if prayer == 'Fajr':
        cron_string = generate_cron_job_string(f"{time['mm']} {time['hh']} * * *", script_location, "--fajr", user=USER, python=PYTHON)
    else:
        cron_string = generate_cron_job_string(f"{time['mm']} {time['hh']} * * *", script_location, user=USER, python=PYTHON)
    return cron_string

if __name__ == '__main__':
    get_prayer_schedule_and_generate_cron_jobs()