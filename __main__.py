import argparse
from MediaCaster import MediaCaster
from scheduler import clean_up_cron_jobs, init_cron_job, update_prayer_schedule
from logger import get_logger

DEFAULT_ADHAN = "Azan_Mecca.mp3"
DEFAULT_FAJR_ADHAN = "Fajr_Azan_Mecca.mp3"
DEFAULT_DEVICE_NAME = "Living Room Speaker"
DEFAULT_CITY = "Dortmund"
DEFAULT_COUNTRY = "Germany"
DEFAULT_USER = "biplobmac"
DEFAULT_LOG = "~/logs/prayer.log"
DEFAULT_PYTHON = "/usr/bin/python"
DEFAULT_PORT = 8000

parser = argparse.ArgumentParser(
    description="Casting the adhan to a chromecast device in the home network"
)
parser.add_argument('--fajr', action='store_true', default=False)
parser.add_argument('--setup', dest='mode', action='store_const', const='setup')
parser.add_argument('--cleanup', dest='mode', action='store_const', const='cleanup')
parser.add_argument('--update', dest='mode', action='store_const', const='update')
parser.add_argument('--device-name', default=DEFAULT_DEVICE_NAME)
parser.add_argument('--adhan', default=DEFAULT_ADHAN)
parser.add_argument('--fajr-adhan', default=DEFAULT_FAJR_ADHAN)
parser.add_argument('--city', default=DEFAULT_CITY)
parser.add_argument('--country', default=DEFAULT_COUNTRY)
parser.add_argument('--user', default=DEFAULT_USER)
parser.add_argument('--log', default=DEFAULT_LOG)
parser.add_argument('--python', default=DEFAULT_PYTHON)
parser.add_argument('--port', type=int, default=DEFAULT_PORT)

args = parser.parse_args()

logger = get_logger(__name__, args.log)

def prayer_call():
    fajr_prayer: str = args.fajr
    logger.info(f"Starting adhan playback - Fajr: {fajr_prayer}")
    try:
        with MediaCaster(args.device_name, args.port) as player:
            if fajr_prayer:
                logger.info("Playing Fajr adhan at reduced volume (0.7)")
                player.cast_audio(args.fajr_adhan, 0.7)
            else:
                logger.info("Playing regular adhan")
                player.cast_audio(args.adhan)
        logger.info("Adhan playback completed successfully")
    except Exception as e:
        logger.error(f"Adhan playback failed: {e}")
    
if __name__ == '__main__':
    mode = args.mode
    if mode == 'setup':
        logger.info("Setting up cron jobs")
        init_cron_job(args.user, args.python, args.city, args.country)
        logger.info("Cron jobs setup completed")
    elif mode == 'cleanup':
        logger.info("Cleaning up cron jobs")
        clean_up_cron_jobs(args.user)
        logger.info("Cron jobs cleanup completed")
    elif mode == 'update':
        logger.info("Updating prayer schedule from API")
        update_prayer_schedule(args.user, args.city, args.country)
        logger.info("Prayer schedule update completed")
    else:
        prayer_call()
