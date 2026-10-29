#check mk, nhấn giữ nút 1 nhả để chọn số

import RPi.GPIO as GPIO
import time

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

LCD_PINS = {'RS': 23, 'E': 27, 'D4': 18, 'D5': 17, 'D6': 14, 'D7': 3, 'BL': 2}
LCD_WIDTH = 16
LCD_CHR = True
LCD_CMD = False
LCD_LINE_1 = 0x80
LCD_LINE_2 = 0xC0
E_PULSE = 0.0005
E_DELAY = 0.0005

BT1 = 21  
GPIO.setup(BT1, GPIO.IN, pull_up_down=GPIO.PUD_UP) 

RL1 = 16
GPIO.setup(RL1, GPIO.OUT)
GPIO.output(RL1, GPIO.LOW)

PASSWORD = "999"
input_password = ""

def lcd_init():
    for pin in LCD_PINS.values():
        GPIO.setup(pin, GPIO.OUT)
    for byte in [0x33, 0x32, 0x28, 0x0C, 0x06, 0x01]:
        lcd_byte(byte, LCD_CMD)
    GPIO.output(LCD_PINS['BL'], GPIO.HIGH)

def lcd_clear():
    lcd_byte(0x01, LCD_CMD)

def lcd_byte(bits, mode):
    GPIO.output(LCD_PINS['RS'], mode)
    for bit_num in range(4):
        GPIO.output(LCD_PINS[f'D{bit_num + 4}'], bits & (1 << (4 + bit_num)) != 0)
    time.sleep(E_DELAY)
    GPIO.output(LCD_PINS['E'], True)
    time.sleep(E_PULSE)
    GPIO.output(LCD_PINS['E'], False)
    time.sleep(E_DELAY)
    for bit_num in range(4):
        GPIO.output(LCD_PINS[f'D{bit_num + 4}'], bits & (1 << bit_num) != 0)
    time.sleep(E_DELAY)
    GPIO.output(LCD_PINS['E'], True)
    time.sleep(E_PULSE)
    GPIO.output(LCD_PINS['E'], False)
    time.sleep(E_DELAY)

def lcd_display_string(message, line):
    lcd_byte(LCD_LINE_1 if line == 1 else LCD_LINE_2, LCD_CMD)
    for char in message:
        lcd_byte(ord(char), LCD_CHR)

def check_password():
    if input_password == PASSWORD:
        lcd_clear()
        lcd_display_string("Success", 1)
        time.sleep(1)
        GPIO.output(RL1, GPIO.HIGH)
        return True
    
def main():
    global input_password
    lcd_init()
    lcd_clear()
    lcd_display_string("Password", 1)
    
    while True:
        if GPIO.input(BT1) == GPIO.LOW:  
            number = 0
            lcd_clear()   
            while GPIO.input(BT1) == GPIO.LOW: 
                number = (number + 1) % 10  
                lcd_clear()
                lcd_display_string(str(number), 1)
                time.sleep(0.5)  
                
            input_password += str(number) 
            time.sleep(1) 
            lcd_clear()
            lcd_display_string("Password", 1)
            lcd_display_string("*" * len(input_password), 2)  
            time.sleep(1)  
            
            if len(input_password) == 3: 
                if check_password():
                    pass

try:
    main()
except KeyboardInterrupt:
    GPIO.output(RL1, GPIO.LOW)
    lcd_clear()
    GPIO.cleanup()
