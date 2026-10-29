#menu, nút 1 quay lại, nút 2 lên, nút 3 xuống, nút 4 chọn

import RPi.GPIO as GPIO
import time
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

BTS = {"BT1" : 21, "BT2" : 26, "BT3" : 20, "BT4" : 19}
for bt in BTS.values():
    GPIO.setup(bt, GPIO.IN, pull_up_down=GPIO.PUD_UP)

RLS = {"RELAY_1" : 16, "RELAY_2" : 12, "LED": 13}
for rls in RLS.values():
    GPIO.setup(rls, GPIO.OUT)
    GPIO.output(rls, GPIO.LOW)

current_menu = 'Main'
current_level = 1
current_pos = 1

LCD_PINS = {'RS': 23, 'E': 27, 'D4': 18, 'D5': 17, 'D6': 14, 'D7': 3, 'BL':2}
LCD_WIDTH = 16
LCD_CHR = True
LCD_CMD = False
LCD_LINE_1 = 0x80
LCD_LINE_2 = 0xC0
E_PULSE = 0.0005
E_DELAY = 0.0005

def lcd_init():
    for pin in LCD_PINS.values():
        GPIO.setup(pin, GPIO.OUT)
    for byte in [0x33, 0x32, 0x28, 0x0C, 0x06, 0x01]:
        lcd_byte(byte, LCD_CMD)
    GPIO.output(LCD_PINS['BL'], GPIO.HIGH)

def lcd_clear():
    lcd_byte(0x01, LCD_CMD)

def lcd_byte(bits, mode):
    GPIO.output (LCD_PINS['RS'], mode)
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

def display_menu(menu_name):
    lcd_clear()
    lcd_display_string(menu_name, 1)

def on_button1_pressed():
    global current_menu, current_level, current_pos
    if current_level > 1:
        current_level -= 1
        current_pos = 1
        current_menu = f"Menu {current_level}.{current_pos}"
        display_menu(current_menu)

def on_button2_pressed():
    global current_menu, current_level, current_pos
    if current_pos > 1:
        current_pos -= 1
        current_menu = f"Menu {current_level}.{current_pos}"
        display_menu(current_menu)

def on_button3_pressed():
    global current_menu, current_level, current_pos
    current_pos += 1
    current_menu = f"Menu {current_level}.{current_pos}"
    display_menu(current_menu)

def on_button4_pressed():
    global current_menu, current_level, current_pos
    if current_level < 4:
        current_level += 1
        current_pos = 1
        current_menu = f"Menu {current_level}.{current_pos}"
        display_menu(current_menu)
    if current_level == 4 :
        if current_menu == "Menu 4.1":
            lcd_display_string("LED ON", 2)
            GPIO.output(RLS['LED'], GPIO.HIGH)
            GPIO.output(RLS['RELAY_1'], GPIO.LOW)
            GPIO.output(RLS['RELAY_2'], GPIO.LOW)
        elif current_menu == "Menu 4.2":
            lcd_display_string("RELAY1 ON", 2)
            GPIO.output(RLS['RELAY_1'], GPIO.HIGH)
            GPIO.output(RLS['LED'], GPIO.LOW)
            GPIO.output(RLS['RELAY_2'], GPIO.LOW)
        elif current_menu == "Menu 4.3":
            lcd_display_string("RELAY2 ON", 2)
            GPIO.output(RLS['RELAY_2'], GPIO.HIGH)
            GPIO.output(RLS['LED'], GPIO.LOW)
            GPIO.output(RLS['RELAY_1'], GPIO.LOW)
        
def main():
    lcd_init()
    display_menu(current_menu)
    global current_level
    while True:
        if GPIO.input(BTS["BT1"]) == 0:
            time.sleep(0.5)
            on_button1_pressed()
        elif GPIO.input(BTS["BT2"]) == 0:
            time.sleep(0.5)
            on_button2_pressed()
        elif GPIO.input(BTS["BT3"]) == 0:
            time.sleep(0.5)
            on_button3_pressed()
        elif GPIO.input(BTS["BT4"]) == 0:
            time.sleep(0.5)
            on_button4_pressed()
        if current_level != 4 :
            GPIO.output(RLS['LED'], GPIO.LOW)
            GPIO.output(RLS['RELAY_1'], GPIO.LOW)
            GPIO.output(RLS['RELAY_2'], GPIO.LOW)
            
try:
    main()
except KeyboardInterrupt:
    lcd_clear()
    GPIO.cleanup()
        