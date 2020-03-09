#!/usr/bin/env python
from bt_rssi import BluetoothRSSI
import datetime
import time
import threading
import sys
import math
import RPi.GPIO as GPIO


class Device:
    def __init__(self, name, pin):
        self.name = name
        self.pin = pin


# List of bluetooth addresses to scan
BT_ADDR_DICT = {
    "E4:50:EB:00:EF:DF": Device("Ard Watch", 15),
    "F8:2D:7C:EF:40:17": Device("Ard IPhone", 14)}
DAILY = False  # Set to True to invoke callback only once per day per address
DEBUG = True  # Set to True to print out debug messages
THRESHOLD = (-10, 10)
SLEEP = 1


def dummy_callback(addr, rssi):
    print(f"Dummy callback function invoked: {BT_ADDR_DICT[addr].name}")
    # Log Normal Shadowing Model considering d0 =1m where
    A0 = 0
    n = 1.5
    c = 0
    x = float((rssi-A0)/(-10*n))
    distance = (math.pow(10, x) * 100) + c
    print(distance)
    GPIO.output(BT_ADDR_DICT[addr], GPIO.HIGH)
    print(f"led {BT_ADDR_DICT[addr].name} is on")


def bluetooth_listen(addr, threshold, callback, sleep=1, daily=True, debug=False):
    """Scans for RSSI value of bluetooth address in a loop. When the value is
    within the threshold, calls the callback function.

    @param: addr: Bluetooth address
    @type: addr: str

    @param: threshold: Tuple of integer values (low, high), e.g. (-10, 10)
    @type: threshold: tuple

    @param: callback: Callback function to invoke when RSSI value is within
                      the threshold
    @type: callback: function

    @param: sleep: Number of seconds to wait between measuring RSSI
    @type: sleep: int

    @param: daily: Set to True to invoke callback only once per day
    @type: daily: bool

    @param: debug: Set to True to print out debug messages and does not
                   actually sleep until tomorrow if `daily` is True.
    @type: debug: bool
    """
    init_pins(addr)
    b = BluetoothRSSI(addr=addr)
    while True:
        rssi = b.get_rssi()
        if debug:
            print("---")
            print(f"addr: {addr}, rssi: {rssi}")
        # Sleep and then skip to next iteration if device not found
        if rssi is None:
            time.sleep(sleep)
            GPIO.output(BT_ADDR_DICT[addr].pin, GPIO.LOW)
            continue
        # Trigger if RSSI value is within threshold
        if threshold[0] < rssi < threshold[1]:
            callback(addr, rssi)
        else:
            print('Resetting the led')
            GPIO.output(BT_ADDR_DICT[addr].pin, GPIO.LOW)
        # Delay between iterations
        time.sleep(sleep)


def init_pins(addr):
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(BT_ADDR_DICT[addr].pin, GPIO.OUT)
    GPIO.output(BT_ADDR_DICT[addr].pin, GPIO.HIGH)


def start_thread(addr, callback, threshold=THRESHOLD, sleep=SLEEP,
                 daily=DAILY, debug=DEBUG):
    """Helper function that creates and starts a thread to listen for the
    bluetooth address.

    @param: addr: Bluetooth address
    @type: addr: str

    @param: callback: Function to call when RSSI is within threshold
    @param: callback: function

    @param: threshold: Tuple of the high/low RSSI value to trigger callback
    @type: threshold: tuple of int

    @param: sleep: Time in seconds between RSSI scans
    @type: sleep: int or float

    @param: daily: Daily flag to pass to `bluetooth_listen` function
    @type: daily: bool

    @param: debug: Debug flag to pass to `bluetooth_listen` function
    @type: debug: bool

    @return: Python thread object
    @rtype: threading.Thread
    """
    thread = threading.Thread(
        target=bluetooth_listen,
        args=(),
        kwargs={
            'addr': addr,
            'threshold': threshold,
            'callback': callback,
            'sleep': sleep,
            'daily': daily,
            'debug': debug
        }
    )
    # Daemonize
    thread.daemon = True
    # Start the thread
    thread.start()
    return thread


def main():
    threads = []
    for addr in BT_ADDR_DICT.keys():
        th = start_thread(addr=addr, callback=dummy_callback)
        threads.append(th)
    while True:
        # Keep main thread alive
        time.sleep(1)


if __name__ == '__main__':
    main()
