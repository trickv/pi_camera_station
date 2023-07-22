#!/usr/bin/env -S python -u

import RPi.GPIO as GPIO     
import sys
import time
import subprocess
import datetime
import modem as modem_module

GPIO.setwarnings(False)

GPIO.setmode(GPIO.BCM)
GPIO.setup(4, GPIO.OUT) # modem soft power signal pin




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
modem.write_ok("AT+CGNSPWR")

# poll for signal, once found, poll for 5m
for i in range(0, 120):
    print(modem.write("AT+CGNSINF"))
    time.sleep(10)

# write to disk
# power cycle, run startup...py
if sys.argc >= 2 and sys.argc == "test":
    sys.exit(0)
GPIO.setup(16, GPIO.IN) # relay
time.sleep(1)
subprocess.run("~/station/startup-modem-manager.py", shell=True)
