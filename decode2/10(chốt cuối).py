import RPi.GPIO as GPIO
import time

# Khai báo chân GPIO
SERVO = 6
buttons = {'BT_1': 21, 'BT_2': 26, 'BT_3': 20}

# Cấu hình LCD
LCD_PINS = {'RS': 23, 'E': 27, 'D4': 18, 'D5': 17, 'D6': 14, 'D7': 3, 'BL': 2}
LCD_WIDTH = 16
LCD_CHR = True
LCD_CMD = False
LCD_LINE_1 = 0x80
LCD_LINE_2 = 0xC0
E_PULSE = 0.0005
E_DELAY = 0.0005

# Thiết lập GPIO
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

# Khởi tạo servo
GPIO.setup(SERVO, GPIO.OUT)
pwm = GPIO.PWM(SERVO, 50)  # Tần số 50Hz cho servo
pwm.start(0)

# Thiết lập các nút bấm
for button in buttons.values():
    GPIO.setup(button, GPIO.IN, pull_up_down=GPIO.PUD_UP)

# Khởi tạo LCD
def lcd_init():
    for pin in LCD_PINS.values():
        GPIO.setup(pin, GPIO.OUT)
    for byte in [0x33, 0x32, 0x28, 0x0C, 0x06, 0x01]:
        lcd_byte(byte, LCD_CMD)

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

def lcd_string(message, line):
    message = message.ljust(LCD_WIDTH, " ")
    lcd_byte(line, LCD_CMD)
    for char in message:
        lcd_byte(ord(char), LCD_CHR)

def lcd_clear():
    lcd_byte(0x01, LCD_CMD)

# Điều khiển servo
def set_servo_angle(angle):
    duty = angle / 18 + 2  # Công thức chuyển đổi góc sang duty cycle
    pwm.ChangeDutyCycle(duty)
    time.sleep(0.5)
    pwm.ChangeDutyCycle(0)  # Dừng xung để tránh servo rung
    
    # Hiển thị góc quay lên LCD
    lcd_clear()
    lcd_string("RC Servo Control", LCD_LINE_1)
    lcd_string(f"Goc quay: {angle}°", LCD_LINE_2)

def main():
    lcd_init()
    lcd_string("RC Servo Control", LCD_LINE_1)
    lcd_string("San sang...", LCD_LINE_2)
    time.sleep(1)
    
    current_angle = 0  # Lưu góc hiện tại
    
    while True:
        if GPIO.input(buttons['BT_1']) == GPIO.LOW:
            current_angle = 20
            set_servo_angle(current_angle)
            time.sleep(0.2)  # Chống dội phím
            
        elif GPIO.input(buttons['BT_2']) == GPIO.LOW:
            current_angle = 60
            set_servo_angle(current_angle)
            time.sleep(0.2)
            
        elif GPIO.input(buttons['BT_3']) == GPIO.LOW:
            current_angle = 160
            set_servo_angle(current_angle)
            time.sleep(0.2)
        
        time.sleep(0.05)

try:
    main()
except KeyboardInterrupt:
    pwm.stop()
    lcd_clear()
    GPIO.cleanup()