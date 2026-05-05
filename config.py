import argparse
import sys
from dataclasses import dataclass
from logger import get_logger

DEFAULT_ADHAN = "assets/azan.mp3"
DEFAULT_FAJR_ADHAN = "assets/fajr_azan.mp3"
DEFAULT_DEVICE_NAME = "Living Room Speaker"
DEFAULT_CITY = "Dortmund"
DEFAULT_COUNTRY = "Germany"
DEFAULT_USER = "biplobmac"
DEFAULT_LOG = "log/prayer.log"
DEFAULT_PORT = 8000


def get_python_executable() -> str:
    return sys.executable


@dataclass
class AdhanConfig:
    device_name: str
    port: int
    adhan_file: str
    fajr_adhan_file: str
    log_file: str


@dataclass
class LocationConfig:
    city: str
    country: str
    user: str


@dataclass
class Config:
    adhan: AdhanConfig
    location: LocationConfig


def prompt_for_value(prompt_text: str, default: str = None) -> str:
    if default:
        value = input(f"{prompt_text} (default: {default}): ")
        return value.strip() if value.strip() else default
    else:
        value = input(f"{prompt_text}: ")
        return value.strip()


def create_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(
        description="Casting the adhan to a chromecast device in the home network"
    )
    parser.add_argument('--fajr', action='store_true', default=False)
    parser.add_argument('--setup', dest='mode', action='store_const', const='setup')
    parser.add_argument('--cleanup', dest='mode', action='store_const', const='cleanup')
    parser.add_argument('--update', dest='mode', action='store_const', const='update')
    parser.add_argument('--status', dest='mode', action='store_const', const='status')
    parser.add_argument('--device-name', default=None)
    parser.add_argument('--adhan', default=None)
    parser.add_argument('--fajr-adhan', default=None)
    parser.add_argument('--city', default=None)
    parser.add_argument('--country', default=None)
    parser.add_argument('--user', default=None)
    parser.add_argument('--log', default=None)
    parser.add_argument('--port', type=int, default=None)
    return parser


def get_config(args: argparse.Namespace, prompt: bool = False) -> Config:
    device_name = args.device_name or DEFAULT_DEVICE_NAME
    port = args.port or DEFAULT_PORT
    adhan_file = args.adhan or DEFAULT_ADHAN
    fajr_adhan_file = args.fajr_adhan or DEFAULT_FAJR_ADHAN
    log_file = args.log or DEFAULT_LOG

    city = args.city
    country = args.country
    user = args.user

    if prompt:
        city = city or prompt_for_value("City", DEFAULT_CITY)
        country = country or prompt_for_value("Country", DEFAULT_COUNTRY)
        user = user or prompt_for_value("User", DEFAULT_USER)

    adhan_config = AdhanConfig(
        device_name=device_name,
        port=port,
        adhan_file=adhan_file,
        fajr_adhan_file=fajr_adhan_file,
        log_file=log_file
    )

    location_config = LocationConfig(
        city=city or DEFAULT_CITY,
        country=country or DEFAULT_COUNTRY,
        user=user or DEFAULT_USER
    )

    return Config(adhan=adhan_config, location=location_config)