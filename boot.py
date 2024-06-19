# ...module boot.py
# Create connection to trusted AP
from network import WLAN, STA_IF
import gc
from time import sleep_ms, sleep

from config import CONFIG
import config


def try_connection():
    t = 12
    while not wlan.isconnected() and t > 0:
        print('.', end='')
        sleep_ms(500)
        t = t - 1
    return wlan.isconnected()

def wlan_connect():
    wlan = WLAN(STA_IF)
    if not wlan.isconnected():
        wlan.active(True)
        wlan.config(txpower=8.5) # necessary for WEMOS C3 Mini
        sleep(2)
        wlan.connect(config.SSID, config.PASSWORD)
        while not wlan.isconnected():
            pass
    print('network config:', wlan.ifconfig())
    return wlan

wlan = wlan_connect()

gc.collect()
