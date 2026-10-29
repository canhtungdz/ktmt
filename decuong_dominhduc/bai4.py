from RPi import GPIO
from Device import *
import time

def init():
    GPIO.setmode(GPIO.BCM)
    GPIO.setwarnings(False)
    init_LCD()
    init_BTS()
    init_RLS()

def check_password(pass_word):
    if pass_word == [9, 9, 9]:
        GPIO.output(RLS['RELAY_1'], True)
        lcd_clear()
        lcd_display_string("thanh cong", 2)
        return True
    else:
        lcd_clear()
        lcd_display_string("thu lai", 2)
        time.sleep(1)
        lcd_clear()
        pass_word = [0, 0, 0]
        return False

def main():
    init()
    pass_word = [0, 0, 0]
    str_pass = ""
    current_pass = 0
    while True:
        if GPIO.input(BTS['BT_1']) == GPIO.LOW:
            lcd_display_string(str_pass + str(pass_word[current_pass]), 1)
            str_pass += '*'
            time.sleep(0.5)
            lcd_display_string(str_pass, 1)
            pass_word[current_pass] += 1
            if pass_word[current_pass] == 10:
                pass_word[current_pass] = 0
            continue

        current_pass += 1
        if current_pass == 3:
            current_pass = 3 if check_password(pass_word) else 0
    
if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        lcd_clear()
        GPIO.cleanup()
        pass