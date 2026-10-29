# Viêt chương trình điêu khiền tôc độ động cơ một chiêu theo kịch bản sau: Ban đâu động cơ đứng yên, nhân nút bám 1 và giữ, động cơ quay theo một chiều bất kỷ với tốc độ tăng dần 10% theo mỗi giây và khi đạt đến tốc độ 100% thì duy trì tốc độ này, khi thả nút bấm 1 thì động cơ sẽ quay theo quán tính và dừng hẳn. Nhấn nút bẩm 3 và giữ, động cơ sẽ quay theo chiêu ngược lại với tốc độ tăng dân 10% theo mỗi giây và khi đạt đên tốc độ 100% thì duy trì tôc độ này, khi thả nút bâm 2 thì động cơ sẽ quay theo quán tính và dừng hăn. Trong quá trình động cơ đang quay, nêu nhấn nút bấm 2 động cơ ngay lập tức dừng lại hẳn. Hiển thị trạng thái của động cơ gồm: chiều quay, tốc độ lên màn hình LCD 16x2

import RPi.GPIO as GPIO
import time

# --- Trang 135 ---
LCD_PINS = {'RS': 23, 'E': 27, 'D4': 18, 
            'D5': 17, 'D6': 14, 'D7': 3, 'BL': 2}
BTS = {"BT_1":21, "BT_2": 26, "BT_3": 20}
PWM_PIN = 24
DIR_PIN = 25
LCD_WIDTH = 16
LCD_CHR = True
LCD_CMD = False
LCD_LINE_1 = 0x80
LCD_LINE_2 = 0xC0
E_PULSE = 0.0005
E_DELAY = 0.0005
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
GPIO.setup(PWM_PIN, GPIO.OUT)
GPIO.setup(DIR_PIN, GPIO.OUT)
pwm = GPIO.PWM(PWM_PIN, 1000)
pwm.start(0)
speed = 0
count = 0
count1 = 0
direction = 0

# --- Trang 135 & 136 ---
def lcd_init():
    for pin in LCD_PINS.values():
        GPIO.setup(pin, GPIO.OUT)
    for byte in [0x33, 0x32, 0x28, 0x0C,
                 0x06, 0x01]:
        lcd_byte(byte, LCD_CMD)

# --- Trang 136 ---
def lcd_clear():
    lcd_byte(0x01, LCD_CMD)

def lcd_byte(bits, mode):
    GPIO.output(LCD_PINS['RS'], mode)
    for bit_num in range(4):
        GPIO.output(LCD_PINS[f'D{bit_num+4}'],
        bits & (1 << (4 + bit_num)) != 0)
    time.sleep(E_DELAY)
    GPIO.output(LCD_PINS['E'], True)
    time.sleep(E_PULSE)
    GPIO.output(LCD_PINS['E'], False)
    time.sleep(E_DELAY)
    for bit_num in range(4):
        GPIO.output(LCD_PINS[f'D{bit_num+4}'],
        bits & (1 << bit_num) != 0)
    time.sleep(E_DELAY)
    GPIO.output(LCD_PINS['E'], True)
    time.sleep(E_PULSE)
    GPIO.output(LCD_PINS['E'], False)
    time.sleep(E_DELAY)

def lcd_display_string(message, line):
    lcd_byte(LCD_LINE_1 if line == 1 else
    LCD_LINE_2, LCD_CMD)
    for char in message:
        lcd_byte(ord(char), LCD_CHR)

def pull_up_bts():
    for pin in BTS.values():
        GPIO.setup(pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)

# --- Trang 137 ---
def motor_control(speed, direction):
    GPIO.output(DIR_PIN, direction)
    if direction == 0:
        speed = speed
    else:
        speed = 100 - speed
    pwm.ChangeDutyCycle(speed)

def button_1_pressed():
    global speed, count
    count += 1
    speed += 10
    if speed >= 100:
        speed = 100
    motor_control(speed, 0)

def button_2_pressed():
    global speed, count1
    count1 += 1
    speed += 10
    if speed >= 100:
        speed = 100
    motor_control(speed, 1)

