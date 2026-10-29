# Viết chương trình điều khiền tốc độ động cơ một chiều theo kịch bản sau: Ban đầu động cơ đứng yên, nhấn nút bẩm 1 lần 1 động cơ quay theo một chiều bất kỳ tốc độ 20%, nhấn nút bẩm 1 lần 2 động cơ tăng tốc lên 40%, nhấn nút bấm 1 lần 3 động cơ tăng tốc lên 100%, nhấn nút bấm 1 lần 4 động cơ dừng quay. Tương tự khi nhấn nút bấm 2 theo cùng kịch bản nhưng lúc này động cơ đảo chiều quay:

import RPi.GPIO as GPIO
import time

# --- Trang 130 ---
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

BT_1 = 21
BT_2 = 26
PWM_PIN = 24
DIR_PIN = 25

GPIO.setup(PWM_PIN, GPIO.OUT)
GPIO.setup(DIR_PIN, GPIO.OUT)
GPIO.setup(BT_1, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(BT_2, GPIO.IN, pull_up_down=GPIO.PUD_UP)

pwm = GPIO.PWM(PWM_PIN, 1000)
pwm.start(0)
speed = 0
count = 0
count1 = 0
direction = 0

def motor_control(speed, direction):
    GPIO.output(DIR_PIN, direction)
    
    # --- Trang 131 ---
    if direction == 0:
        speed = speed
    else:
        speed = 100 - speed
    
    pwm.ChangeDutyCycle(speed)

def button_1_pressed():
    global speed, count
    count += 1
    speed += 20
    if count == 4:
        speed = 0
        count = 0
    if speed >= 100:
        speed = 100
    motor_control(speed, 0)

def button_2_pressed():
    global speed, count1
    count1 += 1
    speed += 20
    if count1 == 4:
        speed = 0
        count1 = 0
    if speed >= 100:
        speed = 100
    
    # --- Trang 132 ---
    motor_control(speed, 1)

def main():
    motor_control(0, 0)
    while True:
        if GPIO.input(BT_1) == GPIO.LOW:
            button_1_pressed()
            print(f"so lan bam: {count}")
            time.sleep(0.25)
            
        if GPIO.input(BT_2) == GPIO.LOW:
            button_2_pressed()
            print(f" so lan bam: {count1}")
            time.sleep(0.25)

try:
    main()
except KeyboardInterrupt:
    pwm.stop()
    GPIO.cleanup()