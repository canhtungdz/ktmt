from RPi import GPIO
import time
import numpy as np
import spidev
from PIL import Image, ImageDraw, ImageFont

# bts
BTS = {'BT_1' : 21, 'BT_2' : 26, 'BT_3': 20, 'BT_4' : 19}

def init_BTS():
    for bt in BTS.values():
        GPIO.setup(bt, GPIO.IN, pull_up_down=GPIO.PUD_UP)

# rls
RLS = {"RELAY_1": 16, "RELAY_2": 12, "LED": 13}
def init_RLS():
    for pin in RLS.values():
        GPIO.setup(pin, GPIO.OUT)


# dht11

DHT11_PIN = 7
def init_DHT11():
    # GPIO.output(DHT11_PIN, GPIO.OUT)
    pass

def read_dht11(time_sleep = 0.02):
    GPIO.setup(DHT11_PIN, GPIO.OUT)
    GPIO.output(DHT11_PIN, GPIO.LOW)
    time.sleep(time_sleep)
    GPIO.output(DHT11_PIN, GPIO.HIGH)
    GPIO.setup(DHT11_PIN, GPIO.IN)
    while GPIO.input(DHT11_PIN) == GPIO.LOW:
        pass
    while GPIO.input(DHT11_PIN) == GPIO.HIGH:
        pass

    data = []
    for i in range(40):
        while GPIO.input(DHT11_PIN) == GPIO.LOW:
            pass
        count = 0
        while GPIO.input(DHT11_PIN) == GPIO.HIGH:
            count += 1
            if count > 100:
                break
        if count > 8:
            data.append(1)
        else:
            data.append(0)
    humidity_bit = data[:8]
    humidity_point_bit = data[8:16]
    temperature_bit = data[16:24]
    temperature_point_bit = data[24:32]
    check_bit = data[32:40]
    humidity = 0
    humidity_point = 0
    temperature = 0
    temperature_point = 0
    checksum = 0
    for i in range(8):
        humidity += humidity_bit[i] * 2 ** (7 - i)
        humidity_point += humidity_point_bit[i] * 2 ** (7 - i)
        temperature += temperature_bit[i] * 2 ** (7 - i)
        temperature_point += temperature_point_bit[i] * 2 ** (7 - i)
        checksum += check_bit[i] * 2 ** (7 - i)
    check = humidity + humidity_point + temperature + temperature_point
    if check == checksum:
        return temperature + temperature_point, humidity + humidity_point
    else:
        return None, None


# distance

TRIG = 15
ECHO = 4

def init_distance():
    GPIO.setup(TRIG, GPIO.OUT)
    GPIO.setup(ECHO, GPIO.IN)
    GPIO.output(TRIG, False)

def cal_distance(times_sleep = 1):
    time.sleep(times_sleep)
    GPIO.output(TRIG, True)
    time.sleep(0.001)
    GPIO.output(TRIG, False)
    pulse_start = 0
    pulse_end = 0
    while GPIO.input(ECHO) == 0:
        pulse_start = time.time()
    while GPIO.input(ECHO) == 1:
        pulse_end = time.time()
    pulse_duration = pulse_end - pulse_start
    distance = pulse_duration * 17150
    distance = round(distance, 2)

    return distance

# lcd

LCD_PINS = {'RS': 23, 'E': 27, 'D4': 18, 'D5': 17, 'D6': 14, 'D7': 3, 'BL': 2}
LCD_WIDTH = 16
BT_1 = 21
LCD_CHR = True
LCD_CMD = False
LCD_LINE_1 = 0x80
LCD_LINE_2 = 0xC0
E_PULSE = 0.0005
E_DELAY = 0.0005

def init_LCD():
    for pin in LCD_PINS.values():
        GPIO.setup(pin, GPIO.OUT)
    for byte in [0x33, 0x32, 0x28, 0x0C, 0x06, 0x01]:
        lcd_byte(byte, LCD_CMD)

    GPIO.output(LCD_PINS['BL'], True)

def lcd_clear():
    lcd_byte(0x01, LCD_CMD)