# --- Trang 137 & 138 ---
def main():
    lcd_init()
    # GPIO.output(2, GPIO.LOW)
    GPIO.output(2, GPIO.HIGH)
    pull_up_bts()
    motor_control(0,0)
    global speed
    while True:
        # Xử lý Nút 1 (Quay tiến)
        if GPIO.input(BTS["BT_1"]) == GPIO.LOW:
            speed = 0
            while True:
                if GPIO.input(BTS["BT_1"]) == GPIO.LOW:
                    button_1_pressed()
                    lcd_display_string("quay tien ", 1)
                    lcd_display_string(f"toc      do: {speed}", 2)
                    time.sleep(0.1)
                else:
                    if speed < 100:
                        # Nhả nút -> Giảm tốc theo quán tính
                        for new_speed in range(speed, -1, -10):
                            motor_control(new_speed, 0)
                            lcd_display_string("giam toc ", 1)
                            lcd_display_string(f"toc      do: {new_speed}   ", 2)
                            time.sleep(0.25)
                            # --- Trang 138 (Cuối) ---
                            if GPIO.input(BTS["BT_3"]) == GPIO.LOW:
                                motor_control(0, 0)
                                lcd_display_string("dung quay    ", 1)
                                lcd_display_string(f"toc do: {0}", 2)
                                break
                        break
                    else:
                        # Đã đạt 100% -> Giữ nguyên tốc độ và kiểm tra BT3
                        motor_control(100, 0)
                        while True:
                            lcd_display_string("quay tien", 1)
                            lcd_display_string(f"toc      do: 100", 2)
                            time.sleep(0.1)
                            # Kiểm tra BT3 để dừng
                            if GPIO.input(BTS["BT_3"]) == GPIO.LOW:
                                motor_control(0, 0)
                                lcd_display_string("dung quay    ", 1)
                                lcd_display_string(f"toc do: {0}   ", 2)
                                speed = 0
                                time.sleep(0.5)
                                break
                            # Kiểm tra BT1 để tăng tốc tiếp (nếu bấm lại)
                            if GPIO.input(BTS["BT_1"]) == GPIO.LOW:
                                break
                    break
        
        # --- Trang 139: Xử lý Nút 2 (Quay lùi) ---
        if GPIO.input(BTS["BT_2"]) == GPIO.LOW:
            speed = 0
            while True:
                if GPIO.input(BTS["BT_2"]) == GPIO.LOW:
                    button_2_pressed()
                    lcd_display_string("quay lui    ", 1)
                    lcd_display_string(f"toc      do: {speed}", 2)
                    time.sleep(0.1)
                elif GPIO.input(BTS["BT_3"]) == GPIO.LOW:
                    motor_control(0, 1)
                    lcd_display_string("dung quay   ", 1)
                    lcd_display_string(f"toc do: {speed}", 2)
                    break
                else:
                    # Nhả nút -> Giảm tốc
                    if speed < 100:
                        for new_speed in range(speed, -1, -10):
                            motor_control(new_speed, 1)
                            lcd_display_string("giam toc  ", 1)
                            lcd_display_string(f"toc      do: {new_speed}   ", 2)
                            time.sleep(0.25)
                            if GPIO.input(BTS["BT_3"]) == GPIO.LOW:
                                motor_control(0, 0)
                                lcd_display_string("dung quay   ", 1)
                                # --- Trang 140 ---
                                lcd_display_string(f"toc      do: {0}   ", 2)
                                break
                        break
                    else:
                        # Đã đạt 100% -> Giữ nguyên tốc độ và kiểm tra BT3
                        motor_control(100, 1)
                        while True:
                            lcd_display_string("quay lui", 1)
                            lcd_display_string(f"toc      do: 100", 2)
                            time.sleep(0.1)
                            # Kiểm tra BT3 để dừng
                            if GPIO.input(BTS["BT_3"]) == GPIO.LOW:
                                motor_control(0, 0)
                                lcd_display_string("dung quay   ", 1)
                                lcd_display_string(f"toc      do: {0}   ", 2)
                                speed = 0
                                time.sleep(0.5)
                                break
                            # Kiểm tra BT2 để tăng tốc tiếp (nếu bấm lại)
                            if GPIO.input(BTS["BT_2"]) == GPIO.LOW:
                                break
                    break
                        

try:
    main()
except KeyboardInterrupt:
    pwm.stop()
    lcd_clear()
    GPIO.cleanup()