import pychromecast
from time import sleep
from typing import Optional
from logger import get_logger

DISCOVER_TIMEOUT = 5

logger = get_logger(__name__)


class MediaCaster:
    def __init__(self, device_name: str, port: int = 8000) -> None:
        self._device_name = device_name
        self._port = port
        self._browser: Optional[pychromecast.CastBrowser] = None
        self._device: Optional[pychromecast.Chromecast] = None
        self._audio_server = None
        self._base_url: Optional[str] = None

    def _set_device(self) -> None:
        logger.info(f"Searching for Chromecast device: {self._device_name}")
        t = 5
        chromecasts, browser = pychromecast.get_listed_chromecasts(
            friendly_names=[self._device_name], discovery_timeout=DISCOVER_TIMEOUT
        )
        while len(chromecasts) == 0 and t > 0:
            sleep(0.2)
            t -= 0.2

        if len(chromecasts) != 0:
            logger.info(f"Found device: {chromecasts[0].cast_info.friendly_name}")
            self._device = chromecasts[0]
            self._browser = browser
        else:
            logger.warning(f"Device '{self._device_name}' not found within {DISCOVER_TIMEOUT} seconds")

    def _set_temporary_volume(self, volume: float) -> callable:
        device = self._device
        old_volume = device.status.volume_level
        device.set_volume(volume, 5)

        def reset_volume() -> None:
            device.set_volume(old_volume, 5)

        return reset_volume

    def cast_audio(self, audio_source: str, volume: Optional[float] = None) -> None:
        if self._device is None:
            logger.warning("No device available, skipping playback")
            return

        if audio_source.startswith("http"):
            audio_url = audio_source
        else:
            audio_url = self._base_url + audio_source

        logger.info(f"Casting audio from: {audio_url}")
        if volume is not None:
            logger.debug(f"Setting volume to: {volume}")

        device = self._device
        device.wait(5)

        reset = None
        if volume is not None:
            reset = self._set_temporary_volume(volume)

        media_controller = device.media_controller
        media_controller.play_media(audio_url, 'audio/mp3')
        media_controller.block_until_active()

        logger.debug("Waiting for playback to start")
        while media_controller.status.player_state != 'PLAYING':
            sleep(5)
        logger.info("Playback started")

        logger.debug("Waiting for playback to finish")
        while media_controller.status.player_state == 'PLAYING':
            sleep(5)
        logger.info("Playback finished")

        if reset:
            reset()

    def __enter__(self) -> 'MediaCaster':
        from server import AudioServer
        self._audio_server = AudioServer(port=self._port)
        try:
            self._base_url = self._audio_server.start()
            logger.info(f"Audio server started at {self._base_url}")
        except Exception as e:
            logger.error(f"Failed to start audio server: {e}")
            raise RuntimeError(f"Failed to start audio server on port {self._port}: {e}") from e

        self._set_device()
        return self

    def __exit__(self, exc_type, exc_val, exc_tb) -> None:
        if self._audio_server:
            self._audio_server.stop()
            logger.info("Audio server stopped")
        if self._device is not None:
            self._device.disconnect(5)
            self._browser.stop_discovery()