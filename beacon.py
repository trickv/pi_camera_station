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

modem.lte_configure()
modem.lte_connect()
modem.print_status()
response = modem.lte_send_beacon()
modem.lte_disconnect()

if (response.find("ET_PHONE_HOME") > 0):
    print("ET PHONE HOME RECEIVED!")
    time.sleep(1)
    subprocess.run(["sudo pppd call gprs"], shell=True)
else:
    print("Beacon response: {}".format(response))