def lcd_byte(bits, mode):
    GPIO.output(LCD_PINS['RS'], mode)
    for bit_num in range(4):
        GPIO.output(LCD_PINS[f'D{bit_num + 4}'],
                    bits & (1 << (bit_num + 4)) != 0)
    time.sleep(E_DELAY)
    GPIO.output(LCD_PINS['E'], True)
    time.sleep(E_PULSE)
    GPIO.output(LCD_PINS['E'], False)
    time.sleep(E_DELAY)

    for bit_num in range(4):
        GPIO.output(LCD_PINS[f'D{bit_num + 4}'],
                    bits & (1 << bit_num) != 0)
    
    time.sleep(E_DELAY)
    GPIO.output(LCD_PINS['E'], True)
    time.sleep(E_PULSE)
    GPIO.output(LCD_PINS['E'], False)
    time.sleep(E_DELAY)

def lcd_display_string(message, line):
    lcd_byte(LCD_LINE_1 if line == 1 else LCD_LINE_2, LCD_CMD)
    for char in message:
        lcd_byte(ord(char), LCD_CHR)


# led matrix
CLK = 11
DIN = 10
CS = 8
spi = None
character = {
    'A': [0x3C, 0x66, 0xC3, 0xC3, 0xFF, 0xC3, 0xC3, 0xC3],
    'B': [0xFC, 0x66, 0x66, 0x7C, 0x66, 0x66, 0x66, 0xFC],
    '0': [0x3C, 0x66, 0xC3, 0xC3, 0xC3, 0xC3, 0x66, 0x3C],
    '1': [0x10, 0x30, 0x10, 0x10, 0x10, 0x10, 0x10, 0x7C],
    '2': [0x3E, 0x63, 0x03, 0x0E, 0x1C, 0x30, 0x63, 0x7F],
    '+': [0x00, 0x18, 0x18, 0x7E, 0x7E, 0x18, 0x18, 0x00],
    '-': [0x00, 0x00, 0x00, 0x7E, 0x7E, 0x00, 0x00, 0x00],
    'x': [0x00, 0xC3, 0x66, 0x3C, 0x3C, 0x66, 0xC3, 0x00],
    '/': [0x03, 0x06, 0x0C, 0x18, 0x30, 0x60, 0xC0, 0x00]
}

def max7219_init():
    max7219_write(0x0C, 0x01)
    max7219_write(0x0B, 0x07)
    max7219_write(0x09, 0x00)
    max7219_write(0x0A, 0x00)
    max7219_write(0x0F, 0x00)

def init_CLK_DIN_CS():
    GPIO.setup(CLK, GPIO.OUT)
    GPIO.setup(DIN, GPIO.OUT)
    GPIO.setup(CS, GPIO.OUT)

def init_led_matrix(max_speed_hz = 10000000, mode = 0b00, init_clk_din_cs = False):
    global spi, CLK, DIN, CS
    spi = spidev.SpiDev()
    spi.open(0, 0)
    spi.max_speed_hz = max_speed_hz
    spi.mode = mode
    init_CLK_DIN_CS() if init_clk_din_cs else ''
    max7219_init()

def spi_send_byte(register, data):
    GPIO.output(CS, GPIO.LOW)

    for bit in range(8):
        GPIO.output(CLK, GPIO.LOW)
        GPIO.output(DIN, (register >> (7 - bit)) & 0x01)
        GPIO.output(CLK, GPIO.HIGH)

    for bit in range(8):
        GPIO.output(CLK, GPIO.LOW)
        GPIO.output(DIN, (data >> (7 - bit)) & 0x01)
        GPIO.output(CLK, GPIO.HIGH)
        
    GPIO.output(CS, GPIO.HIGH)

def clear_display():
    for row in range(1, 9):
        spi_send_byte(row, 0x00)

def display_pattern(character):
    for row in range(8):
        spi_send_byte(row + 1, character[row])

def display_pattern_180(pattern):
    pattern_180 = [int('{:08b}'.format(row)[::-1], 2) for row in pattern[::-1]]

    for row in range(8):
            spi_send_byte(row + 1, pattern_180[row])

def max7219_write(register, data):
    spi.xfer2([register, data])

def create_text_image(text, width, height,
                        mode='1', color=0, font_size=1,
                        text_position = (1, -1), fill=1):
    image = Image.new(mode, (width, height), color)
    draw = ImageDraw.Draw(image)
    font = ImageFont.load_default()
    draw.text(text_position, text, font=font, fill=fill)

    return image

def display_image(image):
    pixels = np.array(image)
    for y in range(8):
        row_data = 0
        for x in range(8):
            if pixels[y, x]:
                row_data |= 1 << x
        max7219_write(y + 1, row_data)

def clear_matrix():
    max7219_write(0x0c, 0x00)

# light ss

LIGHT_SS = 5

