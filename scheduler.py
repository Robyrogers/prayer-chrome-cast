from os import getcwd, getenv
from typing import Literal
from PrayerSchedule import PrayerSchedule
from crontab import CronTab, CronItem

USER = getenv('USER')
PYTHON = getenv('PYTHON', '/usr/bin/python')
CITY = getenv('CITY')
COUNTRY = getenv('COUNTRY')
LOG = getenv('LOG')

def create_prayer_job(prayer: str, time: dict[Literal['hh', 'mm'], int]):
    job = CronItem(
            user=USER,
            comment=f'{prayer} Prayer',
            command=f'cd $DIR && $PYTHON -m pipenv run start --fajr' if prayer == 'Fajr'
                    else f'cd $DIR && $PYTHON -m pipenv run start'
        )
    job.hour.on(time['hh'])
    job.minute.on(time['mm'])
    job.env['DIR'] = getcwd()
    job.env['PYTHON'] = PYTHON
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
            command=f'cd $DIR && $PYTHON -m pipenv run start --update'
        )
        job.minute.on(0)
        job.hour.on(1)
        job.env['DIR'] = getcwd()
        job.env['PYTHON'] = PYTHON
        cron.append(job)

        update_prayer_schedule(cron)

def clean_up_cron_jobs():
    with CronTab(user=USER) as cron:
        for prayer in ['Update', 'Fajr', 'Dhuhr', 'Asr', 'Maghrib', 'Isha']:
            cron.remove_all(comment=f'{prayer} Prayer')