from RPi import GPIO
from Device import *
import cv2
import numpy as np

def init():
    GPIO.setmode(GPIO.BCM)
    GPIO.setwarnings(False) 
    init_BTS()
    init_RLS()

def quantity_red_pixel(img, lower, upper):
    hsv = cv2.cvtColor(img, cv2.COLOR_BGR2HSV)
    mask = cv2.inRange(hsv, lower, upper)
    return cv2.countNonZero(mask)

upper_red = np.array([5, 255, 255])
lower_red = np.array([0, 118, 130])
upper_green = np.array([45, 241, 213])
lower_green = np.array([35, 89, 107])

def main():
    init()
    cap = cv2.VideoCapture(0)
    img = None
    while True:
        ret, frame = cap.read()
        if GPIO.input(BTS['BT_1']) == GPIO.LOW:
            cv2.imshow("Camera", frame)
            img = frame
            cv2.waitKey(0)
            cv2.destroyAllWindows()
        if GPIO.input(BTS['BT_2']) == GPIO.LOW:
            quan_red = quantity_red_pixel(img, lower_red, upper_red)
            quan_green = quantity_red_pixel(img, lower_green, upper_green)
            if quan_red > quan_green:
                GPIO.output(RLS['RELAY_1'], GPIO.HIGH)
                GPIO.output(RLS['RELAY_2'], GPIO.LOW)
            else:
                GPIO.output(RLS['RELAY_1'], GPIO.LOW)
                GPIO.output(RLS['RELAY_2'], GPIO.HIGH)

try:
    main()
except KeyboardInterrupt:
    cv2.destroyAllWindows()
    GPIO.cleanup()