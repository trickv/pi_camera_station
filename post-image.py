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

if len(sys.argv) > 1 and sys.argv[1] == "old":
    print("Debug mode: reading /dev/shm/old image")
    image_file = "/dev/shm/old"
else:
    image_file="/dev/shm/image-{}".format(datetime.datetime.isoformat(datetime.datetime.now()))
    subprocess.run(["raspistill -t 2000 -o {}.png -e png".format(image_file)], shell=True, check=True)
    subprocess.run(["cwebp -q 50 {}.png -o {}.webp".format(image_file,image_file)], shell=True, check=True)
    os.unlink("{}.png".format(image_file))

image = None
with open("{}.webp".format(image_file), "rb") as in_file:
    image = in_file.read()
#sys.exit(11)

url_template = "http://hacks.v9n.us/sim800c/?image={}&id={}&xmethod=chunky"

modem.lte_configure()
modem.lte_connect()
modem.print_status()
modem.write("AT+SHDISC") # disconnect in case a previous connection attempt is still lingering

# configure HTTP session parameters beforehand as these get reused
modem.write_ok("AT+SHCONF=\"URL\",\"{}\"".format(host)) # Set up server URL
modem.write_ok("AT+SHCONF=\"HEADERLEN\",350") # Set HTTP head length

def chunks(lst, n):
    """ Yield successive n-sized chunks from lst.
        https://stackoverflow.com/a/312464 """
    for i in range(0, len(lst), n):
        yield lst[i:i + n]
   
chunk_size = 3500

id = 0
iter = 0
for chunk in chunks(image, chunk_size):
    print("*****†**********†chunk iter {} id {}".format(iter, id))
    url = url_template.format('new' if id == 0 else 'append', id)
    [status, length, response] = modem.lte_http_post(url, chunk)
    if status != 200:
        raise Exception("Status {} is not good, bailing out at response '{}', len={}".format(status, response, length))
    part1 = response[response.find('id='):]
    part2 = part1[:part1.find("\r\n")]
    id = part2.split("=")[1].strip()
    iter += 1

modem.lte_disconnect()
