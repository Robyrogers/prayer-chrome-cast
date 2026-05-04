import argparse
from os import getenv
from MediaCaster import MediaCaster
from scheduler import clean_up_cron_jobs, init_cron_job, update_prayer_schedule
from logger import get_logger

ADHAN = getenv('ADHAN')
FAJR_ADHAN = getenv('FAJR_ADHAN')
DEVICE_NAME = getenv('DEVICE_NAME')

logger = get_logger(__name__)

parser = argparse.ArgumentParser(
    description="Casting the adhan to a chromecast device in the home network"
)
parser.add_argument('--fajr', action='store_true', default=False)
parser.add_argument('--setup', dest='mode', action='store_const', const='setup')
parser.add_argument('--cleanup', dest='mode', action='store_const', const='cleanup')
parser.add_argument('--update', dest='mode', action='store_const', const='update')

args = parser.parse_args()

def prayer_call():
    fajr_prayer: str = args.fajr
    logger.info(f"Starting adhan playback - Fajr: {fajr_prayer}")
    try:
        with MediaCaster(DEVICE_NAME) as player:
            if fajr_prayer:
                logger.info("Playing Fajr adhan at reduced volume (0.7)")
                player.cast_audio(FAJR_ADHAN, 0.7)
            else:
                logger.info("Playing regular adhan")
                player.cast_audio(ADHAN)
        logger.info("Adhan playback completed successfully")
    except Exception as e:
        logger.error(f"Adhan playback failed: {e}")
    
if __name__ == '__main__':
    mode = args.mode
    if mode == 'setup':
        logger.info("Setting up cron jobs")
        init_cron_job()
        logger.info("Cron jobs setup completed")
    elif mode == 'cleanup':
        logger.info("Cleaning up cron jobs")
        clean_up_cron_jobs()
        logger.info("Cron jobs cleanup completed")
    elif mode == 'update':
        logger.info("Updating prayer schedule from API")
        update_prayer_schedule()
        logger.info("Prayer schedule update completed")
    else:
        prayer_call()
