import os
import pychromecast
import time

DEVICE_NAME = os.getenv('DEVICE_NAME')

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

    def cast_audio(self, audio_url: str):
        device = self.__device
        
        device.wait()
        
        media_controller = device.media_controller
        media_controller.play_media(audio_url, 'audio/mp3')
        time.sleep(5)

    def __enter__(self):
        self.__set_device()
        return self
    
    def __exit__(self, type, value, traceback):
        self.__device.disconnect(5)
        self.__browser.stop_discovery()

# with MediaCaster(DEVICE_NAME) as cast:
#     cast.cast_audio('https://media.sd.ma/assabile/adhan_3435370/0bf83c80b583.mp3')