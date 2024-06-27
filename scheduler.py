from os import getcwd, getenv
from typing import Literal
from PrayerSchedule import PrayerSchedule
from crontab import CronTab, CronItem

USER = getenv('USER')
PYTHON = getenv('PYTHON', 'python')
CITY = getenv('CITY')
COUNTRY = getenv('COUNTRY')
CRON_DIR = getenv('CRON_DIR', getcwd())
LOG = getenv('LOG')

def create_prayer_job(prayer: str, time: dict[Literal['hh', 'mm'], int]):
    job = CronItem(
            user=USER,
            comment=f'{prayer} Prayer',
            command=f'cd {getcwd()} && {PYTHON} -m pipenv run start --fajr >> {LOG} 2>&1' if prayer == 'Fajr'
                    else f'cd {getcwd()} && {PYTHON} -m pipenv run start >> {LOG} 2>&1'
        )
    job.hour.on(time['hh'])
    job.minute.on(time['mm'])    
    return job

def update_prayer_schedule(cron: CronTab = None):
    cron_in_use = cron if cron else CronTab(user=USER)
    
    prayer_schedule = PrayerSchedule(CITY, COUNTRY)
    timings = prayer_schedule.get_timings()
    for prayer, time in timings.items():
        cron_in_use.remove_all(comment=f'{prayer} Prayer')
        cron_in_use.append(create_prayer_job(prayer, time))
    
    if cron == None:
        cron_in_use.write()

def init_cron_job():
    with CronTab(user=USER) as cron:
        job = CronItem(
            user=USER,
            comment='Update Prayer',
            command=f'cd {getcwd()} && {PYTHON} -m pipenv run start --update >> {LOG} 2>&1'
        )
        job.minute.on(0)
        job.hour.on(1)
        cron.append(job)

        update_prayer_schedule(cron)

def clean_up_cron_jobs():
    with CronTab(user=USER) as cron:
        for prayer in ['Update', 'Fajr', 'Dhuhr', 'Asr', 'Maghrib', 'Isha']:
            cron.remove_all(comment=f'{prayer} Prayer')