#!/usr/bin/env python

import RPi.GPIO as GPIO
import datetime
import subprocess
import time


# The BCM-numbered GPIO pin with the attached switch circuit:
pin = 24 # The one right next to 3.3v for easy attachment

wifi_up = None

def rfkill(mode):
    print("rfkill state change: {}".format(mode))
    subprocess.run("sudo rfkill {} all".format(mode), shell=True)

def my_callback(channel):
    global wifi_up
    if GPIO.input(channel) == GPIO.HIGH:
        #print("Down Arrow at " + str(datetime.datetime.now()))
        if wifi_up:
            rfkill("unblock")
            wifi_up = False
    else:
        #print("Up Arrow at " + str(datetime.datetime.now()))
        if not wifi_up:
            rfkill("block")
            wifi_up = True

try:
    rfkill("block")
    time.sleep(10)
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(pin, GPIO.IN, pull_up_down=GPIO.PUD_DOWN)
    wifi_up = GPIO.input(pin) == GPIO.HIGH
    print("Initial: WiFi should be up? " + str(wifi_up))
    if wifi_up:
        rfkill("unblock")
    else:
        rfkill("block")


    GPIO.add_event_detect(pin, GPIO.BOTH, callback=my_callback)
    message = input("Press any key to exit.")

finally:
    GPIO.cleanup()

print("Bye")

