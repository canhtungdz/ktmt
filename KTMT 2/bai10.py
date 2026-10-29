import RPi.GPIO as GPIO
import time


GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

buttons = {'BT_1': 21, 'BT_2': 26, 'BT_3': 20}
for button in buttons.values():
    GPIO.setup(button, GPIO.IN, pull_up_down = GPIO.PUD_UP)

LCD_PINS = {'RS': 23, 'E': 27, 'D4': 18, 'D5': 17, 'D6': 14, 'D7': 3, 'BL': 2}
LCD_WIDTH = 16
LCD_CHR = True
LCD_CMD = False
LCD_LINE_1 = 0x80
LCD_LINE_2 = 0xC0
E_PULSE = 0.0005
E_DELAY = 0.0005
SERVO = 6
GPIO.setup(SERVO, GPIO.OUT)
pwm = GPIO.PWM(SERVO, 50)
pwm.start(0)
def set_servo_angle(angle):
    duty = angle / 18
    pwm.ChangeDutyCycle(duty)
    time.sleep(0.5)
    pwm.ChangeDutyCycle(0)
def lcd_init():
    for pin in LCD_PINS.values():
        GPIO.setup(pin, GPIO.OUT)
    for byte in [0x33, 0x32, 0x28, 0x0C, 0x06, 0x01]:
        lcd_byte(byte, LCD_CMD)
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
    GPIO.output(LCD_PINS['BL'], True)
    while True:
        if GPIO.input(buttons['BT_1']) == GPIO.LOW:
            set_servo_angle(20)
            lcd_clear()
            lcd_display_string('goc quay: 20 *', 1)
        elif GPIO.input(buttons['BT_2']) == GPIO.LOW:
            set_servo_angle(60)
            lcd_clear()
            lcd_display_string('goc quay: 60 *', 1)
        elif GPIO.input(buttons['BT_3']) == GPIO.LOW:
            set_servo_angle(160)
            lcd_clear()
            lcd_display_string('goc quay: 160 *', 1)
        time.sleep(0.1)

try:
    main()
except KeyboardInterrupt:
    pwm.stop()
    GPIO.cleanup()
