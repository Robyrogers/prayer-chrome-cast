from os import getcwd
from typing import Optional, Dict
import time
import pychromecast
import zeroconf
from prayer import PrayerSchedule, PrayerTime
from crontab import CronTab, CronItem
from logger import get_logger

logger = get_logger(__name__)

PRAYER_ORDER = ['Fajr', 'Dhuhr', 'Asr', 'Maghrib', 'Isha']


class _DeviceListener:
    def add_cast(self, uuid, service): pass
    def remove_cast(self, uuid, service): pass
    def update_cast(self, uuid, service): pass


def discover_devices(timeout: int = 10) -> Dict[str, str]:
    """Discover Chromecast devices on the network.

    Args:
        timeout: Number of seconds to search for devices.

    Returns:
        Dict mapping device UUID to friendly name.
    """
    logger.info(f"Searching for Chromecast devices (timeout: {timeout}s)")
    zconf = zeroconf.Zeroconf()
    browser = pychromecast.CastBrowser(_DeviceListener(), zconf)
    browser.start_discovery()
    time.sleep(timeout)
    browser.stop_discovery()
    zconf.close()

    devices = {uuid: dev.friendly_name for uuid, dev in browser.devices.items()}
    logger.info(f"Found {len(devices)} device(s)")
    return devices


def _build_command(
    user: str,
    python_path: str,
    city: str,
    country: str,
    port: int,
    device_name: str,
    adhan: str,
    fajr_adhan: str,
    log: str,
    is_fajr: bool = False,
    is_update: bool = False
) -> str:
    cmd = (
        f"cd $DIR && $PYTHON . "
        f"--user {user} "
        f"--python {python_path} "
        f"--city {city} "
        f"--country {country} "
        f"--port {port} "
        f"--device-name \"{device_name}\" "
        f"--adhan \"{adhan}\" "
        f"--fajr-adhan \"{fajr_adhan}\" "
        f"--log \"{log}\""
    )
    if is_fajr:
        cmd += ' --fajr'
    if is_update:
        cmd += ' --update'
    return cmd


def _create_job(
    prayer: str,
    time: PrayerTime,
    user: str,
    python_path: str,
    city: str,
    country: str,
    port: int,
    device_name: str,
    adhan: str,
    fajr_adhan: str,
    log: str
) -> CronItem:
    cmd = _build_command(
        user, python_path, city, country, port,
        device_name, adhan, fajr_adhan, log,
        is_fajr=(prayer == 'Fajr')
    )
    job = CronItem(user=user, comment=f'{prayer} Prayer', command=cmd)
    job.hour.on(time.hour)
    job.minute.on(time.minute)
    job.env['DIR'] = getcwd()
    job.env['PYTHON'] = python_path
    return job


def update_prayer_schedule(
    user: str,
    city: str,
    country: str,
    cron: Optional[CronTab] = None,
    python_path: str = "/usr/bin/python",
    port: int = 8000,
    device_name: str = "Living Room Speaker",
    adhan: str = "assets/azan.mp3",
    fajr_adhan: str = "assets/fajr_azan.mp3",
    log: str = "~/logs/prayer.log"
) -> None:
    cron_in_use = cron if cron else CronTab(user=user)

    logger.info("Fetching prayer schedule from API")
    schedule = PrayerSchedule(city, country)
    timings: Dict[str, PrayerTime] = schedule.get_timings()

    for name, time_obj in timings.items():
        prayer = PRAYER_ORDER[['fajr', 'dhuhr', 'asr', 'maghrib', 'isha'].index(name)]
        logger.info(f"Scheduling {prayer} prayer at {time_obj.hour:02d}:{time_obj.minute:02d}")
        cron_in_use.remove_all(comment=f'{prayer} Prayer')
        cron_in_use.append(_create_job(
            prayer, time_obj, user, python_path, city, country, port,
            device_name, adhan, fajr_adhan, log
        ))

    if cron is None:
        cron_in_use.write()
        logger.info("Prayer schedule updated in cron")


def init_cron_job(
    user: str,
    python_path: str,
    city: str,
    country: str,
    port: int = 8000,
    device_name: str = "Living Room Speaker",
    adhan: str = "assets/azan.mp3",
    fajr_adhan: str = "assets/fajr_azan.mp3",
    log: str = "~/logs/prayer.log"
) -> None:
    with CronTab(user=user) as cron:
        logger.info("Creating daily update cron job at 01:00")
        cmd = _build_command(
            user, python_path, city, country, port,
            device_name, adhan, fajr_adhan, log,
            is_update=True
        )
        job = CronItem(user=user, comment='Update Prayer', command=cmd)
        job.minute.on(0)
        job.hour.on(1)
        job.env['DIR'] = getcwd()
        job.env['PYTHON'] = python_path
        cron.append(job)

        update_prayer_schedule(
            user, city, country, cron, python_path,
            port, device_name, adhan, fajr_adhan, log
        )


def clean_up_cron_jobs(user: str) -> None:
    with CronTab(user=user) as cron:
        for prayer in ['Update', 'Fajr', 'Dhuhr', 'Asr', 'Maghrib', 'Isha']:
            removed = cron.remove_all(comment=f'{prayer} Prayer')
            if removed:
                logger.info(f"Removed cron job: {prayer} Prayer")