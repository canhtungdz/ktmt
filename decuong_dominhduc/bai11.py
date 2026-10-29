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
    while True:
        if GPIO.input(BTS['BT_1']) == GPIO.LOW:
            alpha = alpha + 10
            print(alpha)
            if alpha > 160:
                alpha = 10
                lcd_clear()
            set_servo_angle(alpha)
            time.sleep(0.02)

        lcd_display_string('alpha: {}'.format(alpha), 1)


try:
    main()
except KeyboardInterrupt:
    lcd_clear()
    if pwmServo is not None:
        pwmServo.stop()
    GPIO.cleanup()