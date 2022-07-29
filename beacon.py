#!/usr/bin/env python

import sys
import time
import subprocess
import modem as modem_module

modem = modem_module.modem()
modem.init()

while True:
    modem.write_noblock('AT')
    rcv = modem.port.read(100)
    if len(rcv) > 0:
        print(rcv)
        break
    print(".", end='', flush=True)
    time.sleep(1)

# MEH: # reset the modem in case it was left in an unclean state
#write_ok('AT+CIPSHUT')
#write_ok('AT+SAPBR=0,1') # Close GPRS context # not idempotent...
#write_ok('AT+HTTPTERM') # Close HTTP handler in case it was left open # not idempotent...

#if power_cycle:
#    print("Module online, giving 15 more seconds to connect:")
#    time.sleep(15)
#    rcv = port.read(100)
#    print(rcv)

# check status

modem.print_status()
modem.connect_gprs()
response = modem.send_beacon()
modem.cleanup()

if (response.find("ET_PHONE_HOME") > 0):
    print("ET PHONE HOME RECEIVED!")
    time.sleep(1) # probably should be longer in prod?
    subprocess.run(["sudo pppd call gprs"], shell=True)
