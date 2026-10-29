import cv2
import numpy as np 
import time

def quantity_red_pixel(img):
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    lower_red_1 = np.array([0, 50, 50])
    upper_red_1 = np.array([10, 255, 255])
    lower_red_2 = np.array([170, 50, 50])
    upper_red_2 = np.array([180, 255, 255])
    mask1 = cv2.inRange(hsv, lower_red_1, upper_red_1)
    mask2 = cv2.inRange(hsv, lower_red_2, upper_red_2)
    mask = mask1 + mask2

    return cv2.countNonZero(mask)

def main():
    capture = cv2.VideoCapture(0)
    print("Capture ready")
    while True:
        ret, frame = capture.read()
        print(quantity_red_pixel(frame))
        frame = cv2.flip(frame, 1)
        cv2.imshow("Camera urs", frame)
        if cv2.waitKey(1) & 0xFF == ord('q'):
            break
        time.sleep(0.1)
    capture.release()
    cv2.destroyAllWindows()

main()