from config import create_parser, get_config, Config, prompt_required, HINT_ADDRESS
from media import MediaCaster
from scheduler import init_cron_job, update_prayer_schedule, clean_up_cron_jobs, get_current_user
from logger import get_logger

parser = create_parser()
args = parser.parse_args()


def play_mode(config: Config, user: str) -> None:
    """Default mode - play adhan to Chromecast device."""
    if not config.adhan.device_name:
        config.adhan.device_name = MediaCaster.discover_and_select(timeout=10)
        if config.adhan.device_name is None:
            print("No device selected. Exiting...")
            return

    if not config.location.address:
        config.location.address = prompt_required("Address", HINT_ADDRESS)

    logger = get_logger(__name__, config.adhan.log_file)
    logger.info(f"Starting adhan playback - Fajr: {args.fajr}")
    try:
        with MediaCaster(config.adhan.device_name, config.adhan.port) as player:
            audio_file = config.adhan.fajr_adhan_file if args.fajr else config.adhan.adhan_file
            volume = 0.3 if args.fajr else None
            if args.fajr:
                logger.info("Playing Fajr adhan at reduced volume (0.3)")
            else:
                logger.info("Playing regular adhan")
            player.cast_audio(audio_file, volume)
        logger.info("Adhan playback completed successfully")
    except Exception as e:
        logger.error(f"Adhan playback failed: {e}")


def setup_mode(config: Config, user: str) -> None:
    """Initialize cron jobs for prayer schedule."""
    if not config.location.address:
        config.location.address = prompt_required("Address", HINT_ADDRESS)

    device_name = config.adhan.device_name
    if device_name is None:
        device_name = MediaCaster.discover_and_select(timeout=10)
        if device_name is None:
            print("No device selected. Exiting...")
            return

    logger = get_logger(__name__, config.adhan.log_file)
    logger.info(f"Setting up cron jobs - address: {config.location.address}, user: {user}, device: {device_name}")
    init_cron_job(
        address=config.location.address,
        user=user,
        port=config.adhan.port,
        device_name=device_name,
        adhan=config.adhan.adhan_file,
        fajr_adhan=config.adhan.fajr_adhan_file,
        log=config.adhan.log_file
    )
    logger.info("Cron jobs setup completed")


def cleanup_mode(config: Config, user: str) -> None:
    """Remove all cron jobs."""
    logger = get_logger(__name__, config.adhan.log_file)
    logger.info("Cleaning up cron jobs")
    clean_up_cron_jobs(user)
    logger.info("Cron jobs cleanup completed")


def update_mode(config: Config, user: str) -> None:
    """Refresh prayer times from API and update cron."""
    if not config.location.address:
        config.location.address = prompt_required("Address", HINT_ADDRESS)

    logger = get_logger(__name__, config.adhan.log_file)
    logger.info("Updating prayer schedule from API")
    update_prayer_schedule(
        address=config.location.address,
        user=user,
        port=config.adhan.port,
        device_name=config.adhan.device_name,
        adhan=config.adhan.adhan_file,
        fajr_adhan=config.adhan.fajr_adhan_file,
        log=config.adhan.log_file
    )
    logger.info("Prayer schedule update completed")


def main() -> None:
    """Dispatch to appropriate mode function based on CLI arguments."""
    user = get_current_user()
    config = get_config(args)

    mode_dispatch = {
        'setup': setup_mode,
        'cleanup': cleanup_mode,
        'update': update_mode,
    }
    mode_fn = mode_dispatch.get(args.mode, play_mode)
    mode_fn(config, user)


if __name__ == '__main__':
    main()