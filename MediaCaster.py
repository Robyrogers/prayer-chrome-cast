import pychromecast
from time import sleep

class MediaCaster:
    def __init__(self, device_name: str):
        self.__device_name = device_name
        self.__browser: pychromecast.CastBrowser = None
        self.__device: pychromecast.Chromecast

    def __set_device(self):
        chromecasts, browser = pychromecast.get_listed_chromecasts(friendly_names=[self.__device_name], discovery_timeout=5)

        print(f"Found Device: {chromecasts[0].cast_info.friendly_name}")

        self.__device = chromecasts[0]
        self.__browser = browser

    def __set_temporary_volume(self, volume: float):
        device = self.__device
        old_volume = device.status.volume_level
        device.set_volume(volume, 5)

        def reset_volume():
            device.set_volume(old_volume, 5)
            return None
        
        return reset_volume

    def cast_audio(self, audio_url: str, volume: float = 0):
        device = self.__device
        device.wait(5)

        if volume > 0:
            reset = self.__set_temporary_volume(volume)

        media_controller = device.media_controller
        media_controller.play_media(audio_url, 'audio/mp3')
        media_controller.block_until_active()

        while(media_controller.status.player_state != 'PLAYING'):
            sleep(5)
        while(media_controller.status.player_state == 'PLAYING'):
            sleep(5)
        
        if volume > 0:
            reset()

    def __enter__(self):
        self.__set_device()
        return self
    
    def __exit__(self, type, value, traceback):
        self.__device.disconnect(5)
        self.__browser.stop_discovery()