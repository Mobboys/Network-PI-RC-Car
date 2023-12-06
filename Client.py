import socket
import time
from inputs import get_gamepad
import math
import threading
import cv2
import pickle
import sys


# C:\Users\vance\PycharmProjects\RC_Client\venv\Scripts\python.exe
class XboxController(object):
    MAX_TRIG_VAL = math.pow(2, 8)
    MAX_JOY_VAL = math.pow(2, 15)

    def __init__(self):

        self.LeftJoystickY = 0
        self.LeftJoystickX = 0
        self.RightJoystickY = 0
        self.RightJoystickX = 0
        self.LeftTrigger = 0
        self.RightTrigger = 0
        self.LeftBumper = 0
        self.RightBumper = 0
        self.A = 0
        self.X = 0
        self.Y = 0
        self.B = 0
        self.LeftThumb = 0
        self.RightThumb = 0
        self.Back = 0
        self.Start = 0
        self.LeftDPad = 0
        self.RightDPad = 0
        self.UpDPad = 0
        self.DownDPad = 0

        self._monitor_thread = threading.Thread(target=self._monitor_controller, args=())
        self._monitor_thread.daemon = True
        self._monitor_thread.start()

    def read(self):  # return the buttons/triggers that you care about in this methode
        x = self.LeftJoystickX
        y = self.LeftJoystickY
        x2 = self.RightJoystickX
        y2 = self.RightJoystickY
        a = self.A
        b = self.X  # b=1, x=2
        rb = self.RightBumper
        return [x, y, x2, y2, a, b, rb]

    def _monitor_controller(self):
        while True:
            events = get_gamepad()
            for event in events:
                match event.code:
                    case 'ABS_Y':
                        self.LeftJoystickY = event.state / XboxController.MAX_JOY_VAL  # normalize between -1 and 1
                    case 'ABS_X':
                        self.LeftJoystickX = event.state / XboxController.MAX_JOY_VAL  # normalize between -1 and 1
                    case 'ABS_RY':
                        self.RightJoystickY = event.state / XboxController.MAX_JOY_VAL  # normalize between -1 and 1
                    case 'ABS_RX':
                        self.RightJoystickX = event.state / XboxController.MAX_JOY_VAL  # normalize between -1 and 1
                    case 'ABS_Z':
                        self.LeftTrigger = event.state / XboxController.MAX_TRIG_VAL  # normalize between 0 and 1
                    case 'ABS_RZ':
                        self.RightTrigger = event.state / XboxController.MAX_TRIG_VAL  # normalize between 0 and 1
                    case 'BTN_TL':
                        self.LeftBumper = event.state
                    case 'BTN_TR':
                        self.RightBumper = event.state
                    case 'BTN_SOUTH':
                        self.A = event.state
                    case 'BTN_NORTH':
                        self.Y = event.state  # previously switched with X
                    case 'BTN_WEST':
                        self.X = event.state  # previously switched with Y
                    case 'BTN_EAST':
                        self.B = event.state
                    case 'BTN_THUMBL':
                        self.LeftThumb = event.state
                    case 'BTN_THUMBR':
                        self.RightThumb = event.state
                    case 'BTN_SELECT':
                        self.Back = event.state
                    case 'BTN_START':
                        self.Start = event.state
                    case 'BTN_TRIGGER_HAPPY1':
                        self.LeftDPad = event.state
                    case 'BTN_TRIGGER_HAPPY2':
                        self.RightDPad = event.state
                    case 'BTN_TRIGGER_HAPPY3':
                        self.UpDPad = event.state
                    case 'BTN_TRIGGER_HAPPY4':
                        self.DownDPad = event.state


def send_gamepad_data(serverAddress, joy, s):
    x, y, x2, y2, a, b, rb = joy.read()
    x = round(x * 35 + 95, 1)
    data = str('{},{},{},{},{}').format(x, y, x2, y2, rb).encode('utf-8')
    s.sendall(data)
    #print(data)


def receive_image_data(s, bufferSize):
    data = s.recv(bufferSize)                   #Latest Error - ConnectionResetError: [WinError 10054] An existing connection was forcibly closed by the remote host
    Frame = pickle.loads(data) #pickle data was truncated
    print(Frame)
    #cv2.imshow('Camera Feed', Frame)



def main():
    serverAddress = ('192.168.0.99', 5000)#('rc-receiver-udp.at.remote.it', 33001)
    bufferSize = 1024
    joy = XboxController()

    #UDPClient = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:#not working, kept saying client refused connection when using remote.it
        s.connect(serverAddress)
        print("connected to", serverAddress)


        while True:
            send_gamepad_data(serverAddress, joy, s)
            receive_image_data(s, bufferSize)  # uh oh he too big
            if cv2.waitKey(1) == ord('q'):
                break
            time.sleep(.01)


if __name__ == '__main__':
    main()
