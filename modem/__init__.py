import sys
import time
import serial
import RPi.GPIO as GPIO

class modem:

    def init(self):
        self.port = serial.Serial("/dev/ttyS0", baudrate=115200, timeout=1)

    def poweroff(self):
        self.write('AT+CIPSTATUS')
        self.write('AT+HTTPTERM')
        self.write('AT+SAPBR=0,1')
        self.write('AT+CIPSHUT')
        self.write('AT+CIPSTATUS')
        sys.exit(2)
        self.write('AT+CPOWD=1')
        time.sleep(5)
        print(self.port.read(1000))
        GPIO.output(4, GPIO.LOW) # Turn modem power switch off
        sys.exit(1)

    def write_noblock(self, command):
        command = command + "\r\n"
        command = command.encode('latin1')
        self.port.write(command)

    def write(self, command):
        command = command + "\r\n"
        command = command.encode('latin1')
        self.port.write(command)
        received = b''
        while True:
            received += self.port.read(1000)
            if len(received) > 0:
                break
            print(".", end="", flush=True)
            time.sleep(0.1)
        print(received)
        return(received.decode('latin1'))

    def read_ok(self):
        return self.read_expect("OK")

    def read_expect(self, expect_message):
        received = b''
        timeout_cycles = 30
        counter = 0
        while True:
            received += self.port.read_until(size=1000)
            if len(received) > 0:
                if received.decode('latin1').find("ERROR") >= 0:
                    print(received)
                    #self.poweroff()
                    print("I found an ERROR, oops! Exiting.")
                    sys.exit(1)

                if received.decode('latin1').find(expect_message) >= 0:
                    print(received)
                    return received.decode('latin1')
            print(".", end="", flush=True)
            counter += 1
            if counter > timeout_cycles:
                raise Exception("modem: read timeout waiting for expected message")
            time.sleep(0.1)

    def write_ok(self, command):
        self.write_noblock(command)
        return self.read_ok()

    def write_expect(self, command, expect):
        self.write_noblock(command)
        self.read_expect(expect)

    def power_on(self, ):
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(4, GPIO.OUT)
        GPIO.output(4, GPIO.HIGH)
        time.sleep(0.5)
        GPIO.output(4, GPIO.LOW)
        time.sleep(1)
    
    def cleanup(self):
        self.write("AT+HTTPTERM")
        self.write('AT+SAPBR=0,1') # Close GPRS context
        self.write("AT+CIPSHUT") # Close PDP thing
        self.write("AT+HTTPTERM")

    def get_gsm_time(self):
        output = self.write_ok("AT+CIPGSMLOC=2,1")
        print(output)
        return(output)
        # b'AT+CIPGSMLOC=2,1\r\r\n+CIPGSMLOC: 0,2022/07/28,15:59:20\r\n\r\nOK\r\n'
        # AT+CIPGSMLOC=2,1
        # +CIPGSMLOC: 0,2022/07/28,15:59:20

    def lte_disconnect(self):
        # Don't confirm anything in case it errors, which is probably fine
        self.write("AT+SHDISC") # Disconnect HTTP just in case it's still open
        self.write("AT+CNACT=0,0") # disconnect LTE

    def connect_gprs(self):
        self.write_ok('AT+CSTT="hologram"')
        self.write_ok('AT+CIICR')
        self.write_ok('AT+SAPBR=3,1,"Contype","GPRS"')
        self.write_ok('AT+SAPBR=3,1,"APN","hologram"')
        self.write_ok('AT+SAPBR=1,1') # open GPRS context
        self.write_ok('AT+SAPBR=2,1') # Query GPRS context

    def lte_configure(self):
        # This only needs to be run once per boot
        self.write_ok("AT+CFUN=1")
        self.write_ok("AT+CNMP=38") # set 38 mode lte, or 2 for NB iot
        self.write_ok("AT+CMNB=1") # hologram doc: prefer LTE over NB...

    def lte_connect(self):
        #self.write_ok("AT+CGNAPN")
        self.write("AT+CNACT=0,0") # disconnect
        self.write_ok("AT+CNACT=0,1") # connect

    def lte_send_beacon(self):
        self.write("AT+SHDISC") # Disconnect HTT
        url = "http://hacks.v9n.us/sim800c/"
        host = "http://hacks.v9n.us"
        self.write_ok("AT+SHCONF=\"URL\",\"{}\"".format(host)) # Set up server URL
        self.write_ok("AT+SHCONF=\"BODYLEN\",1024") # Set HTTP body length
        self.write_ok("AT+SHCONF=\"HEADERLEN\",350") # Set HTTP head length
        self.write_ok("AT+SHCONN") # HTTP build
        self.write_ok("AT+SHSTATE?") # Get HTTP status
        self.write_ok("AT+SHCHEAD") # Clear HTTP header
        self.write_ok("AT+SHAHEAD=\"Accept\",\"text/html, */*\"") # Add header content
        self.write_ok("AT+SHAHEAD=\"User-Agent\",\"Chicken Wings\"") #  OK Add header content
        self.write_ok("AT+SHAHEAD=\"Content-Type\",\"application/x-www-form-urlencoded\"") # Add header content
        self.write_ok("AT+SHAHEAD=\"Connection\",\"keep-alive\"") # Add header content
        self.write_ok("AT+SHAHEAD=\"Cache-control\",\"no-cache\"") # Add header content
        self.write_ok("AT+SHSTATE?") # Get HTTP status
        self.write_ok("AT+SHREQ=\"{}\",1".format(url)) # Set request type is GET. This is where the request is executed.
        # out:
        #Get data size is 8. 
        # i think this is where we get 8 for the next cmd?
        #self.write_ok("AT+SHSTATE?") # Get HTTP status
        time.sleep(2) # I think the request takes a bit to actually run; this is a race condition...
        response = self.write("AT+SHREAD=0,15") # read
        # TO DO: check for missing OK
        self.write_ok("AT+SHDISC") # Disconnect HTT
        return(response)
    
    def lte_http_post(self):
        self.write("AT+SHDISC") # Disconnect HTT
        url = "http://hacks.v9n.us/sim800c/"
        host = "http://hacks.v9n.us"
        self.write_ok("AT+SHCONF=\"URL\",\"{}\"".format(host)) # Set up server URL
        self.write_ok("AT+SHCONF=\"BODYLEN\",1024") # Set HTTP body length
        self.write_ok("AT+SHCONF=\"HEADERLEN\",350") # Set HTTP head length
        self.write_ok("AT+SHCONN") # HTTP build
        self.write_ok("AT+SHSTATE?") # Get HTTP status
        self.write_ok("AT+SHCHEAD") # Clear HTTP header
        self.write_ok("AT+SHAHEAD=\"Accept\",\"text/html, */*\"") # Add header content
        self.write_ok("AT+SHAHEAD=\"User-Agent\",\"Chicken Wings\"") #  OK Add header content
        self.write_ok("AT+SHAHEAD=\"Content-Type\",\"application/x-www-form-urlencoded\"") # Add header content
        self.write_ok("AT+SHAHEAD=\"Connection\",\"keep-alive\"") # Add header content
        self.write_ok("AT+SHAHEAD=\"Cache-control\",\"no-cache\"") # Add header content
        self.write_ok("AT+SHSTATE?") # Get HTTP status
        self.write_ok("AT+SHBOD=7,10000") # set body content
