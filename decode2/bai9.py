import RPi.GPIO as GPIO
import time

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

BT_1 = 21
BT_2 = 26

GPIO.setup(BT_1, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(BT_2, GPIO.IN, pull_up_down=GPIO.PUD_UP)

LCD_PINS = {'RS': 23, 'E': 27, 'D4': 18, 'D5': 17, 'D6': 14, 'D7': 3, 'BL':2}
LCD_WIDTH = 16
LCD_CHR = True
LCD_CMD = False
LCD_LINE_1 = 0x80
LCD_LINE_2 = 0xC0
E_PULSE = 0.0005
E_DELAY = 0.0005

PWM_PIN = 24
DIR_PIN = 25
GPIO.setup(PWM_PIN, GPIO.OUT)
GPIO.setup(DIR_PIN, GPIO.OUT)
pwm = GPIO.PWM(PWM_PIN, 1000)
pwm.start(0)

speed = 0
direction = 0

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
        GPIO.output(LCD_PINS[f'D{bit_num+4}'], bits & (1 << (4 + bit_num)) != 0)
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

def motor_control(speed, direction):
    GPIO.output(DIR_PIN, direction)
    pwm.ChangeDutyCycle(speed)

def main():
    global speed
    motor_control(0, 0)
    
    while True:
        if GPIO.input(BT_2) == GPIO.LOW:
            speed = 0
            motor_control(speed, direction)
            time.sleep(0.2)
            lcd_clear()
            lcd_display_string("dung quay", 1)
            lcd_display_string(f"toc do: {0}", 2)

        elif GPIO.input(BT_1) == GPIO.LOW:
            if speed < 100:
                speed += 10
                if speed > 100:
                    speed = 100
            motor_control(speed, direction)
            time.sleep(1)
            lcd_clear()
            lcd_display_string("quay tien", 1)
            lcd_display_string(f"toc do: {speed}", 2)

        else:
            if speed > 0:
                speed -= 10
                if speed < 0:
                    speed = 0
                motor_control(speed, direction)
            time.sleep(1)
            if speed == 0:
                lcd_clear()
                lcd_display_string("dung quay", 1)
                lcd_display_string(f"toc do: {0}", 2)
            else:
                lcd_clear()
                lcd_display_string("giam toc", 1)
                lcd_display_string(f"toc do: {speed}", 2)

try:
    main()
except KeyboardInterrupt:
    pwm.stop()
    GPIO.cleanup()