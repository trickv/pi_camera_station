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

if len(sys.argv) > 1 and sys.argv[1] == "old":
    print("Debug mode: reading /dev/shm/old image")
    image_file = "/dev/shm/old"
else:
    image_file="/dev/shm/image-{}".format(datetime.datetime.isoformat(datetime.datetime.now()))
    subprocess.run(["raspistill -t 2000 -o {}.png -e png".format(image_file)], shell=True, check=True)
    subprocess.run(["cwebp -q 50 {}.png -o {}.webp".format(image_file,image_file)], shell=True, check=True)
    os.unlink("{}.png".format(image_file))

url = "http://hacks.v9n.us/sim800c/?image=new"
touchfile = '/dev/shm/now-image'
pathlib.Path(touchfile).touch()

proc = subprocess.Popen("sudo pppd call image", shell=True)
print("gprs called")
time.sleep(5)
print("now curl")
cmd = "curl --data-binary @{}.webp {}".format(image_file, url)
print("cmd: {}".format(cmd))
subprocess.run([cmd], shell=True)
os.unlink(touchfile)
print("cleam up in ten")
time.sleep(10)
proc.terminate()
print("genie")