# example goes on to set parameterized body content...how to do it raw? else use AT+SHPARA
        self.write_ok("AT+SHREQ=\"{}\",2".format(url)) # 2 for post, 3 for put
# TODO i think at this point i write the image..
        self.port.write(image)
        # out:
        #Get data size is 8. 
        # i think this is where we get 8 for the next cmd?
        #self.write_ok("AT+SHSTATE?") # Get HTTP status
        time.sleep(2) # I think the request takes a bit to actually run; this is a race condition...
        response = self.write("AT+SHREAD=0,15") # read 15 chars back. FIXME variable len!
        # TO DO: check for missing OK
        self.write_ok("AT+SHDISC") # Disconnect HTT
        return(response)

    def gprs_send_beacon(self):
        self.write_ok('AT+HTTPINIT')
        self.write_ok('AT+HTTPPARA="CID",1')
        self.write_ok('AT+HTTPPARA="URL","http://hacks.v9n.us/sim800c/"')
        self.write_ok('AT+HTTPACTION=0')
        time.sleep(2)
        response = self.write_ok('AT+HTTPREAD')
        return(response)

    def print_status(self):
        print("Network signal quality query, returns a signal value:")
        self.write_ok('AT+CSQ')
        #print("Firmware version:")
        #write_ok('AT+CGMR')
        print("Network registration status:")
        self.write_ok("AT+CGREG?")
        print("CPSI shows LTE connectivity status:")
        self.write_ok("AT+CPSI?")
        print("APN:")
        self.write_ok("AT+COPS?")
        print("IP address:")
        self.write_ok("AT+CNACT?")
