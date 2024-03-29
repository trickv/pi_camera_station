import sys
import time
import serial
import subprocess
import re
import RPi.GPIO as GPIO

GPIO.setwarnings(False)

class modem:

    def init(self):
        self.port = serial.Serial("/dev/ttyS0", baudrate=115200, timeout=1)

    def poweroff(self):
        self.write('AT+CPOWD=1')
        time.sleep(1)
        print(self.port.read(1000))
    
    def poweron(self):
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(4, GPIO.OUT)
        GPIO.output(4, GPIO.HIGH)
        time.sleep(0.5)
        GPIO.output(4, GPIO.LOW)
        #time.sleep(1)
        while True:
            self.write_noblock('AT')
            rcv = self.port.read(100)
            if len(rcv) > 0:
                print(rcv)
                break
            print(".", end='', flush=True)
            time.sleep(1)

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

    def read(self):
        return(self.port.read(1000).decode('latin1'))

    def read_ok(self):
        return self.read_expect("OK")

    def read_expect(self, expect_message, command="Unknown"):
        received = b''
        timeout_cycles = 90
        counter = 0
        while True:
            received += self.port.read_until(size=1000)
            if len(received) > 0:
                if received.decode('latin1').find("ERROR") >= 0:
                    print(received[:100])
                    #self.poweroff()
                    print("I found an ERROR, oops! Exiting.")
                    sys.exit(1)

                if received.decode('latin1').find(expect_message) >= 0:
                    print(received[:100])
                    return received.decode('latin1')
            print(".", end="", flush=True)
            counter += 1
            if counter > timeout_cycles:
                raise Exception("modem: read timeout after command '{}' waiting for expected message '{}'".format(command, expect_message))
            time.sleep(0.1)

    def write_ok(self, command):
        self.write_noblock(command)
        return self.read_ok()
    
    def write_ok_plus(self, command, next_expect):
        self.write_noblock(command)
        return self.read_ok() + self.read_expect(next_expect, command)

    def write_expect(self, command, expect):
        self.write_noblock(command)
        self.read_expect(expect, command)

    
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
        self.write("AT+CNACT=0,0") # disconnect
        self.write_ok("AT+CNACT=0,1") # connect
        iter = 0
        while True:
            iter += 1
            if iter > 300:
                print("oops: never came online? :(")
                return
            self.write_noblock("AT+CPSI?")
            out = self.read_expect("CPSI", "lte_connect CPSI?")
            out += self.read()
            if out.find("LTE") >= 0:
                print("looks online to me...let's see if we have an IP:")
                # ok: AT+CNACT?\r\r\n+CNACT: 0,1,"100.70.169.229"\r\n+CNACT: 1,0,"0.0.0.0"\r\n+CNACT: 2,0,"0.0.0.0"\r\n+CNACT: 3,0,"0.0.0.0"\r\n\r\nOK\r\nAT+SHDISC\r\r\nERROR\r\n
                # not good: ......b'AT+CNACT?\r\r\n+CNACT: 0,0,"0.0.0.0"\r\n+CNACT: 1,0,"0.0.0.0"\r\n+CNACT: 2,0,"0.0.0.0"\r\n+CNACT: 3,0,"0.0.0.'
                ip_match = re.compile(".*\+CNACT: \d,1.*", flags=re.MULTILINE|re.DOTALL)
                out = self.write_ok("AT+CNACT?")
                if ip_match.match(out) is not None:
                    print("ok now have an IP, really online now.")
                    return
                else:
                    print("no ip yet!")
            else:
                print("not online...")
                time.sleep(1)

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
        status_output = self.write_ok_plus("AT+SHREQ=\"{}\",1".format(url), "+SHREQ") # type 1 is GET. This is where the request is executed.
        [status, length] = self.parse_http_status(status_output)
        response = self.write("AT+SHREAD=0,{}".format(length)) # read
        # TO DO: check for missing OK
        self.write_ok("AT+SHDISC") # Disconnect HTT
        return(response)
   
    def lte_http_post(self, url, data):
        if len(data) > 4096:
            raise Exception("max of 4096 requested")
        host = "/".join(url.split("/")[0:3])
        length = len(data)
        self.write_ok("AT+SHCONF=\"URL\",\"{}\"".format(host)) # Set up server URL
        self.write_ok("AT+SHCONF=\"BODYLEN\",{}".format(length)) # Set HTTP body length
        self.write_ok("AT+SHCONF=\"HEADERLEN\",350") # Set HTTP head length
        self.write_ok("AT+SHCONN") # HTTP build
        self.write_expect("AT+SHBOD={},10000".format(length), ">") # set body content length and input timeout of 10000ms
        self.port.write(data)
        self.read_ok()
        status_output = self.write_ok_plus("AT+SHREQ=\"{}\",3".format(url), "+SHREQ") # 2 for post, 3 for put
        [status, length] = self.parse_http_status(status_output)
        response = self.write("AT+SHREAD=0,{}".format(length)) # read
        print("DBG: response: {}".format(response))
        self.write_ok("AT+SHDISC") # Disconnect HTTP
        return([status, length, response])

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

    def parse_http_status(self, status):
        # x = b'\r\nOK\r\n+SHREQ: "GET",200,472\r\n'
        # real:
        # b'AT+SHREQ="http://hacks.v9n.us/sim800c/",1\r\r\nOK\r\n'
        # b'\r\n+SHREQ: "GET",200,15\r\nAT+SHREAD=0,15\r\r\nOK\r\n\r\n+SHREAD: 15\r\nOK no need...\n\n\r\n'
        for line in status.split("\r\n"):
            if line.find("+SHREQ:") >= 0:
                ret = line.split(": ")[1].split(',')
                print("status {}, len: {}".format(ret[1], ret[2]))
                return [int(ret[1]), ret[2]]
        raise Exception("failed to parse HTTP status out of this: {}".format(status))

    def sync_clock(self):
        self.read() # flush the buffer
        self.write_ok("AT+CNTP=pool.ntp.org")
        #output = self.write_ok_plus("AT+CNTP", "+CNTP")
        self.write_noblock("AT+CNTP")
        time.sleep(10)
        output = self.read()
        print("got:")
        print(output)
        for_timedatectl_time = output.split('"')[1].replace("+00","").replace("/","-").replace(","," ")
        print("Setting system clock via timedatectl to {}".format(for_timedatectl_time))
        subprocess.run("sudo timedatectl set-time \"{}\"".format(for_timedatectl_time), shell=True)
