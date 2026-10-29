from RPi import GPIO
from Device import *
import time

def init():
    GPIO.setmode(GPIO.BCM)
    GPIO.setwarnings(False)
    init_BTS()
    init_servo()
    init_LCD()

def main():
    init()
    alpha = 0
    lcd_clear()
    while True:
        if GPIO.input(BTS['BT_1']) == GPIO.LOW:
            alpha = 20
            lcd_clear()
        elif GPIO.input(BTS['BT_2']) == GPIO.LOW:
            alpha = 60
            lcd_clear()
        elif GPIO.input(BTS['BT_3']) == GPIO.LOW:
            alpha = 160
            lcd_clear()

        lcd_display_string('alpha {}*'.format(alpha), 1)
        set_servo_angle(alpha)
        time.sleep(0.02)

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        if pwmServo is not None:
            pwmServo.stop()
        lcd_clear()
        GPIO.cleanup()