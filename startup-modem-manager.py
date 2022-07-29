#!/usr/bin/env python

import RPi.GPIO as GPIO     
import sys
import time
import subprocess
import datetime
import modem as modem_module

GPIO.setwarnings(False)

GPIO.setmode(GPIO.BCM)
GPIO.setup(4, GPIO.OUT) # modem power signal pin
GPIO.setup(26, GPIO.IN) # lipo shim low battery signal

print("GPIO pins initialized; sleeping a bit before doing anything to give the battery a bit to charge")

time.sleep(15) # sleep a bit every startup

print("Sleep done; now waiting for the lipo shim to report that we have enough battery")

iterations = 0

while True:
    iterations += 1
    if iterations > 30:
        print("300s elapsed, close enough, let's rock!")
        break
    if GPIO.input(26) != GPIO.LOW:
        print("flux capacitor enabled")
        break
    print("waiting for full power...")
    time.sleep(10)

# turn on modem power relay
GPIO.setup(16, GPIO.OUT) #  relay, this seems to activate it without even needing to pull up, weird
time.sleep(10) # Give the modem 10 seconds to start up
GPIO.output(4, GPIO.HIGH) # Tell the modem to turn on via it's power signal pin
time.sleep(45) # time for the modem to get a signal ++

def run(command):
    #subprocess.run(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    subprocess.run(command, shell=True)

run("/home/trick/station/powerstatus.py")
run("/home/trick/station/powerstatus.py")

modem = modem_module.modem()
modem.init()
modem.connect_gprs()
modem.send_beacon()
output = modem.get_gsm_time()
print("Output:")
print(output)
print("repr:")
print(repr(output))
for_timedatectl_time = (" ".join(output.split("\r\n")[1].split(",")[1:3])).replace("/","-")
print("Setting system clock via timedatectl to {}".format(for_timedatectl_time))
run("sudo timedatectl set-time \"{}\"".format(for_timedatectl_time))
modem.cleanup()
sys.exit(1) # HACK
# to then do something with the time:
# first disable ntp: sudo timedatectl set-ntp false
# perhaps only do any of this when sudo timedatectl | grep "System clock synchronized" is "no"
# sudo date -s '2022/07/21 03:51:34' # just sub out the comma!
# Or maybe try using sudo timedatectl set-time xxx; maybe this'll work when in offline mode

run("/home/trick/station/beacon.py")
time.sleep(30)
run("/home/trick/station/post-image.py")
