#!/usr/bin/env python

import serial
import RPi.GPIO as GPIO     
import subprocess
import sys
import time
import datetime

image_file="/dev/shm/image-{}".format(datetime.datetime.isoformat(datetime.datetime.now()))

subprocess.run(["raspistill -t 2000 -o {}.png -e png".format(image_file)], shell=True, check=True)
subprocess.run(["cwebp -q 80 {}.png -o {}.webp".format(image_file,image_file)], shell=True, check=True)
image = None
with open("{}.webp".format(image_file), "rb") as in_file:
    image = in_file.read()
#sys.exit(11)

power_cycle = True

if power_cycle:
    GPIO.setmode(GPIO.BCM)
    GPIO.setup(4, GPIO.OUT)
    GPIO.output(4, GPIO.LOW) # Turn modem off
    time.sleep(3) # wait a sec for it to turn off

    # Now turn it on (pulse high, wait for it, then sustain high)
    GPIO.output(4, GPIO.HIGH)
    time.sleep(0.5)
    GPIO.output(4, GPIO.LOW)
    time.sleep(1)
    GPIO.output(4, GPIO.HIGH)
    time.sleep(3)

# Enable Serial Communication
port = serial.Serial("/dev/ttyS0", baudrate=115200, timeout=1)
#received = port.read(1000)
#print(received.decode('latin1'))
#print("\n")

# Transmitting AT Commands to the Modem
# '\r\n' indicates the Enter key

def write(command):
    command = command + "\r\n"
    command = command.encode('latin1')
    port.write(command)

def read_ok():
    read_expect("OK")

def read_expect(message):
    while True:
        received = port.read(1000)
        if len(received) > 0:
            break
        else:
            print("waiting...")
    if received.decode('latin1').find(message) < 0:
        print(received)
        sys.exit(1)
    else:
        print(received)

def write_expect(command, message):
    write(command)
    read_expect(message)

def write_ok(command):
    write(command)
    read_ok()


while True:
    write('AT')
    rcv = port.read(100)
    print(rcv)
    if len(rcv) > 0:
        break
    print(".")
    time.sleep(1)

# MEH: # reset the modem in case it was left in an unclean state
#write_ok('AT+CIPSHUT')
#write_ok('AT+SAPBR=0,1') # Close GPRS context # not idempotent...
#write_ok('AT+HTTPTERM') # Close HTTP handler in case it was left open # not idempotent...

print("Module online, giving 15 more seconds to connect:")
time.sleep(15)

# check status
print("Network signal quality query, returns a signal value:")
write_ok('AT+CSQ')
#print("Firmware version:")
#write_ok('AT+CGMR')
print("Network registration status:")
write_ok("AT+CREG?")
print("GPRS attachment status:")
write_ok("AT+CGATT?")



# Connect to GPRS:
write_ok('AT+CSTT="hologram"')
write_ok('AT+CIICR')
write_ok('AT+SAPBR=3,1,"Contype","GPRS"')
write_ok('AT+SAPBR=3,1,"APN","hologram"')
write_ok('AT+SAPBR=1,1') # open GPRS context
write_ok('AT+SAPBR=2,1') # Query GPRS context


# Now run the HTTP command:
write_ok('AT+HTTPINIT')
write_ok('AT+HTTPPARA="CID",1')
write_ok('AT+HTTPPARA="URL","http://hacks.v9n.us/sim800c/?image=1"')
data_length = len(image)
write_expect("AT+HTTPDATA={},120000".format(data_length), "DOWNLOAD")
port.write(image)
read_ok()
write_ok('AT+HTTPACTION=1')
write_ok('AT+HTTPTERM')
# for now, just shut the module down now:
write_ok('AT+CPOWD=1')
#write_ok('AT+SAPBR=0,1') # Close GPRS context

# Now turn the modem off:

#GPIO.output(4, GPIO.LOW) # Turn modem off
