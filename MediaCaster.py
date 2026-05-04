import pychromecast
from time import sleep
from logger import get_logger

DISCOVER_TIMEOUT = 5

logger = get_logger(__name__)


class MediaCaster:
    def __init__(self, device_name: str, port: int = 8000):
        self.__device_name = device_name
        self.__port = port
        self.__browser: pychromecast.CastBrowser = None
        self.__device: pychromecast.Chromecast = None
        self.__audio_server = None
        self.__base_url = None

    def __set_device(self):
        logger.info(f"Searching for Chromecast device: {self.__device_name}")
        t = 5
        chromecasts, browser = pychromecast.get_listed_chromecasts(friendly_names=[self.__device_name], discovery_timeout=DISCOVER_TIMEOUT)
        while(len(chromecasts) == 0 and t > 0):
            sleep(0.2)
            t = t - 0.2

        if(len(chromecasts) != 0):
            logger.info(f"Found device: {chromecasts[0].cast_info.friendly_name}")
            self.__device = chromecasts[0]
            self.__browser = browser
        else:
            logger.warning(f"Device '{self.__device_name}' not found within {DISCOVER_TIMEOUT} seconds")

    def __set_temporary_volume(self, volume: float):
        device = self.__device
        old_volume = device.status.volume_level
        device.set_volume(volume, 5)

        def reset_volume():
            device.set_volume(old_volume, 5)
            return None
        
        return reset_volume

    def cast_audio(self, audio_source: str, volume: float = None):
        if self.__device is None:
            logger.warning("No device available, skipping playback")
            return

        if audio_source.startswith("http"):
            audio_url = audio_source
        else:
            audio_url = self.__base_url + audio_source

        logger.info(f"Casting audio from: {audio_url}")
        if volume is not None:
            logger.debug(f"Setting volume to: {volume}")

        device = self.__device
        device.wait(5)

        if volume is not None:
            reset = self.__set_temporary_volume(volume)

        media_controller = device.media_controller
        media_controller.play_media(audio_url, 'audio/mp3')
        media_controller.block_until_active()

        logger.debug("Waiting for playback to start")
        while(media_controller.status.player_state != 'PLAYING'):
            sleep(5)
        logger.info("Playback started")

        logger.debug("Waiting for playback to finish")
        while(media_controller.status.player_state == 'PLAYING'):
            sleep(5)
        logger.info("Playback finished")

        if volume is not None:
            reset()

    def __enter__(self):
        from server import AudioServer
        self.__audio_server = AudioServer(port=self.__port)
        try:
            self.__base_url = self.__audio_server.start()
            logger.info(f"Audio server started at {self.__base_url}")
        except Exception as e:
            logger.error(f"Failed to start audio server: {e}")
            raise RuntimeError(f"Failed to start audio server on port {self.__port}: {e}") from e

        self.__set_device()
        return self

    def __exit__(self, type, value, traceback):
        if self.__audio_server:
            self.__audio_server.stop()
            logger.info("Audio server stopped")
        if self.__device != None:
            self.__device.disconnect(5)
            self.__browser.stop_discovery()