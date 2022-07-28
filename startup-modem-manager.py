#!/usr/bin/env python

import RPi.GPIO as GPIO     
import sys
import time
import subprocess
import datetime

start_time = datetime.datetime.now()

GPIO.setmode(GPIO.BCM)
GPIO.setup(4, GPIO.OUT) # modem power signal pin
GPIO.setup(26, GPIO.IN) # lipo shim low battery signal

time.sleep(120) # sleep a bit every startup

while True:
    if GPIO.input(26) != GPIO.LOW:
        print("flux capacitor enabled")
        break
    print("waiting for full power...")
    time.sleep(10)

# turn on modem power relay
GPIO.setup(16, GPIO.OUT) #  relay, this seems to activate it without even needing to pull up, weird
time.sleep(10) # Give the modem 10 seconds to start up
GPIO.output(4, GPIO.HIGH) # Tell the modem to turn on via it's power signal pin

subprocess.run("/home/trick/station/powerstatus.py", shell=True)
subprocess.run("/home/trick/station/powerstatus.py", shell=True)

subprocess.run("/home/trick/station/beacon.py", shell=True)
time.sleep(30)
subprocess.run("/home/trick/station/post-image.py", shell=True)
