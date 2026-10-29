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
    current_state = 0
    direction = 0
    speeds = {0 : 0, 
              1: (maxSpeed * 0.02), 
              2: (maxSpeed * 0.04), 
              3: maxSpeed}
    
    while True:
        motor_control(speeds[current_state], direction)
        
        if GPIO.input(BTS['BT_1']) == GPIO.LOW:
            current_state += 1
            direction = 0
            time.sleep(0.2)
        
        if GPIO.input(BTS['BT_2']) == GPIO.LOW:
            current_state += 1
            direction = 1
            time.sleep(0.2)
            
        if current_state > 3:
            current_state = 0

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        if pwmMotor is not None:
            pwmMotor.stop()
        GPIO.cleanup()