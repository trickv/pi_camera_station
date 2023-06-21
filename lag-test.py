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


# Enable Serial Communication
port = serial.Serial("/dev/ttyS0", baudrate=115200, timeout=1)
#received = port.read(1000)
#print(received.decode('latin1'))
#print("\n")

while True:
    print("Sending AT:")
    port.write("AT\r\n".encode('latin1'))
    time.sleep(1)
    print(port.read(1000))
