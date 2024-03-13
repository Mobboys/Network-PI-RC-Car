import socket
import RPi.GPIO as GPIO
import time
import cv2
import pickle
import struct
import time
import math
import smbus
import numpy
from flask import Flask, render_template, Response, stream_with_context, request


video = cv2.VideoCapture(0)
app = Flask('__name__')


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
    print("(" + data + ")")
    controllerInputs = [float(x) for x in data.split(',')]
    return controllerInputs


def send(s, cap):
    _, frame = cap.read()
    serialized = pickle.dumps("test")
    s.sendall(serialized) #OSError: [Errno 90] Message too long  <-   I only get this error when it uses RPIsocket


def motorControl(controllerInputs, lastPos, pwm, x):
    pos = controllerInputs
    if lastPos != pos:
        pwm.setServoPulse(x,pos) 
        lastPos = pos
        return pos
    else:
        return lastPos
    
    
def video_stream():
    while True:
        ret, frame = video.read()
        if not ret:
            break
        else:
            ret, buffer = cv2.imencode('.jpeg',frame)
            frame = buffer.tobytes()
            yield (b' --frame\r\n' b'Content-type: imgae/jpeg\r\n\r\n' + frame +b'\r\n')


@app.route('/camera')
def camera():
    return render_template('camera.html')


@app.route('/video_feed')
def video_feed():
    return Response(video_stream(), mimetype='multipart/x-mixed-replace; boundary=frame')


def main():
    lastAngle = 0
    lastSpeed = 0
    motor = PCA9685(0x40, debug=False)
    servo = PCA9685(0x40, debug=False)
    motor.setPWMFreq(50)
    servo.setPWMFreq(50)

    bufferSize = 1024
    serverPort = 5001
    serverIP = '192.168.4.229'

    app.run(host='0.0.0.0', port='5000', debug=False)

    #RPIsocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    #RPIsocket.bind((serverIP, serverPort))
    with socket.socket() as s: #socket.AF_INET, socket.SOCK_STREAM
        s.bind((serverIP, serverPort))
        s.listen(1)
        print ('Server Ready...')
        conn, addr = s.accept()

        with conn:
            print('Connected by', addr)
            
            while True:
                controllerInputs = receive(conn, bufferSize)
                lastAngle = motorControl(controllerInputs[0], lastAngle, servo, 0)

                lastSpeed = motorControl(controllerInputs[1], lastSpeed, motor, 1)
                # send(s, cap)  # uh oh he too big
                
                time.sleep(.05)


if __name__ == "__main__":
    main()
