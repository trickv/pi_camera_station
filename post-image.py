#!/usr/bin/env python

import RPi.GPIO as GPIO     
import subprocess
import sys
import time
import datetime
import modem as modem_module

modem = modem_module.modem()
modem.init()

image_file="/dev/shm/image-{}".format(datetime.datetime.isoformat(datetime.datetime.now()))

subprocess.run(["raspistill -t 2000 -o {}.png -e png".format(image_file)], shell=True, check=True)
subprocess.run(["cwebp -q 60 {}.png -o {}.webp".format(image_file,image_file)], shell=True, check=True)
image = None
with open("{}.webp".format(image_file), "rb") as in_file:
    image = in_file.read()
#sys.exit(11)

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


# check status
print("Network signal quality query, returns a signal value:")
modem.write_ok('AT+CSQ')
#print("Firmware version:")
#write_ok('AT+CGMR')
print("Network registration status:")
modem.write_ok("AT+CREG?")
print("GPRS attachment status:")
modem.write_ok("AT+CGATT?")



# Connect to GPRS:
modem.write_ok('AT+CSTT="hologram"')
modem.write_ok('AT+CIICR')
modem.write_ok('AT+SAPBR=3,1,"Contype","GPRS"')
modem.write_ok('AT+SAPBR=3,1,"APN","hologram"')
modem.write_ok('AT+SAPBR=1,1') # open GPRS context
modem.write_ok('AT+SAPBR=2,1') # Query GPRS context


# Now run the HTTP command:
modem.write_ok('AT+HTTPINIT')
modem.write_ok('AT+HTTPPARA="CID",1')
modem.write_ok('AT+HTTPPARA="URL","http://hacks.v9n.us/sim800c/?image=1"')
data_length = len(image)
modem.write_expect("AT+HTTPDATA={},120000".format(data_length), "DOWNLOAD")
modem.port.write(image)
modem.read_ok()
modem.write_ok('AT+HTTPACTION=1')
#time.sleep(1)
modem.cleanup()
