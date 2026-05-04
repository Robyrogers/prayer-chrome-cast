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


def prompt_for_value(prompt_text: str, default: str = None) -> str:
    if default:
        value = input(f"{prompt_text} (default: {default}): ")
        return value.strip() if value.strip() else default
    else:
        value = input(f"{prompt_text}: ")
        return value.strip()


parser = argparse.ArgumentParser(
    description="Casting the adhan to a chromecast device in the home network"
)
parser.add_argument('--fajr', action='store_true', default=False)
parser.add_argument('--setup', dest='mode', action='store_const', const='setup')
parser.add_argument('--cleanup', dest='mode', action='store_const', const='cleanup')
parser.add_argument('--update', dest='mode', action='store_const', const='update')
parser.add_argument('--device-name', default=None)
parser.add_argument('--adhan', default=None)
parser.add_argument('--fajr-adhan', default=None)
parser.add_argument('--city', default=None)
parser.add_argument('--country', default=None)
parser.add_argument('--user', default=None)
parser.add_argument('--log', default=None)
parser.add_argument('--python', default=None)
parser.add_argument('--port', type=int, default=None)

args = parser.parse_args()

logger = get_logger(__name__, args.log or DEFAULT_LOG)

def prayer_call():
    fajr_prayer: str = args.fajr
    device_name = args.device_name or DEFAULT_DEVICE_NAME
    port = args.port or DEFAULT_PORT
    adhan = args.adhan or DEFAULT_ADHAN
    fajr_adhan = args.fajr_adhan or DEFAULT_FAJR_ADHAN

    logger.info(f"Starting adhan playback - Fajr: {fajr_prayer}")
    try:
        with MediaCaster(device_name, port) as player:
            if fajr_prayer:
                logger.info("Playing Fajr adhan at reduced volume (0.7)")
                player.cast_audio(fajr_adhan, 0.7)
            else:
                logger.info("Playing regular adhan")
                player.cast_audio(adhan)
        logger.info("Adhan playback completed successfully")
    except Exception as e:
        logger.error(f"Adhan playback failed: {e}")
    
if __name__ == '__main__':
    mode = args.mode
    if mode == 'setup':
        logger.info("Setting up cron jobs - prompting for required values")

        city = args.city or prompt_for_value("City", DEFAULT_CITY)
        country = args.country or prompt_for_value("Country", DEFAULT_COUNTRY)
        user = args.user or prompt_for_value("User", DEFAULT_USER)

        logger.info(f"Using city: {city}, country: {country}, user: {user}")

        init_cron_job(
            user=user,
            python_path=args.python or DEFAULT_PYTHON,
            city=city,
            country=country,
            port=args.port or DEFAULT_PORT,
            device_name=args.device_name or DEFAULT_DEVICE_NAME,
            adhan=args.adhan or DEFAULT_ADHAN,
            fajr_adhan=args.fajr_adhan or DEFAULT_FAJR_ADHAN,
            log=args.log or DEFAULT_LOG
        )
        logger.info("Cron jobs setup completed")
    elif mode == 'cleanup':
        logger.info("Cleaning up cron jobs")
        user = args.user or prompt_for_value("User", DEFAULT_USER)
        clean_up_cron_jobs(user)
        logger.info("Cron jobs cleanup completed")
    elif mode == 'update':
        logger.info("Updating prayer schedule from API")
        city = args.city or prompt_for_value("City", DEFAULT_CITY)
        country = args.country or prompt_for_value("Country", DEFAULT_COUNTRY)
        user = args.user or prompt_for_value("User", DEFAULT_USER)

        update_prayer_schedule(
            user=user,
            city=city,
            country=country,
            python_path=args.python or DEFAULT_PYTHON,
            port=args.port or DEFAULT_PORT,
            device_name=args.device_name or DEFAULT_DEVICE_NAME,
            adhan=args.adhan or DEFAULT_ADHAN,
            fajr_adhan=args.fajr_adhan or DEFAULT_FAJR_ADHAN,
            log=args.log or DEFAULT_LOG
        )
        logger.info("Prayer schedule update completed")
    else:
        prayer_call()
