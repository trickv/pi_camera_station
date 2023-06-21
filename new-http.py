#!/usr/bin/env python

import serial
import RPi.GPIO as GPIO     
import sys
import time

#GPIO.setwarnings(False)

#GPIO.setmode(GPIO.BCM)
#GPIO.setup(4, GPIO.OUT)

#print("GPIO Function:")
#print(GPIO.gpio_function(4))
#print("GPIO State:")
#print(GPIO.input(4))

import modem as modem_module

modem = modem_module.modem()
modem.init()


modem.print_status()

modem.write_ok("AT+CFUN=1")
modem.write_ok("AT+CPIN?")
modem.write_ok("AT+COPS?")
modem.write_ok("AT+CGREG?")
modem.write_ok("AT+CNMP=38") # set 38 mode lte, or 2 for NB iot
modem.write_ok("AT+CMNB=1") # hologram doc: prefer LTE over NB...
#modem.write_ok("AT+CSTT=\"hologram\"")
modem.write_ok("AT+CPSI?")
#modem.write_ok("AT+CIPSTATUS")
modem.write_ok("AT+CGNAPN")
modem.write_ok("AT+CNACT=0,1") # connect
modem.write_ok("AT+CNACT?")
modem.write_ok("AT+CPSI?")


modem.write_ok("AT+SHCONF=\"URL\",\"http://www.yahoo.com\"") # Set up server URL
modem.write_ok("AT+SHCONF=\"BODYLEN\",1024") # Set HTTP body length

modem.write_ok("AAT+SHCONF="HEADERLEN",350 OK Set HTTP head length

modem.write_ok("AAT+SHCONN OK HTTP build

modem.write_ok("AAT+SHSTATE? +SHSTATE: 1

OK

Get HTTP status

modem.write_ok("AAT+SHCHEAD OK Clear HTTP header

modem.write_ok("AAT+SHAHEAD="Accept","text/html, */*" OK Add header content

modem.write_ok("AAT+SHAHEAD="User-Agent","IOE Client" OK Add header content

modem.write_ok("AAT+SHAHEAD="Content-Type","application

/x-www-form-urlencoded"

OK Add header content

modem.write_ok("AAT+SHAHEAD="Connection","keep-alive" OK Add header content

modem.write_ok("AAT+SHAHEAD="Cache-control","no-cache" OK Add header content

modem.write_ok("AAT+SHREQ="http://www.yahoo.com/",1 OK

+SHREQ: "GET",301,8

Set request type is GET. 

Get data size is 8. 

modem.write_ok("AAT+SHREAD=0,8 OK

+SHREAD: 8

redirect

Read data length is 8 

Data is “redirect” 

modem.write_ok("AAT+SHDISC OK Disconnect HTT


modem.write_ok("AT+CNACT=0,0") # disconnect
modem.write_ok("AT+CPSI?")


