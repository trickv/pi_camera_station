#!/usr/bin/env python

import RPi.GPIO as GPIO     
import subprocess
import sys
import os
import time
import datetime
import modem as modem_module

modem = modem_module.modem()
modem.init()

image_file="/dev/shm/image-{}".format(datetime.datetime.isoformat(datetime.datetime.now()))

subprocess.run(["raspistill -t 2000 -o {}.png -e png".format(image_file)], shell=True, check=True)
subprocess.run(["cwebp -q 50 {}.png -o {}.webp".format(image_file,image_file)], shell=True, check=True)
image = None
with open("{}.webp".format(image_file), "rb") as in_file:
    image = in_file.read()
os.unlink("{}.png".format(image_file))
#sys.exit(11)

while True:
    modem.write_noblock('AT')
    rcv = modem.port.read(100)
    if len(rcv) > 0:
        print(rcv)
        break
    print(".", end='', flush=True)
    time.sleep(1)


modem.lte_configure()
modem.lte_connect()
modem.print_status()

url = "http://hacks.v9n.us/sim800c/?image=1"
host = "http://hacks.v9n.us"
modem.lte_http_post(host, url, image)
modem.lte_disconnect()
