import cv2
import RPi.GPIO as GPIO
import numpy as np
import time

LCD_PINS = {'RS': 23, 'E': 27, 'D4': 18, 'D5': 17, 'D6': 14, 'D7': 3, 'BL': 2}
LCD_WIDTH = 16
LCD_CHR = True
LCD_CMD = False
LCD_LINE_1 = 0x80
LCD_LINE_2 = 0xC0
E_PULSE = 0.0005
E_DELAY = 0.0005


def lcd_init():
    GPIO.setmode(GPIO.BCM)
    GPIO.setwarnings(False)
    for pin in LCD_PINS.values():
        GPIO.setup(pin, GPIO.OUT)
    lcd_byte(0x33, LCD_CMD)
    lcd_byte(0x32, LCD_CMD)
    lcd_byte(0x28, LCD_CMD)
    lcd_byte(0x0C, LCD_CMD)
    lcd_byte(0x06, LCD_CMD)
    lcd_byte(0x01, LCD_CMD)
def lcd_clear():
    lcd_byte(0x01, LCD_CMD)
def lcd_byte(bits, mode):
    GPIO.output(LCD_PINS['RS'], mode)
    for bit_num in range(4):
        GPIO.output(LCD_PINS[f'D{bit_num+4}'], bits & (1 << (bit_num + 4)) != 0)
    time.sleep(E_DELAY)
    GPIO.output(LCD_PINS['E'], True)
    time.sleep(E_PULSE)
    GPIO.output(LCD_PINS['E'], False)
    time.sleep(E_DELAY)
    for bit_num in range(4):
        GPIO.output(LCD_PINS[f'D{bit_num+4}'], bits & (1 << bit_num) != 0)
    time.sleep(E_DELAY)
    GPIO.output(LCD_PINS['E'], True)
    time.sleep(E_PULSE)
    GPIO.output(LCD_PINS['E'], False)
    time.sleep(E_DELAY)

def lcd_display_string(message, line):
    lcd_byte(LCD_LINE_1 if line == 1 else LCD_LINE_2, LCD_CMD)
    for char in message:
        lcd_byte(ord(char), LCD_CHR)

def main():
    BT1 = 21
    BT2 = 20  # Thêm nút BT2
    GPIO.setmode(GPIO.BCM)
    GPIO.setwarnings(False)
    GPIO.setup(BT1, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    GPIO.setup(BT2, GPIO.IN, pull_up_down=GPIO.PUD_UP)

    global namewindow
    namewindow = "Camera User"
    capture = cv2.VideoCapture(0)
    print("Capture ready")
    lcd_init()
    while True:
        ret, frame = capture.read()
        if GPIO.input(BT1) == GPIO.LOW:
            print("Nhan Button 1")
            cv2.imshow("Anh chup camera", frame)
            cv2.waitKey(0)  # Hiển thị ảnh chụp
            cv2.destroyWindow("Anh chup camera")

        if GPIO.input(BT2) == GPIO.LOW:
            print("Nhan Button 2")
            # Xử lý ảnh để đếm pixel màu đỏ
            hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
            red_mask = cv2.inRange(hsv,(0,118,130),(5,255,255))
            red_pixel_count = cv2.countNonZero(red_mask)
            lcd_clear()
            lcd_display_string(f"Red Pixels: {red_pixel_count}", LCD_LINE_1)
            print(f"Red Pixels: {red_pixel_count}")

try:
    main()
except KeyboardInterrupt:
    cv2.destroyAllWindows()
    GPIO.cleanup()



