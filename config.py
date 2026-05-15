import argparse
from dataclasses import dataclass

DEFAULT_PORT = 8000
DEFAULT_ADHAN = "assets/azan.mp3"
DEFAULT_FAJR_ADHAN = "assets/fajr_azan.mp3"
DEFAULT_LOG = "log/prayer.log"
DEFAULT_DEVICE_NAME = "Living Room Speaker"

HINT_PORT = str(DEFAULT_PORT)
HINT_ADHAN = DEFAULT_ADHAN
HINT_FAJR_ADHAN = DEFAULT_FAJR_ADHAN
HINT_LOG = DEFAULT_LOG
HINT_DEVICE_NAME = "e.g., Living Room Speaker"
HINT_ADDRESS = "e.g., Dortmund, Germany"


@dataclass
class AdhanConfig:
    """Configuration for adhan playback and Chromecast device."""
    device_name: str
    port: int
    adhan_file: str
    fajr_adhan_file: str
    log_file: str


@dataclass
class LocationConfig:
    """Configuration for location-based prayer time settings."""
    address: str = None


@dataclass
class Config:
    """Main configuration container for the adhan caster."""
    adhan: AdhanConfig
    location: LocationConfig


def prompt_for_value(prompt_text: str, hint: str = None) -> str:
    """Prompt the user for a value with an optional hint.

    Args:
        prompt_text: The prompt to display to the user.
        hint: Optional hint/example to display in brackets.

    Returns:
        The user's input stripped of whitespace, or None if empty.
    """
    if hint:
        value = input(f"{prompt_text} [{hint}]: ")
    else:
        value = input(f"{prompt_text}: ")
    if not value.strip():
        return None
    return value.strip()


def create_parser() -> argparse.ArgumentParser:
    """Create and return the command-line argument parser.

    Returns:
        Configured ArgumentParser for the adhan caster CLI.
    """
    parser = argparse.ArgumentParser(
        description="Casting the adhan to a chromecast device in the home network"
    )
    parser.add_argument('--fajr', action='store_true', default=False)
    parser.add_argument('--setup', dest='mode', action='store_const', const='setup')
    parser.add_argument('--cleanup', dest='mode', action='store_const', const='cleanup')
    parser.add_argument('--update', dest='mode', action='store_const', const='update')
    parser.add_argument('--device-name', default=None)
    parser.add_argument('--adhan', default=DEFAULT_ADHAN)
    parser.add_argument('--fajr-adhan', default=DEFAULT_FAJR_ADHAN)
    parser.add_argument('--address', default=None)
    parser.add_argument('--log', default=DEFAULT_LOG)
    parser.add_argument('--port', type=int, default=DEFAULT_PORT)
    return parser


def prompt_required(prompt_text: str, hint: str = None) -> str:
    """Prompt for a required value, looping until non-empty input is given.

    Args:
        prompt_text: The prompt to display to the user.
        hint: Optional hint/example to display in brackets.

    Returns:
        The user's non-empty input.

    Raises:
        KeyboardInterrupt: If user cancels the input.
    """
    while True:
        value = prompt_for_value(prompt_text, hint)
        if value:
            return value
        print("This field is required. Please enter a value.")


def get_config(args: argparse.Namespace) -> Config:
    """Build a Config object from parsed command-line arguments.

    Args:
        args: Parsed argparse.Namespace containing CLI arguments.

    Returns:
        A Config object with adhan and location sub-configs.
    """
    device_name = args.device_name
    port = args.port
    adhan_file = args.adhan
    fajr_adhan_file = args.fajr_adhan
    log_file = args.log

    address = args.address

    adhan_config = AdhanConfig(
        device_name=device_name,
        port=port,
        adhan_file=adhan_file,
        fajr_adhan_file=fajr_adhan_file,
        log_file=log_file
    )

    location_config = LocationConfig(
        address=address
    )

    return Config(adhan=adhan_config, location=location_config)