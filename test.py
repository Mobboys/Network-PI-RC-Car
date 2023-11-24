import cv2
import pickle

FRAME_WIDTH = 1920 // 2
FRAME_HEIGHT = 1080 // 2

def main():
    cap = cv2.VideoCapture(0)
    cap.set(cv2.CAP_PROP_FRAME_WIDTH, FRAME_WIDTH)
    cap.set(cv2.CAP_PROP_FRAME_HEIGHT, FRAME_HEIGHT)

    while True:
        _, frame = cap.read()

        # serialize and deserialize
        serialized = pickle.dumps(frame)
        frame = pickle.loads(serialized)

        print(frame.size, frame)
        #cv2.imshow('Camera Feed', frame)
        
        if cv2.waitKey(1) == ord('q'):
            break

    cap.release()
    cv2.destroyAllWindows()


if __name__ == '__main__':
    main()