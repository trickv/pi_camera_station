#!/usr/bin/env python

import sys
import time
import subprocess
import urllib.parse
import modem as modem_module

modem = modem_module.modem()
modem.init()
modem.poweron()

signal = modem.write_ok('AT+CSQ')
cpsi = modem.write_ok("AT+CPSI?")
apn = modem.write_ok("AT+COPS?")
#cops_query = modem.write_ok("AT+COPS=?")
cops_query = "x"

body = "cops_query={}&signal={}&cpsi={}&apn={}".format(urllib.parse.quote(cops_query), urllib.parse.quote(signal), urllib.parse.quote(cpsi), urllib.parse.quote(apn))

url = "http://hacks.v9n.us/sim800c/diag/"

modem.lte_configure()
modem.lte_connect()
modem.print_status()
modem.lte_http_post(url, body)
modem.lte_disconnect()
modem.poweroff()

