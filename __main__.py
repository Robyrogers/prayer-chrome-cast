from config import create_parser, get_config
from media import MediaCaster
from scheduler import init_cron_job, update_prayer_schedule, clean_up_cron_jobs
from logger import get_logger

parser = create_parser()
args = parser.parse_args()

config = get_config(args, require_all=False)
logger = get_logger(__name__, config.adhan.log_file)


def play_mode() -> None:
    """Default mode - play adhan to Chromecast device."""
    from config import prompt_required, HINT_CITY, HINT_COUNTRY, HINT_USER

    if not config.adhan.device_name:
        config.adhan.device_name = MediaCaster.discover_and_select(timeout=10)
        if config.adhan.device_name is None:
            print("No device selected. Exiting...")
            return

    if not config.location.city:
        config.location.city = prompt_required("City", HINT_CITY)
    if not config.location.country:
        config.location.country = prompt_required("Country", HINT_COUNTRY)
    if not config.location.user:
        config.location.user = prompt_required("User", HINT_USER)

    adhan_config = config.adhan
    logger.info(f"Starting adhan playback - Fajr: {args.fajr}")
    try:
        with MediaCaster(adhan_config.device_name, adhan_config.port) as player:
            audio_file = adhan_config.fajr_adhan_file if args.fajr else adhan_config.adhan_file
            volume = 0.3 if args.fajr else None
            if args.fajr:
                logger.info("Playing Fajr adhan at reduced volume (0.7)")
            else:
                logger.info("Playing regular adhan")
            player.cast_audio(audio_file, volume)
        logger.info("Adhan playback completed successfully")
    except Exception as e:
        logger.error(f"Adhan playback failed: {e}")


def setup_mode() -> None:
    """Initialize cron jobs for prayer schedule."""
    from config import prompt_required, HINT_CITY, HINT_COUNTRY, HINT_USER

    city = args.city or prompt_required("City", HINT_CITY)
    country = args.country or prompt_required("Country", HINT_COUNTRY)
    user = args.user or prompt_required("User", HINT_USER)

    device_name = args.device_name
    if device_name is None:
        device_name = MediaCaster.discover_and_select(timeout=10)
        if device_name is None:
            print("No device selected. Exiting...")
            return
    else:
        print(f"Using provided device: {device_name}")

    logger.info(f"Setting up cron jobs - city: {city}, country: {country}, user: {user}, device: {device_name}")
    init_cron_job(
        user=user,
        city=city,
        country=country,
        port=config.adhan.port,
        device_name=device_name,
        adhan=config.adhan.adhan_file,
        fajr_adhan=config.adhan.fajr_adhan_file,
        log=config.adhan.log_file
    )
    logger.info("Cron jobs setup completed")


def cleanup_mode() -> None:
    """Remove all cron jobs."""
    from config import prompt_required, HINT_USER

    user = args.user or prompt_required("User", HINT_USER)
    logger.info("Cleaning up cron jobs")
    clean_up_cron_jobs(user)
    logger.info("Cron jobs cleanup completed")


def update_mode() -> None:
    """Refresh prayer times from API and update cron."""
    from config import prompt_required, HINT_CITY, HINT_COUNTRY, HINT_USER

    city = args.city or prompt_required("City", HINT_CITY)
    country = args.country or prompt_required("Country", HINT_COUNTRY)
    user = args.user or prompt_required("User", HINT_USER)

    logger.info("Updating prayer schedule from API")
    update_prayer_schedule(
        user=user,
        city=city,
        country=country,
        port=config.adhan.port,
        device_name=config.adhan.device_name,
        adhan=config.adhan.adhan_file,
        fajr_adhan=config.adhan.fajr_adhan_file,
        log=config.adhan.log_file
    )
    logger.info("Prayer schedule update completed")


def main() -> None:
    """Dispatch to appropriate mode function based on CLI arguments."""
    mode_dispatch = {
        'setup': setup_mode,
        'cleanup': cleanup_mode,
        'update': update_mode,
    }
    mode_fn = mode_dispatch.get(args.mode, play_mode)
    mode_fn()


if __name__ == '__main__':
    main()