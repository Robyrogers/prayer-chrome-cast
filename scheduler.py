from os import getcwd
from typing import Literal
from PrayerSchedule import PrayerSchedule
from crontab import CronTab, CronItem
from logger import get_logger

logger = get_logger(__name__)


def create_prayer_job(prayer: str, time: dict[Literal['hh', 'mm'], int], user: str, python_path: str):
    job = CronItem(
            user=user,
            comment=f'{prayer} Prayer',
            command=f'cd $DIR && $PYTHON . --fajr' if prayer == 'Fajr'
                    else f'cd $DIR && $PYTHON .'
        )
    job.hour.on(time['hh'])
    job.minute.on(time['mm'])
    job.env['DIR'] = getcwd()
    job.env['PYTHON'] = python_path
    return job


def update_prayer_schedule(user: str, city: str, country: str, cron: CronTab = None, python_path: str = "/usr/bin/python"):
    cron_in_use = cron if cron else CronTab(user=user)

    logger.info("Fetching prayer schedule from API")
    prayer_schedule = PrayerSchedule(city, country)
    timings = prayer_schedule.get_timings()

    for prayer, time in timings.items():
        logger.info(f"Scheduling {prayer} prayer at {time['hh']:02d}:{time['mm']:02d}")
        cron_in_use.remove_all(comment=f'{prayer} Prayer')
        cron_in_use.append(create_prayer_job(prayer, time, user, python_path))

    if cron == None:
        cron_in_use.write()
        logger.info("Prayer schedule updated in cron")


def init_cron_job(user: str, python_path: str, city: str, country: str):
    with CronTab(user=user) as cron:
        logger.info("Creating daily update cron job at 01:00")
        job = CronItem(
            user=user,
            comment='Update Prayer',
            command=f'cd $DIR && $PYTHON . --update'
        )
        job.minute.on(0)
        job.hour.on(1)
        job.env['DIR'] = getcwd()
        job.env['PYTHON'] = python_path
        cron.append(job)

        update_prayer_schedule(user, city, country, cron, python_path)


def clean_up_cron_jobs(user: str):
    with CronTab(user=user) as cron:
        for prayer in ['Update', 'Fajr', 'Dhuhr', 'Asr', 'Maghrib', 'Isha']:
            removed = cron.remove_all(comment=f'{prayer} Prayer')
            if removed:
                logger.info(f"Removed cron job: {prayer} Prayer")