from RPi import GPIO
from Device import *
import time

def init():
    GPIO.setmode(GPIO.BCM)
    GPIO.setwarnings(False)
    init_BTS()
    init_motor()

def main():
    init()
    speed = 0
    while True:
        if GPIO.input(BTS['BT_1']) == GPIO.LOW and speed < 100:
            speed += 10
            time.sleep(1)
        if GPIO.input(BTS['BT_2']) == GPIO.LOW:
            speed = 0
        
        motor_control(speed, 0)

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        if pwmMotor is not None:
            pwmMotor.stop()
        GPIO.cleanup()
