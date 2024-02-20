import cv2
import pickle
import socket
import base64
import numpy
import time
import math
import smbus
from flask import Flask, render_template, Response, stream_with_context, request


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




FRAME_WIDTH = 1920 // 2
FRAME_HEIGHT = 1080 // 2

def main():

    t = numpy.arange(3, dtype=numpy.float64)
    s = base64.b64encode(t)
    r = base64.decodebytes(s)
    q = numpy.frombuffer(r, dtype=numpy.float64)

    print(numpy.allclose(q, t))

    cap = cv2.VideoCapture(0)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, FRAME_WIDTH)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, FRAME_HEIGHT)

    while True:
        _, frame = cap.read()
        #_, buffer = cv2.imencode(".jpg", frame, [int(cv2.IMWRITE_JPEG_QUALITY), 30])
        #serialized = pickle.dumps(frame)
        #Frame = pickle.loads(serialized)                 #"trunkated"
        s = base64.b64encode(frame)
        r = base64.decodebytes(s)
        q = numpy.frombuffer(r, dtype=numpy.float64)
        print(len(q))
        cv2.imshow('Camera Feed', frame)
    
        # serialize and deserialize
        # serialized = pickle.dumps(frame)
        # frame = pickle.loads(serialized)

        #buffer = cv2.imencode(".jpg", photo, [int(cv2.IMWRITE_JPEG_QUALITY), 30])

        # print(frame)
        #cv2.imshow('Camera Feed', frame)
        
        if cv2.waitKey(1) == ord('q'):
            break

    #cap.release()
    #cv2.destroyAllWindows()
def main_socket():

    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        ...

def https_main():
    video = cv2.VideoCapture(0)
    app = Flask('__name__')


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


    app.run(host='0.0.0.0', port='5000', debug=False)

def servo_test():
    pwm = PCA9685(0x40, debug=False)
    pwm.setPWMFreq(50)
    while True:
    # setServoPulse(2,2500)
        for i in range(1100,2100,10):  
            pwm.setServoPulse(0,i)
            print(i)   
            time.sleep(0.02)     
        
        for i in range(2100,1100,-10):
            pwm.setServoPulse(0,i) 
            print(i)
            time.sleep(0.02)  


if __name__ == '__main__':
    servo_test()