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
modem.write_ok("AT+SHCONF=\"HEADERLEN\",350") # Set HTTP head length
modem.write_ok("AT+SHCONN") # HTTP build
modem.write_ok("AT+SHSTATE?") # Get HTTP status
modem.write_ok("AT+SHCHEAD") # Clear HTTP header
modem.write_ok("AT+SHAHEAD=\"Accept\",\"text/html, */*\"") # Add header content
modem.write_ok("AT+SHAHEAD=\"User-Agent\",\"IOE Client\"") #  OK Add header content
modem.write_ok("AT+SHAHEAD=\"Content-Type\",\"application/x-www-form-urlencoded\"") # Add header content
modem.write_ok("AT+SHAHEAD=\"Connection\",\"keep-alive\"") # Add header content
modem.write_ok("AT+SHAHEAD=\"Cache-control\",\"no-cache\"") # Add header content
modem.write_ok("AT+SHREQ=\"http://www.yahoo.com/\",1") # Set request type is GET. 
# out:
#Get data size is 8. 
# i think this is where we get 8 for the next cmd?

modem.write_ok("AT+SHREAD=0,8") # read
modem.write_ok("AT+SHDISC") # Disconnect HTT


modem.write_ok("AT+CNACT=0,0") # disconnect
modem.write_ok("AT+CPSI?")


