from RPi import GPIO
from Device import *
import time
import cv2
import numpy as np

def init():
    GPIO.setmode(GPIO.BCM)
    GPIO.setwarnings(False) 
    init_BTS()
    init_LCD()

def quantity_red_pixel(img):
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    lower_red = np.array([0, 118, 130])
    upper_red = np.array([10, 255, 255])
    mask = cv2.inRange(hsv, lower_red, upper_red)

    return cv2.countNonZero(mask)

def main():
    init()
    lcd_clear()
    cap = cv2.VideoCapture(0)
    img = None
    while True:
        ret, frame = cap.read()
        if BTS['BT_1'] == GPIO.LOW:
            cv2.imshow("Camera", frame)
            img = frame
            cv2.waitKey(0)
            cv2.destroyAllWindows()
            # time.sleep(0.5)
        if BTS['BT_2'] == GPIO.LOW:
            quantity = quantity_red_pixel(img)
            lcd_display_string("Red pixel: {}".format(quantity), 1)
            # cv2.destroyAllWindows()

try:
    main()
except KeyboardInterrupt:
    GPIO.cleanup()
    cv2.destroyAllWindows()
    lcd_clear()