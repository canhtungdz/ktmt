from RPi import GPIO
from Device import *
import time

heart = [
    0b00000000,
    0b00000000,
    0b00000000,
    0b00000000,
    0b00000000,
    0b00000000,
    0b00000000,
    0b00000000,
]

heart = [hex(_) for _ in heart]

def init():
    GPIO.setmode(GPIO.BCM)
    GPIO.setwarnings(False) 
    init_BTS()
    init_led_matrix(init_clk_din_cs=True)

def main():
    init()
    while True:
        time.sleep(1)
        display_pattern(heart)
        time.sleep(1)
        clear_display()

try:
    main()
except KeyboardInterrupt:
    clear_display()
    GPIO.cleanup()