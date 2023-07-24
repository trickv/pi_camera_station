#!/usr/bin/env python

import sys
import time
import subprocess
import modem as modem_module

modem = modem_module.modem()
modem.init()

modem.poweron()

modem.lte_configure()
modem.lte_connect()
modem.print_status()
response = modem.lte_send_beacon()
modem.lte_disconnect()

if (response.find("ET_PHONE_HOME") > 0):
    print("ET PHONE HOME RECEIVED!")
    time.sleep(1)
    proc = subprocess.Popen("sudo pppd call gprs", shell=True)
    time.sleep(60)
    subprocess.run("~/station/ci.sh", shell=True)
    # proc.terminate()
else:
    print("Beacon response: {}".format(response))
    modem.poweroff()

