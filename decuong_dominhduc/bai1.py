# Viết chương trình theo kịch bản sau, nhấn lần lượt theo thứ tự nút bẩm 1, nút bảm 2 thì LED sáng, nhân lần lượt theo thứ tự nút bấm 3, nút bấm 4 thì đèn nền LCD sáng, nhấn giữ đồng thời nút bấm 1 và nút bấm 3 thì cả hai LED và đèn nền LCD tắt
# ? sai yêu cầu.
from RPi import GPIO
from Device import *

def init():
    GPIO.setmode(GPIO.BCM)
    GPIO.setwarnings(False)
    init_BTS()
    init_LCD()
    init_RLS()

def main():
    init()
    status = [0, 0, 0, 0]
    GPIO.output(LCD_PINS['BL'], GPIO.LOW)
    GPIO.output(RLS['LED'], GPIO.LOW)

    while True:
        if BTS['BT_1'] == GPIO.LOW:
            status[0] = 1
        if BTS['BT_2'] == GPIO.LOW and status[0] == 1:
            status[1] = 1
        if BTS['BT_3'] == GPIO.LOW:
            status[2] = 1
        if BTS['BT_4'] == GPIO.LOW and status[2] == 1:
            status[3] = 1
        
        if BTS['BT_1'] == GPIO.LOW and BTS['BT_2'] == GPIO.LOW and BTS['BT_3'] == GPIO.LOW and BTS['BT_4'] == GPIO.LOW:
            status = [0, 0, 0, 0]

        if status[1] == 1:
            GPIO.output(RLS['LED'], GPIO.HIGH)
        if status[3] == 1:
            GPIO.output(LCD_PINS['BL'], GPIO.HIGH)

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        lcd_clear()
        GPIO.cleanup()  