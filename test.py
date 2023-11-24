import cv2
import pickle

FRAME_WIDTH = 1920 // 2
FRAME_HEIGHT = 1080 // 2

def main():
    cap = cv2.VideoCapture(1)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, FRAME_WIDTH)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, FRAME_HEIGHT)

    if True:
        ret, frame = cap.read()
        print(ret, frame)
    
        # serialize and deserialize
        # serialized = pickle.dumps(frame)
        # frame = pickle.loads(serialized)

        buffer = cv2.imencode(".jpg",photo,[int(cv2.IMWRITE_JPEG_QUALITY),30])

        # print(frame)
        #cv2.imshow('Camera Feed', frame)
        
        # if cv2.waitKey(1) == ord('q'):
        #     break

    cap.release()
    cv2.destroyAllWindows()


if __name__ == '__main__':
    main()