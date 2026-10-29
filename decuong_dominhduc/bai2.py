# Viết chương trình nhấn nút bấm 1 lần 1 từng ký tự trong chữ "Hello-World" chạy từ phải sang trái màn hình LCD
# 16x2, nhấn nút bẩm 1 lần 2 từng ký tự trong chữ trên chạy từ trái sang phải màn hình LCD 16x2, nhấn nút bấm 1
# lần 3 thì xóa trắng màn hình. Ưu tiên nút bấm.

# error: bấm lần 1 từ trái sang phải.
from RPi import GPIO
from Device import *
import time

BT_1 = 21
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
GPIO.setup(BT_1, GPIO.IN, pull_up_down = GPIO.PUD_UP)

def main():
    init_LCD()
    button_state = 0
    time.sleep(1)
    while True:
        if GPIO.input(BT_1) == GPIO.LOW:
            button_state += 1
            time.sleep(0.25)
        if button_state == 2:
            for i in range(LCD_WIDTH - len("Hello-world")):
                lcd_clear()
                lcd_display_string(" " * i  + "Hello-world", 1)
                time.sleep(0.25)
                if GPIO.input(BT_1) == GPIO.LOW:
                    button_state += 1
                    time.sleep(0.1)
                    lcd_clear()
                    break
        elif button_state == 1:
            for i in range(LCD_WIDTH - len("Hello-world"), - 1, -1):
                lcd_clear()
                lcd_display_string(" " * i + "Hello-world", 1)
                time.sleep(0.25)
                if GPIO.input(BT_1) == GPIO.LOW:
                    button_state += 1
                    time.sleep(0.1)
                    lcd_clear()
                    break
        elif button_state >= 3:
            lcd_clear()
            time.sleep(0.1)
            button_state = 0

try:
    main()
except KeyboardInterrupt:
    lcd_clear()
    GPIO.cleanup()
