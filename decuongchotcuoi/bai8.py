# Viêt chương trình điêu khiền tôc độ động cơ một chiêu theo kịch bản sau: Ban đâu động cơ đứng yên, nhân nút bám 1 và giữ, động cơ quay theo một chiều bất kỷ với tốc độ tăng dần 10% theo mỗi giây và khi đạt đến tốc độ 100% thì duy trì tốc độ này, khi thả nút bấm 1 thì động cơ sẽ quay theo quán tính và dừng hẳn. Nhấn nút bẩm 3 và giữ, động cơ sẽ quay theo chiêu ngược lại với tốc độ tăng dân 10% theo mỗi giây và khi đạt đên tốc độ 100% thì duy trì tôc độ này, khi thả nút bâm 2 thì động cơ sẽ quay theo quán tính và dừng hăn. Trong quá trình động cơ đang quay, nêu nhấn nút bấm 2 động cơ ngay lập tức dừng lại hẳn. Hiển thị trạng thái của động cơ gồm: chiều quay, tốc độ lên màn hình LCD 16x2

#giữ để tăng tốc, nhả ra chậm dần, nut 3 dừng lại, áp dụng nút 1,2
# khi nhả thì chậm dần theo quán tính nhưng hơi chậm, cần dừng nhanh hơn.
# hoạt động với nút 1,3; nút 2 để dừng.

import RPi.GPIO as GPIO
import time
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

BTS = {'BT_1': 21, 'BT_2': 26, 'BT_3': 20}
for bt in BTS.values():
    GPIO.setup(bt, GPIO.IN, pull_up_down=GPIO.PUD_UP)

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
    if direction == 0 :
        speed = speed
    else:
        speed = 100 - speed
    pwm.ChangeDutyCycle(speed)

def button1_pressed():
    global speed,direction
    direction = 0
    speed += 10
    if speed >= 100:
        speed = 100
    motor_control(speed, direction)
    lcd_clear()
    lcd_display_string("quay tien", 1)
    lcd_display_string(f"toc do: {speed}", 2)
    time.sleep(1)

def button3_pressed():
    global speed,direction
    direction = 1
    speed += 10
    if speed >= 100:
        speed = 100
    motor_control(speed, direction)
    lcd_clear()
    lcd_display_string("quay lui", 1)
    lcd_display_string(f"toc do: {speed}", 2)
    time.sleep(1)
def button_pressed(BT) :
    global speed, direction
    speed = 0
    while True:
        if GPIO.input(BT) == GPIO.LOW:
            if BT == BTS['BT_1']:
                button1_pressed()
            else:
                button3_pressed()
        else:
            for new_speed in range(speed, -1, -10):
                
                motor_control(new_speed, direction)
                lcd_clear()
                lcd_display_string("giam toc", 1)
                lcd_display_string(f"toc do: {new_speed}", 2)
                time.sleep(1)
                if GPIO.input(BTS['BT_2']) == GPIO.LOW:
                    motor_control(0, 0)
                    lcd_clear()
                    lcd_display_string("dung quay", 1)
                    lcd_display_string(f"toc do: {0}", 2)
                    break
            break

def main():
    lcd_init()
    motor_control(0, 0)
    global speed
    while True:
        if GPIO.input(BTS['BT_1']) == GPIO.LOW:
            button_pressed(BTS['BT_1'])
        if GPIO.input(BTS['BT_3']) == GPIO.LOW:
            button_pressed(BTS['BT_3'])

try:
    main()
except KeyboardInterrupt:
    pwm.stop()
    lcd_clear()
    GPIO.cleanup()
