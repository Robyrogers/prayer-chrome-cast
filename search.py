# """
# Search for available chromecasts.
# """

import pychromecast
import zeroconf
from time import sleep


class DeviceListener:
    def add_cast(self, uuid, service):
        pass

    def remove_cast(self, uuid, service):
        pass

    def update_cast(self, uuid, service):
        pass


zconf = zeroconf.Zeroconf()
browser = pychromecast.CastBrowser(DeviceListener(), zconf)

print("Searching for Chromecast devices...")
browser.start_discovery()

sleep(5)

for device in browser.devices.values():
    print(device.friendly_name)

browser.stop_discovery()