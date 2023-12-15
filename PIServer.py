import socket
import RPi.GPIO as GPIO
import time
import cv2
import pickle
import struct


def receive(client_socket):
    data = client_socket.recv(13)              #Latest Error (Matching Client.py) - OSError: [Errno 107] Transport endpoint is not connected
    data = data.decode('utf-8')
    print(data)
    controllerInputs = [float(x) for x in data.split(',')]
    return controllerInputs


def send(s, cap):
    _, frame = cap.read()
    serialized = pickle.dumps("test")
    print (serialized)
    s.sendall(serialized) #OSError: [Errno 90] Message too long  <-   I only get this error when it uses RPIsocket


def motorControl(controllerInputs, lastAngle, servo1):
    angle = controllerInputs
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


    #RPIsocket = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    #RPIsocket.bind((serverIP, serverPort))
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        s.bind((serverIP, serverPort))
        s.listen(1)
        print ('Server Ready...')
        conn, addr = s.accept()

        with conn:
            print('Connected by', addr)
            
            while True:
                controllerInputs = receive(s, bufferSize)
                lastAngle = motorControl(controllerInputs, lastAngle, servo1)
                send(s, cap)  # uh oh he too big

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
            #lastAngle = motorControl(controllerInputs[0], lastAngle, servo1)
            #lastSpeed = motorControl(controllerInputs[1], lastSpeed, motor)


if __name__ == "__main__":
    new_new_main()
