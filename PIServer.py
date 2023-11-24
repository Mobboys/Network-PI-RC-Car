import socket
import RPi.GPIO as GPIO
import time
import cv2
import pickle


def receive(RPIsocket, bufferSize):
    data, address = RPIsocket.recvfrom(bufferSize)
    data = data.decode('utf-8')
    controllerInputs = [float(x) for x in data.split(',')]
    return controllerInputs, address


def send(address, RPIsocket, cap):
    print("are you running here???")
    _, frame = cap.read()
    serialized = pickle.dumps(frame)
    print("type:", serialized.shape)
    RPIsocket.sendto("serialized", address)


def motorControl(controllerInputs, lastAngle, servo1):
    angle = controllerInputs[0]
    if lastAngle != angle:
        #print(angle)
        servo1.ChangeDutyCycle(2+(angle/18))
        lastAngle = angle
        return angle
    else:
        return lastAngle


def main():
    GPIO.setwarnings(False)
    GPIO.setmode(GPIO.BOARD)
    GPIO.setup(11, GPIO.OUT)
    servo1 = GPIO.PWM(11, 50)  # Note 11 is pin, 50 = 50Hz pulse
    servo1.start(0)
    lastAngle = 0

    FRAME_WIDTH = 1920 // 2
    FRAME_HEIGHT = 1080 // 2
    cap = cv2.VideoCapture(0)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, FRAME_WIDTH)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, FRAME_HEIGHT)

    bufferSize = 1024
    serverPort = 5000
    serverIP = '192.168.0.99'


    RPIsocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    RPIsocket.bind((serverIP, serverPort))

    print ('Server Ready...')
    while True:
        print("wtf?")
        controllerInputs, address = receive(RPIsocket, bufferSize)
        print("here???")
        send(address, RPIsocket, cap)
        print("hello?")
        lastAngle = motorControl(controllerInputs, lastAngle, servo1)
        


if __name__ == "__main__":
    main()
