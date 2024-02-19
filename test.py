import cv2
import pickle
import socket
import base64
import numpy
from flask import Flask, render_template, Response, stream_with_context, request


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

if __name__ == '__main__':
    https_main()