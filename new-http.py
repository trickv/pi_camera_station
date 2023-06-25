#!/usr/bin/env python

import serial
import RPi.GPIO as GPIO     
import sys
import time

#GPIO.setwarnings(False)

#GPIO.setmode(GPIO.BCM)
#GPIO.setup(4, GPIO.OUT)

#print("GPIO Function:")
#print(GPIO.gpio_function(4))
#print("GPIO State:")
#print(GPIO.input(4))

import modem as modem_module

modem = modem_module.modem()
modem.init()

#modem.lte_connect()
modem.print_status()

try:
    response = modem.lte_send_beacon()
    print("Response: {}".format(response))
except:
    print("oops, cleaning up...")
    modem.write_ok("AT+SHDISC")
    #modem.disconnect_lte()

#modem.disconnect_lte()
