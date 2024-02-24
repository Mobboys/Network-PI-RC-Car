import socket
import RPi.GPIO as GPIO
import time
import cv2
import pickle
import struct
import time
import math
import smbus


class PCA9685:

  # Registers/etc.
  __SUBADR1            = 0x02
  __SUBADR2            = 0x03
  __SUBADR3            = 0x04
  __MODE1              = 0x00
  __PRESCALE           = 0xFE
  __LED0_ON_L          = 0x06
  __LED0_ON_H          = 0x07
  __LED0_OFF_L         = 0x08
  __LED0_OFF_H         = 0x09
  __ALLLED_ON_L        = 0xFA
  __ALLLED_ON_H        = 0xFB
  __ALLLED_OFF_L       = 0xFC
  __ALLLED_OFF_H       = 0xFD

  def __init__(self, address=0x40, debug=False):
    self.bus = smbus.SMBus(1)
    self.address = address
    self.debug = debug
    if (self.debug):
      print("Reseting PCA9685")
    self.write(self.__MODE1, 0x00)
	
  def write(self, reg, value):
    "Writes an 8-bit value to the specified register/address"
    self.bus.write_byte_data(self.address, reg, value)
    if (self.debug):
      print("I2C: Write 0x%02X to register 0x%02X" % (value, reg))
	  
  def read(self, reg):
    "Read an unsigned byte from the I2C device"
    result = self.bus.read_byte_data(self.address, reg)
    if (self.debug):
      print("I2C: Device 0x%02X returned 0x%02X from reg 0x%02X" % (self.address, result & 0xFF, reg))
    return result
	
  def setPWMFreq(self, freq):
    "Sets the PWM frequency"
    prescaleval = 25000000.0    # 25MHz
    prescaleval /= 4096.0       # 12-bit
    prescaleval /= float(freq)
    prescaleval -= 1.0
    if (self.debug):
      print("Setting PWM frequency to %d Hz" % freq)
      print("Estimated pre-scale: %d" % prescaleval)
    prescale = math.floor(prescaleval + 0.5)
    if (self.debug):
      print("Final pre-scale: %d" % prescale)

    oldmode = self.read(self.__MODE1);
    newmode = (oldmode & 0x7F) | 0x10        # sleep
    self.write(self.__MODE1, newmode)        # go to sleep
    self.write(self.__PRESCALE, int(math.floor(prescale)))
    self.write(self.__MODE1, oldmode)
    time.sleep(0.005)
    self.write(self.__MODE1, oldmode | 0x80)

  def setPWM(self, channel, on, off):
    "Sets a single PWM channel"
    self.write(self.__LED0_ON_L+4*channel, on & 0xFF)
    self.write(self.__LED0_ON_H+4*channel, on >> 8)
    self.write(self.__LED0_OFF_L+4*channel, off & 0xFF)
    self.write(self.__LED0_OFF_H+4*channel, off >> 8)
    if (self.debug):
      print("channel: %d  LED_ON: %d LED_OFF: %d" % (channel,on,off))
	  
  def setServoPulse(self, channel, pulse):
    "Sets the Servo Pulse,The PWM frequency must be 50HZ"
    pulse = pulse*4096/20000        #PWM frequency is 50HZ,the period is 20000us
    self.setPWM(channel, 0, int(pulse))




def receive(conn, bufferSize):
    data = conn.recv(bufferSize)              #Latest Error (Matching Client.py) - OSError: [Errno 107] Transport endpoint is not connected
    data = data.decode('utf-8')
    controllerInputs = [float(x) for x in data.split(',')]
    return controllerInputs


def send(s, cap):
    _, frame = cap.read()
    serialized = pickle.dumps("test")
    s.sendall(serialized) #OSError: [Errno 90] Message too long  <-   I only get this error when it uses RPIsocket