def init_LIGHT_SS():
    GPIO.setup(LIGHT_SS, GPIO.IN, pull_up_down=GPIO.PUD_UP)

# motor

PWM_PIN = 24
DIR_PIN = 25
maxSpeed = 100
startMotor = 0
directionMotor = 0
frequencyMotor = 0
pwmMotor = None

def init_motor(frequency = 1000, direction = 0):
    global pwmMotor, frequencyMotor, directionMotor
    GPIO.setup(PWM_PIN, GPIO.OUT)
    GPIO.setup(DIR_PIN, GPIO.OUT)
    frequencyMotor = frequency
    directionMotor = direction
    pwmMotor = GPIO.PWM(PWM_PIN, frequencyMotor)
    pwmMotor.start(startMotor)

def motor_control(speed, direction):
    global pwmMotor, directionMotor
    directionMotor = direction
    GPIO.output(DIR_PIN, direction)
    if direction == 0:
        speed = speed
    else:
        speed = maxSpeed - speed
    pwmMotor.ChangeDutyCycle(speed)

# servo

SERVO = 6
startServo = 0
frequencyServo = 50
pwmServo = None
def init_servo(frequency = frequencyServo, start = startServo):
    global frequencyServo, startServo, pwmServo
    frequencyServo = frequency
    startServo = start
    GPIO.setup(SERVO, GPIO.OUT)
    pwmServo = GPIO.PWM(SERVO, frequency)
    pwmServo.start(start)

def set_servo_angle(angle, time_sleep = 1):
    global pwmServo
    duty = angle / 18
    GPIO.output(SERVO, True)
    pwmServo.ChangeDutyCycle(duty)
    time.sleep(time_sleep)
    GPIO.output(SERVO, False)
    pwmServo.ChangeDutyCycle(0)

# # camera
# import cv2
# from RPi import GPIO
#
# def init():
#     pass

# IR
IR_SS = 22

def init_IR():
    GPIO.setup(IR_SS, GPIO.IN, pull_up_down=GPIO.PUD_UP)

def read_IR(IR_SS):
    while True:
        if not GPIO.input(IR_SS):
            count = 0
            while GPIO.input(IR_SS) == 0 and count < 200:
                count += 1
                time.sleep(0.00006)
            count = 0
            while GPIO.input(IR_SS) == 1 and count < 80:
                count += 1
                time.sleep(0.00006)
            idx = 0
            cnt = 0
            data = [0, 0, 0, 0]
            for i in range(0, 32):
                count = 0
                while GPIO.input(IR_SS) == 0 and count < 15:
                    count += 1
                    time.sleep(0.00006)
                count = 0
                while GPIO.input(IR_SS) == 1 and count < 40:
                    count += 1
                    time.sleep(0.00006)
                if count > 8:
                    data[idx] |= 1 << cnt
                if cnt == 7:
                    cnt = 0
                    idx += 1
                else:
                    cnt += 1
            if data[0] + data[1] == 0xFF and data[2] + data[3] == 0xFF:
                # print('Get the key: 0x%02x' % data[2])
                # print(exec_cmd(data[2]))
                return exec_cmd(data[2])

def exec_cmd(key_val):
    if key_val == 0x45:
        return 'Button: CH-  '
    elif key_val == 0x46:
        return 'Button: CH  '
    elif key_val == 0x47:
        return 'Button: CH+  '
    elif key_val == 0x44:
        return 'Button: PREV '
    elif key_val == 0x40:
        return 'Button: NEXT '
    elif key_val == 0x43:
        return 'Button: P/PA '
    elif key_val == 0x07:
        return 'Button: VOL- '
    elif key_val == 0x15:
        return 'Button: VOL+ '
    elif key_val == 0x09:
        return 'Button: EQ   '
    elif key_val == 0x16:
        return 'Button: 0    '
    elif key_val == 0x19:
        return 'Button: 100+ '
    elif key_val == 0x0d:
        return 'Button: 200+ '
    elif key_val == 0x0c:
        return 'Button: 1    '
    elif key_val == 0x18:
        return 'Button: 2    '
    elif key_val == 0x5e:
        return 'Button: 3    '
    elif key_val == 0x08:
        return 'Button: 4    '
    elif key_val == 0x1c:
        return 'Button: 5    '
    elif key_val == 0x5a:
        return 'Button: 6    '
    elif key_val == 0x42:
        return 'Button: 7    '
    elif key_val == 0x52:
        return 'Button: 8    '
    elif key_val == 0x4a:
        return 'Button: 9'