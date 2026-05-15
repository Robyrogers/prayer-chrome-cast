from os import getcwd, getuid
import pwd
from typing import Optional, Dict
import sys
import time
import pychromecast
import zeroconf
from prayer import PrayerSchedule, PrayerTime
from crontab import CronTab, CronItem
from logger import get_logger
from config import DEFAULT_PORT, DEFAULT_ADHAN, DEFAULT_FAJR_ADHAN, DEFAULT_LOG

logger = get_logger(__name__)

PRAYER_ORDER = ['Fajr', 'Dhuhr', 'Asr', 'Maghrib', 'Isha']


def get_current_user() -> str:
    """Get current user for crontab operations with multiple fallback methods."""
    try:
        return pwd.getpwuid(getuid()).pw_name
    except Exception:
        pass

    import os
    if user := os.environ.get('USER'):
        return user
    if user := os.environ.get('USERNAME'):
        return user

    raise RuntimeError("Could not detect current user. Please run with sudo or specify user.")


class _DeviceListener:
    def add_cast(self, uuid, service): pass
    def remove_cast(self, uuid, service): pass
    def update_cast(self, uuid, service): pass


def discover_devices(timeout: int = 10) -> Dict[str, str]:
    """Discover Chromecast devices on the network.

    Args:
        timeout: Number of seconds to search for devices.

    Returns:
        Dictionary mapping UUID to device friendly name.
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
    address: str,
    port: int,
    device_name: str,
    adhan: str,
    fajr_adhan: str,
    log: str,
    is_fajr: bool = False,
    is_update: bool = False
) -> str:
    python_exec = sys.executable
    cmd = (
        f"cd $DIR && {python_exec} . "
        f"--user {user} "
        f"--address \"{address}\" "
        f"--device-name \"{device_name}\""
    )
    if port != DEFAULT_PORT:
        cmd += f' --port {port}'
    if adhan != DEFAULT_ADHAN:
        cmd += f' --adhan "{adhan}"'
    if fajr_adhan != DEFAULT_FAJR_ADHAN:
        cmd += f' --fajr-adhan "{fajr_adhan}"'
    if log != DEFAULT_LOG:
        cmd += f' --log "{log}"'
    if is_fajr:
        cmd += ' --fajr'
    if is_update:
        cmd += ' --update'
    return cmd


def _create_job(
    prayer: str,
    time: PrayerTime,
    user: str,
    address: str,
    port: int,
    device_name: str,
    adhan: str,
    fajr_adhan: str,
    log: str
) -> CronItem:
    cmd = _build_command(
        user, address, port,
        device_name, adhan, fajr_adhan, log,
        is_fajr=(prayer == 'Fajr')
    )
    job = CronItem(user=user, comment=f'{prayer} Prayer', command=cmd)
    job.setall(time.minute, time.hour, '*', '*', '*')
    job.env['DIR'] = getcwd()
    return job


def update_prayer_schedule(
    address: str,
    user: str,
    cron: Optional[CronTab] = None,
    port: Optional[int] = None,
    device_name: Optional[str] = None,
    adhan: Optional[str] = None,
    fajr_adhan: Optional[str] = None,
    log: Optional[str] = None
) -> None:
    port = port if port is not None else DEFAULT_PORT
    device_name = device_name if device_name else "Living Room Speaker"
    adhan = adhan if adhan is not None else DEFAULT_ADHAN
    fajr_adhan = fajr_adhan if fajr_adhan is not None else DEFAULT_FAJR_ADHAN
    log = log if log is not None else DEFAULT_LOG

    cron_in_use = cron if cron else CronTab(user=user)

    logger.info("Fetching prayer schedule from API")
    schedule = PrayerSchedule(address)
    timings: Dict[str, PrayerTime] = schedule.get_timings()

    for name, time_obj in timings.items():
        prayer = PRAYER_ORDER[['fajr', 'dhuhr', 'asr', 'maghrib', 'isha'].index(name)]
        logger.info(f"Scheduling {prayer} prayer at {time_obj.hour:02d}:{time_obj.minute:02d}")
        cron_in_use.remove_all(comment=f'{prayer} Prayer')
        cron_in_use.append(_create_job(
            prayer, time_obj, user, address, port,
            device_name, adhan, fajr_adhan, log
        ))

    if cron is None:
        cron_in_use.write()
        logger.info("Prayer schedule updated in cron")


def init_cron_job(
    address: str,
    user: str,
    port: Optional[int] = None,
    device_name: Optional[str] = None,
    adhan: Optional[str] = None,
    fajr_adhan: Optional[str] = None,
    log: Optional[str] = None
) -> None:
    port = port if port is not None else DEFAULT_PORT
    device_name = device_name if device_name else "Living Room Speaker"
    adhan = adhan if adhan is not None else DEFAULT_ADHAN
    fajr_adhan = fajr_adhan if fajr_adhan is not None else DEFAULT_FAJR_ADHAN
    log = log if log is not None else DEFAULT_LOG

    python_exec = sys.executable
    with CronTab(user=user) as cron:
        logger.info("Creating daily update cron job at 01:00")
        cmd = _build_command(
            user, address, port,
            device_name, adhan, fajr_adhan, log,
            is_update=True
        )
        job = CronItem(user=user, comment='Update Prayer', command=cmd)
        job.setall(0, 1, '*', '*', '*')
        job.env['DIR'] = getcwd()
        cron.append(job)

        update_prayer_schedule(
            address=address,
            user=user,
            cron=cron,
            port=port,
            device_name=device_name,
            adhan=adhan,
            fajr_adhan=fajr_adhan,
            log=log
        )


def clean_up_cron_jobs(user: str) -> None:
    with CronTab(user=user) as cron:
        for prayer in ['Update', 'Fajr', 'Dhuhr', 'Asr', 'Maghrib', 'Isha']:
            removed = cron.remove_all(comment=f'{prayer} Prayer')
            if removed:
                logger.info(f"Removed cron job: {prayer} Prayer")