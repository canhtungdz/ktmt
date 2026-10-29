# menu chua nhu y muon

import RPi.GPIO as GPIO
import time

# --- GPIO setup ---
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

# LCD pins
LCD_PINS = {'RS': 23, 'E': 27, 'D4': 18, 'D5': 17, 'D6': 14, 'D7': 3, 'BL': 2}

# Buttons
BTS = {"BT_1": 21, "BT_2": 26, "BT_3": 20, "BT_4": 19}

# Output devices
RLS = {"LED": 13, "RELAY_1": 16, "RELAY_2": 12}

for bt in BTS.values():
    GPIO.setup(bt, GPIO.IN, pull_up_down=GPIO.PUD_UP)

for pin in LCD_PINS.values():
    GPIO.setup(pin, GPIO.OUT)

for rl in RLS.values():
    GPIO.setup(rl, GPIO.OUT)
    GPIO.output(rl, False)

LCD_WIDTH = 16
LCD_CHR = True
LCD_CMD = False
LCD_LINE_1 = 0x80
LCD_LINE_2 = 0xC0
E_PULSE = 0.0005
E_DELAY = 0.0005

def pulse_enable():
    GPIO.output(LCD_PINS["E"], False)
    time.sleep(E_PULSE)
    GPIO.output(LCD_PINS['E'], True)
    time.sleep(E_DELAY)
    GPIO.output(LCD_PINS["E"], False)
    time.sleep(E_PULSE)

def send_nibble(nibble):
    GPIO.output(LCD_PINS['D4'], (nibble >> 0) & 1)
    GPIO.output(LCD_PINS['D5'], (nibble >> 1) & 1)
    GPIO.output(LCD_PINS['D6'], (nibble >> 2) & 1)
    GPIO.output(LCD_PINS['D7'], (nibble >> 3) & 1)
    pulse_enable()

def lcd_byte(bits, mode):
    GPIO.output(LCD_PINS['RS'], mode)
    send_nibble(bits >> 4)
    send_nibble(bits & 0x0F)
    time.sleep(0.001)

def lcd_clear():
    lcd_byte(0x01, LCD_CMD)
    time.sleep(0.002)

def lcd_init():
    lcd_byte(0x33, LCD_CMD)
    lcd_byte(0x32, LCD_CMD)
    lcd_byte(0x28, LCD_CMD)
    lcd_byte(0x0C, LCD_CMD)
    lcd_byte(0x06, LCD_CMD)
    lcd_clear()

    # GPIO.output(LCD_PINS['BL'], True)

def lcd_write_line(message, line):
    lcd_byte(LCD_LINE_1 if line==1 else LCD_LINE_2, LCD_CMD)
    for char in message.ljust(LCD_WIDTH):
        lcd_byte(ord(char), LCD_CHR)

menu_structure = {
    "Main Menu": {
        "Menu 1": {
            "Menu 1_1": {
                "LED": lambda: GPIO.output(RLS["LED"], True),
                "RELAY 1": lambda: GPIO.output(RLS["RELAY_1"], True)
            },
            "Menu 1_2": {
                "RELAY 2": lambda: GPIO.output(RLS["RELAY_2"], True)
            }
        },
        "Menu 2": {
            "Menu 2_1": {
                "LED": lambda: GPIO.output(RLS["LED"], False),
                "RELAY 1": lambda: GPIO.output(RLS["RELAY_1"], False)
            },
            "Menu 2_2": {
                "RELAY 2": lambda: GPIO.output(RLS["RELAY_2"], False)
            }
        }
    }
}

def navigate_menu(menu_dict):
    path = [menu_dict]  # stack để quay lại
    keys = list(menu_dict.keys())
    index = 0

    while True:
        # hiển thị menu hiện tại
        lcd_write_line(f"> {keys[index]}", 1)
        lcd_write_line("", 2)

        # đọc nút
        if GPIO.input(BTS["BT_2"]) == 0:  # UP
            index = (index - 1) % len(keys)
            time.sleep(0.2)
        elif GPIO.input(BTS["BT_3"]) == 0:  # DOWN
            index = (index + 1) % len(keys)
            time.sleep(0.2)
        elif GPIO.input(BTS["BT_4"]) == 0:  # SELECT
            selected = keys[index]
            next_menu = path[-1][selected]
            if callable(next_menu):
                next_menu()  # chạy chương trình cấp 4
                lcd_write_line("Executed!", 2)
                time.sleep(1)
            elif isinstance(next_menu, dict):
                path.append(next_menu)
                keys = list(next_menu.keys())
                index = 0
            time.sleep(0.2)
        elif GPIO.input(BTS["BT_1"]) == 0:  # BACK
            if len(path) > 1:
                path.pop()
                keys = list(path[-1].keys())
                index = 0
            time.sleep(0.2)

try:
    lcd_init()
    navigate_menu(menu_structure)
except KeyboardInterrupt:
    lcd_clear()
    GPIO.cleanup()
