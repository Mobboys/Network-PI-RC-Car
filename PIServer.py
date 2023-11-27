import socket
import RPi.GPIO as GPIO
import time
import cv2
import pickle


def receive(conn, bufferSize):
    data = conn.recv(bufferSize)
    data = data.decode('utf-8')
    controllerInputs = [float(x) for x in data.split(',')]
    return controllerInputs


def send(conn, cap):
    _, frame = cap.read()
    _, buffer = cv2.imencode(".jpg", frame, [int(cv2.IMWRITE_JPEG_QUALITY), 30])
    serialized = pickle.dumps(buffer)
    conn.sendall(serialized)


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
    VIDEO_DEVICE = 0
    cap = cv2.VideoCapture(VIDEO_DEVICE)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, FRAME_WIDTH)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, FRAME_HEIGHT)

    bufferSize = 1024
    serverPort = 5000
    serverIP = '192.168.0.99'


    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((serverIP, serverPort))
        print ('Server Ready...')
        s.listen()
        conn, addr = s.accept()

        print(f"Connected by {addr}")
        
        while True:
            controllerInputs = receive(conn, bufferSize)
            lastAngle = motorControl(controllerInputs, lastAngle, servo1)
            send(conn, cap)  # uh oh he too big


if __name__ == "__main__":
    main()
