import RPi.GPIO as GPIO
import time
LCD_PINS = {'RS': 23, 'E': 27, 'D4': 18, 'D5': 17, 'D6': 14, 'D7': 3, 'BL': 2}
BT_1 = 21
RELAY_1 = 16
RELAY_2 = 12
PASSWORD = '999'
LCD_WIDTH = 16
LCD_CHR = True
LCD_CMD = False
LCD_LINE_1 = 0x80
LCD_LINE_2 = 0xC0
E_PULSE = 0.0005
E_DELAY = 0.0005


def lcd_init():
    GPIO.setmode(GPIO.BCM)
    GPIO.setwarnings(False)
    GPIO.setup(BT_1, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    GPIO.setup(RELAY_1, GPIO.OUT)
    GPIO.output(RELAY_1, GPIO.LOW)
    GPIO.setup(RELAY_2, GPIO.OUT)
    GPIO.output(RELAY_2, GPIO.LOW)
    for pin in LCD_PINS.values():
        GPIO.setup(pin, GPIO.OUT)
    for byte in [0x33, 0x32, 0x28, 0x0C, 0x06, 0x01]:
        lcd_byte(byte, LCD_CMD)
def lcd_string(message, line = LCD_LINE_1):
    message = message.center(LCD_WIDTH, ' ')
    lcd_byte(line, LCD_CMD)
    for char in message:
        lcd_byte(ord(char), LCD_CHR)
def lcd_clear():
    lcd_byte(0x01, LCD_CMD)
def lcd_byte(bits, mode):
    GPIO.output(LCD_PINS['RS'], mode)
    for bit_num in range(4):
        GPIO.output(LCD_PINS[f'D{bit_num+4}'], bits & (1 << (4 + bit_num)) != 0)
    time.sleep(E_DELAY)
    GPIO.output(LCD_PINS['E'], True)
    time.sleep(E_PULSE)
    GPIO.output(LCD_PINS['E'], False)
    time.sleep(E_DELAY)
    for bit_num in range(4):
        GPIO.output(LCD_PINS[f'D{bit_num+4}'], bits & (1 << bit_num) != 0)
    time.sleep(E_DELAY)
    GPIO.output(LCD_PINS['E'], True)
    time.sleep(E_PULSE)
    GPIO.output(LCD_PINS['E'], False)
    time.sleep(E_DELAY)
def lcd_display_string(message, line):
    lcd_byte(LCD_LINE_1 if line == 1 else LCD_LINE_2, LCD_CMD)
    for char in message:
        lcd_byte(ord(char), LCD_CHR)
def main():
    lcd_init()
    input_password = ''
    GPIO.output(LCD_PINS['BL'], True)
    while True:
        if GPIO.input(BT_1) == GPIO.LOW:
            start = time.time()
            while GPIO.input(BT_1) == GPIO.LOW:
                time.sleep(0.01)
                press_time = time.time() - start
                if press_time >= 0.5:
                    number = 0
                    while GPIO.input(BT_1) == GPIO.LOW:
                        lcd_display_string(str(number), 1)
                        number = (number + 1) % 10
                        time.sleep(0.5)
                    input_password += str((number - 1) % 10)
                    lcd_display_string('*' * len(input_password), 2)
                    if len(input_password) == 3:
                        if input_password == PASSWORD:
                            lcd_display_string('THANH CONG', 1)
                            GPIO.output(RELAY_1, GPIO.HIGH)
                        else:
                            lcd_display_string('CANH BAO', 1)
                            GPIO.output(RELAY_2, GPIO.HIGH)
try:
    main()
except KeyboardInterrupt:
    lcd_clear()
    GPIO.cleanup()