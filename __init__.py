import argparse
from os import getenv
from MediaCaster import MediaCaster

ADHAN = getenv('ADHAN')
FAJR_ADHAN = getenv('FAJR_ADHAN')
DEVICE_NAME = getenv('DEVICE_NAME')

parser = argparse.ArgumentParser(
    description="Casting the adhan to a chromecast device in the home network"
)
parser.add_argument("--fajr", action='store_true', default=False)
args = parser.parse_args()

def prayer_call(fajr_prayer: str = args.fajr):
    with MediaCaster(DEVICE_NAME) as player:
        if fajr_prayer:
            player.cast_audio(FAJR_ADHAN, 0.3)
        else:
            player.cast_audio(ADHAN)
    
if __name__ == '__main__':
    prayer_call()
