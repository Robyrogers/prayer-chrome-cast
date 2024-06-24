# """
# Search for available chromecasts.
# """

from time import sleep
import pychromecast
import zeroconf

zconf = zeroconf.Zeroconf()

browser = pychromecast.CastBrowser(
    pychromecast.SimpleCastListener(lambda uuid, service: print(browser.devices[uuid].friendly_name)), 
    zconf
)

browser.start_discovery()

sleep(5)

browser.stop_discovery()