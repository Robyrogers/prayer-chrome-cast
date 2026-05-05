from config import create_parser, get_config
from media import MediaCaster
from scheduler import init_cron_job, update_prayer_schedule, clean_up_cron_jobs
from logger import get_logger

parser = create_parser()
args = parser.parse_args()

config = get_config(args)
logger = get_logger(__name__, config.adhan.log_file)


def prayer_call() -> None:
    adhan_config = config.adhan
    logger.info(f"Starting adhan playback - Fajr: {args.fajr}")
    try:
        with MediaCaster(adhan_config.device_name, adhan_config.port) as player:
            audio_file = adhan_config.fajr_adhan_file if args.fajr else adhan_config.adhan_file
            volume = 0.7 if args.fajr else None
            if args.fajr:
                logger.info("Playing Fajr adhan at reduced volume (0.7)")
            else:
                logger.info("Playing regular adhan")
            player.cast_audio(audio_file, volume)
        logger.info("Adhan playback completed successfully")
    except Exception as e:
        logger.error(f"Adhan playback failed: {e}")


def main() -> None:
    mode = args.mode

    if mode == 'setup':
        from config import prompt_for_value, DEFAULT_CITY, DEFAULT_COUNTRY, DEFAULT_USER, DEFAULT_DEVICE_NAME
        from scheduler import discover_devices

        city = args.city or prompt_for_value("City", DEFAULT_CITY)
        country = args.country or prompt_for_value("Country", DEFAULT_COUNTRY)
        user = args.user or prompt_for_value("User", DEFAULT_USER)

        device_name = args.device_name
        if device_name is None:
            print("Searching for Chromecast devices (10 seconds)...")
            devices = discover_devices(timeout=10)
            if not devices:
                print("ERROR: No Chromecast devices found on network.")
                print("Please ensure your Chromecast is powered on and connected to the same network.")
                return
            print("Available devices:")
            for i, name in enumerate(devices.values(), 1):
                print(f"  {i}. {name}")
            choice = input("Select device (number): ")
            try:
                device_name = list(devices.values())[int(choice) - 1]
                print(f"Selected: {device_name}")
            except (ValueError, IndexError):
                print("ERROR: Invalid selection.")
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

    elif mode == 'cleanup':
        from config import prompt_for_value, DEFAULT_USER
        user = args.user or prompt_for_value("User", DEFAULT_USER)
        logger.info("Cleaning up cron jobs")
        clean_up_cron_jobs(user)
        logger.info("Cron jobs cleanup completed")

    elif mode == 'update':
        from config import prompt_for_value, DEFAULT_CITY, DEFAULT_COUNTRY, DEFAULT_USER
        city = args.city or prompt_for_value("City", DEFAULT_CITY)
        country = args.country or prompt_for_value("Country", DEFAULT_COUNTRY)
        user = args.user or prompt_for_value("User", DEFAULT_USER)

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

    else:
        prayer_call()


if __name__ == '__main__':
    main()