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

    def read_ok(self):
        return self.read_expect("OK")

    def read_expect(self, expect_message):
        received = b''
        while True:
            received += self.port.read(1000)
            if len(received) > 0:
                if received.decode('latin1').find("ERROR") >= 0:
                    print(received)
                    self.poweroff()

                if received.decode('latin1').find(expect_message) >= 0:
                    print(received)
                    return received.decode('latin1')
            print(".", end="", flush=True)
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

    def connect_gprs(self):
        self.write_ok('AT+CSTT="hologram"')
        self.write_ok('AT+CIICR')
        self.write_ok('AT+SAPBR=3,1,"Contype","GPRS"')
        self.write_ok('AT+SAPBR=3,1,"APN","hologram"')
        self.write_ok('AT+SAPBR=1,1') # open GPRS context
        self.write_ok('AT+SAPBR=2,1') # Query GPRS context

    def send_beacon(self):
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
        self.write_ok("AT+CREG?")
        print("GPRS attachment status:")
        self.write_ok("AT+CGATT?")
