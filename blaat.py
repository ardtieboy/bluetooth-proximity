#!/usr/bin/python

import bluetooth
import time

print("In/Out Board")

while True:
    print("Checking " + time.strftime("%a, %d %b %Y %H:%M:%S", time.gmtime()))

    result = bluetooth.lookup_name('F8:2D:7C:EF:40:17', timeout=5)
    if (result != None):
        print("John: in")
    else:
        print("John: out")

    time.sleep(10)