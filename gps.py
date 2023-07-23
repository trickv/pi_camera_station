#!/usr/bin/env -S python -u

import RPi.GPIO as GPIO     
import sys
import time
import subprocess
import datetime
import modem as modem_module

cleanup = True
if len(sys.argv) >= 2 and sys.argc == "test":
    print("debug mode: not cleaning up! dont use in prod!")
    cleanup = False
    time.sleep(10)

GPIO.setwarnings(False)

GPIO.setmode(GPIO.BCM)
GPIO.setup(4, GPIO.OUT) # modem soft power signal pin


# TODO make sure run inside tmux...look for TMUX env var

# turn off, wait, turn on relay
GPIO.setup(16, GPIO.IN) # relay
time.sleep(1)
GPIO.setup(16, GPIO.OUT)
time.sleep(1)
# press power button soft
GPIO.output(4, GPIO.HIGH)
time.sleep(1)
GPIO.output(4, GPIO.LOW)
time.sleep(1)



# turn on gps power
modem = modem_module.modem()
modem.init()
for i in range(0, 5):
    print("AT:")
    modem.write_noblock("AT")
    print(modem.read())
    time.sleep(1)
modem.write_ok("AT")
modem.write_ok("AT+CGNSPWR=1")

# poll for signal, once found, poll for 5m
for i in range(0, 720):
    print("time: {}".format(i*10))
    modem.write("AT+CGNSINF")
    time.sleep(10)

# write to disk
# power cycle, run startup...py
if not cleanup:
    sys.exit(0)
GPIO.setup(16, GPIO.IN) # relay
time.sleep(1)
subprocess.run("~/station/startup-modem-manager.py", shell=True)
