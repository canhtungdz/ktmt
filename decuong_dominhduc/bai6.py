from RPi import GPIO
from Device import *
import time


ROOM_TEMP = 25
ROOM_HUMI = 70

def init():
    GPIO.setmode(GPIO.BCM)
    GPIO.setwarnings(False)
    init_BTS()
    init_RLS()
    init_DHT11()
    init_LCD()

def main():
    init()
    human = 0
    inout = [0, 0]
    while True:
        if human != 0:
            temp, hum = read_dht11()
            if temp is not None and hum is not None:
                if temp < ROOM_TEMP and hum < ROOM_HUMI:
                    GPIO.output(RLS['RELAY1'], GPIO.HIGH)
                    GPIO.output(RLS['RELAY2'], GPIO.LOW)
                else:
                    GPIO.output(RLS['RELAY1'], GPIO.LOW)
                    GPIO.output(RLS['RELAY2'], GPIO.HIGH)
                lcd_display_string('{}*C, {}%'.format(temp, hum), 1)
                lcd_display_string('human: {}'.format(human), 2)
        
        if GPIO.input(BTS['BT_1']) == GPIO.LOW:
            if inout[1] == 1:
                human -= 1 if human > 0 else 0
                inout = [0, 0]
            else:
                inout[0] = 1
            time.sleep(0.25)
        if GPIO.input(BTS['BT_2']) == GPIO.LOW:
            if inout[0] == 1:
                human += 1
                inout = [0, 0]
            else:
                inout[1] = 1
            time.sleep(0.25)

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        lcd_clear()
        GPIO.cleanup()