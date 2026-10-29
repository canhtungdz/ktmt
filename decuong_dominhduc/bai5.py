from RPi import GPIO
from Device import *
import time

ROOM_TEMP = 27

def init():
    GPIO.setmode(GPIO.BCM)
    GPIO.setwarnings(False)
    init_RLS()
    init_LCD()
    init_DHT11()

def main():
    init()
    lcd_clear()
    
    while True:
        temp, hum = read_dht11()
        if temp is not None:
            if temp > ROOM_TEMP:
                GPIO.output(RLS['RELAY_1'], GPIO.HIGH)
                GPIO.output(RLS['RELAY_2'], GPIO.HIGH)
            elif temp == ROOM_TEMP:
                GPIO.output(RLS['RELAY_1'], GPIO.HIGH)
                GPIO.output(RLS['RELAY_2'], GPIO.LOW)
            else:
                GPIO.output(RLS['RELAY_1'], GPIO.LOW)
                GPIO.output(RLS['RELAY_2'], GPIO.LOW)
            lcd_display_string(f'Temp: {temp}', 1)

if __name__ == '__main__':
    try:
        main()
    except KeyboardInterrupt:
        lcd_clear()
        GPIO.cleanup()