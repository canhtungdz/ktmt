from RPi import GPIO
from Device import *
import time

def init():
    GPIO.setmode(GPIO.BCM)
    GPIO.setwarnings(False)
    init_RLS()
    init_motor()
    init_distance()
    init_LCD()

n1, n2, n3, n4 = 10, 15, 20, 30

def main():
    lcd_clear()
    init()
    while True:
        distance = cal_distance()

        if distance > 100:
            lcd_clear()
            lcd_display_string('ERROR', 1)
        else:
            if distance >= n3:
                motor_control(50, 0)
            else:
                if distance >= n2:
                    GPIO.output(RLS['RELAY_1'], GPIO.HIGH)
                else:
                    if distance >= n1:
                        GPIO.output(RLS['LED'], GPIO.HIGH)
                    else:
                        GPIO.output(RLS['LED'], GPIO.LOW)
                    GPIO.output(RLS['RELAY_1'], GPIO.LOW)
                motor_control(0, 0)

            lcd_display_string(f'Distance: {distance}', 1)

        time.sleep(1)

try:
    main()
except KeyboardInterrupt:
    lcd_clear()
    if pwmMotor is not None:
        pwmMotor.stop()
    GPIO.cleanup()