def motorControl(controllerInputs, lastAngle, pwm):
    angle = controllerInputs[0]
    speed = controllerInputs[1]
    pwm.setPWMFreq(50)
    pwm.setServoPulse(1,speed)
    if lastAngle != angle:
        print(angle)
        pwm.setPWMFreq(50)
        # setServoPulse(2,2500)
        pwm.setServoPulse(0,angle) 
        lastAngle = angle
        return angle
    else:
        return lastAngle


def main():
    lastAngle = 0
    pwm = PCA9685(0x40, debug=False)

    bufferSize = 1024
    serverPort = 5001
    serverIP = '192.168.4.229'


    #RPIsocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    #RPIsocket.bind((serverIP, serverPort))
    with socket.socket(socket.AF_INET, socket.SOCK_DGRAM) as s:
        s.bind((serverIP, serverPort))
        s.listen(1)
        print ('Server Ready...')
        conn, addr = s.accept()

        with conn:
            print('Connected by', addr)
            
            while True:
                controllerInputs = receive(conn, bufferSize)
                lastAngle = motorControl(controllerInputs, lastAngle, pwm)
                # send(s, cap)  # uh oh he too big

def new_main():
    FRAME_WIDTH = 1920 // 10000
    FRAME_HEIGHT = 1080 // 10000
    VIDEO_DEVICE = 0
    cap = cv2.VideoCapture(VIDEO_DEVICE)
    cap.set(cv2.CAP_PROP_FPS, 5)
    #cap.set(cv2.CAP_PROP_FRAME_WIDTH, FRAME_WIDTH)
    #cap.set(cv2.CAP_PROP_FRAME_HEIGHT, FRAME_HEIGHT)

    header_size = 10

    s = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
    s.bind(('192.168.0.99', 5000))
    s.listen(5)
    clientsocket, address = s.accept()
    print(f"Connection from {address} has been made!")

    while True:
        _, frame = cap.read()
        msg = pickle.dumps(frame)
        msg = bytes(f'{len(msg):<{header_size}}', 'utf-8') + msg

        clientsocket.sendall(msg)

        time.sleep(4)

def new_new_main():
    GPIO.setwarnings(False)
    GPIO.setmode(GPIO.BOARD)
    GPIO.setup(11, GPIO.OUT)
    servo1 = GPIO.PWM(11, 50)  # Note 11 is pin, 50 = 50Hz pulse
    servo1.start(0)
    lastAngle = 0

    GPIO.setup(13, GPIO.OUT)
    motor = GPIO.PWM(13, 100.8)
    motor.start(0)
    lastSpeed = 0
        # Socket Create
    server_socket = socket.socket(socket.AF_INET,socket.SOCK_STREAM)
    FRAME_WIDTH = 1920 // 10000
    FRAME_HEIGHT = 1080 // 10000
    #host_name  = socket.gethostname()
    host_ip = '192.168.0.99' #'172.20.10.2' #'192.168.0.99' #socket.gethostbyname(host_name)
    print('HOST IP:',host_ip)
    port = 5000
    socket_address = (host_ip,port)

    # Socket Bind
    server_socket.bind(socket_address)

    # Socket Listen
    server_socket.listen(5)
    print("LISTENING AT:",socket_address)

    # Socket Accept
    #while True:
    client_socket,addr = server_socket.accept()
    print('GOT CONNECTION FROM:',addr)
    if client_socket:
        vid = cv2.VideoCapture(0)
        vid.set(cv2.CAP_PROP_FRAME_WIDTH, FRAME_WIDTH)
        vid.set(cv2.CAP_PROP_FRAME_HEIGHT, FRAME_HEIGHT)
        
        while(True): #vid.isOpened()
            img,frame = vid.read()
            a = pickle.dumps(frame)
            message = struct.pack("Q",len(a))+a
            # client_socket.sendall(message)
            controllerInputs = receive(client_socket)
            lastAngle = motorControl(controllerInputs[0], lastAngle, servo1)
            lastSpeed = motorControl(controllerInputs[1], lastSpeed, motor)


if __name__ == "__main__":
    main()
