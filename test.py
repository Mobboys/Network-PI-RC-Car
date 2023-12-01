import cv2
import pickle
import base64
import numpy as np


FRAME_WIDTH = 1920 // 2
FRAME_HEIGHT = 1080 // 2

def main():

    t = np.arange(3, dtype=np.float64)
    s = base64.b64encode(t)
    r = base64.decodebytes(s)
    q = np.frombuffer(r, dtype=np.float64)

    print(np.allclose(q, t))

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
        q = np.frombuffer(r, dtype=np.float64)
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


if __name__ == '__main__':
    main()