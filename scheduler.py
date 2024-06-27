from os import getcwd, getenv
from typing import Literal
from PrayerSchedule import PrayerSchedule
from crontab import CronTab, CronItem

DEFAULT_PYTHON = f"{getcwd()}/.venv/bin/python"
USER = getenv('USER')
PYTHON = getenv('PYTHON', DEFAULT_PYTHON)
CITY = getenv('CITY')
COUNTRY = getenv('COUNTRY')
CRON_DIR = getenv('CRON_DIR', getcwd())

def create_prayer_job(prayer: str, time: dict[Literal['hh', 'mm'], int]):
    script_location = f"{getcwd()}/"

    job = CronItem(
            user=USER,
            comment=f'{prayer} Prayer',
            command=f'{PYTHON} {script_location} --fajr' if prayer == 'Fajr' else f'{PYTHON} {script_location}'
        )
    job.hour.on(time['hh'])
    job.minute.on(time['mm'])    
    return job

def update_prayer_schedule(cron: CronTab):
    prayer_schedule = PrayerSchedule(CITY, COUNTRY)
    timings = prayer_schedule.get_timings()
    for prayer, time in timings.items():
        cron.remove_all(comment=f'{prayer} Prayer')
        cron.append(create_prayer_job(prayer, time))

def init_cron_job():
    script_location = f"{getcwd()}/scheduler.py"

    with CronTab(user=USER) as cron:
        job = CronItem(
            user=USER,
            comment='Update Prayer',
            command=f'{PYTHON} {script_location}'
        )
        job.minute.on(0)
        job.hour.on(1)
        cron.append(job)

        update_prayer_schedule(cron)

def clean_up_cron_jobs():
    with CronTab(user=USER) as cron:
        for prayer in ['Update', 'Fajr', 'Dhuhr', 'Asr', 'Maghrib', 'Isha']:
            cron.remove_all(comment=f'{prayer} Prayer')

if __name__ == '__main__':
    init_cron_job()