#!/usr/bin/env python

import RPi.GPIO as GPIO     
import subprocess
import sys
import os
import time
import datetime
import modem as modem_module
import pathlib

modem = modem_module.modem()
modem.init()

modem.poweron()
modem.lte_configure()

if len(sys.argv) > 1 and sys.argv[1] == "old":
    print("Debug mode: reading /dev/shm/old image")
    image_file = "/dev/shm/old"
else:
    image_file="/dev/shm/image-{}".format(datetime.datetime.isoformat(datetime.datetime.now()))
    subprocess.run(["raspistill -vf -hf -t 2000 -o {}.png -e png".format(image_file)], shell=True, check=True)
    subprocess.run(["cwebp -q 50 {}.png -o {}.webp".format(image_file,image_file)], shell=True, check=True)
    os.unlink("{}.png".format(image_file))

url = "http://hacks.v9n.us/sim800c/?image=new&xmethod=ppp"
touchfile = '/dev/shm/now-image'
pathlib.Path(touchfile).touch()

proc = subprocess.Popen("sudo pppd call image", shell=True)
print("gprs called")
time.sleep(30) # race...5s is enough
print("now curl")
cmd = "curl --data-binary @{}.webp '{}'".format(image_file, url)
print("cmd: {}".format(cmd))
subprocess.run([cmd], shell=True)
print("sleeping before clean up")
time.sleep(30)
print("Cleaning up now")
proc.terminate()
subprocess.run(["sudo killall pppd"], shell=True)
print("Sleeping 120 to wait for pppd to clean up")
time.sleep(120)
os.unlink(touchfile)
print("genie")

modem.poweroff()
