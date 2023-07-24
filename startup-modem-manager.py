#!/usr/bin/env -S python -u

import RPi.GPIO as GPIO     
import sys
import time
import subprocess
import datetime
import modem as modem_module

GPIO.setwarnings(False)

GPIO.setmode(GPIO.BCM)
GPIO.setup(26, GPIO.IN) # lipo shim low battery signal

def get_uptime():
    with open('/proc/uptime', 'r') as f:
        uptime_seconds = float(f.readline().split()[0])

    return uptime_seconds

print("GPIO pins initialized")

print("Uptime: %d" % get_uptime())
if get_uptime() < 60:
    print("sleeping a bit before doing anything to give the battery a bit to charge")
    time.sleep(15) # sleep a bit every startup
    print("Sleep done; now waiting for the lipo shim to report that we have enough battery")

iterations = 0
max_iterations = 90

while True:
    iterations += 1
    if iterations > max_iterations:
        print("900s elapsed, close enough, let's rock!")
        break
    if GPIO.input(26) != GPIO.LOW:
        print("flux capacitor enabled")
        break
    print("waiting for full power... {}/{}".format(iterations, max_iterations))
    time.sleep(10)

print("turning modem on...")
# turn on modem power relay
GPIO.setup(16, GPIO.OUT) #  relay, this seems to activate it without even needing to pull up, weird
time.sleep(1) # Give the modem some seconds to start up
modem = modem_module.modem()
modem.init()
modem.poweron()
#time.sleep(45) # time for the modem to get a signal ++

def run(command):
    #subprocess.run(command, shell=True, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
    subprocess.run(command, shell=True)

#run("/home/trick/station/powerstatus.py")
run("/home/trick/station/powerstatus.py")

modem.lte_configure()
modem.lte_connect()
modem.print_status()
response = modem.lte_send_beacon()
modem.lte_disconnect()

if (response.find("ET_PHONE_HOME") > 0):
    print("ET PHONE HOME RECEIVED!")
    time.sleep(1)
    proc = subprocess.Popen("sudo pppd call gprs", shell=True)
    time.sleep(60)
    subprocess.run("~/station/ci.sh", shell=True)
    # proc.terminate()
else:
    print("Beacon response: {}".format(response))
    modem.poweroff()

