#bấm nút 1 để tăng tốc 20, 40, 100 theo chiều
#bấm nút 2 để tăng tốc 20, 40, 100 theo chiều ngược lại

import RPi.GPIO as GPIO
import time
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

BT_1 = 21
BT_2 = 26
GPIO.setup(BT_1, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(BT_2, GPIO.IN, pull_up_down=GPIO.PUD_UP)

PWM_PIN = 24
DIR_PIN = 25
GPIO.setup(PWM_PIN, GPIO.OUT)
GPIO.setup(DIR_PIN, GPIO.OUT)
pwm = GPIO.PWM(PWM_PIN, 1000)
pwm.start(0)

speed = 0
speed1 = 0
count = 0
count1 = 0
direction = 0

def motor_control(speed, direction):
    GPIO.output(DIR_PIN, direction)
    if direction == 0:
        speed = speed
    else:
        speed = 100 - speed
    pwm.ChangeDutyCycle(speed)

def button1_presssed():
    global speed, count
    count += 1
    speed += 20
    if count == 3:
        speed = 100
    if count == 4:
        count = 0
        speed = 0
    if speed >= 100:
        speed = 100
    
    motor_control(speed, 0)

def button2_presssed():
    global speed1, count1
    count1 += 1
    speed1 += 20
    if count1 == 3:
        speed1 = 100
    if count1 == 4:
        count1 = 0
        speed1 = 0
    if speed1 >= 100:
        speed1 = 100
    motor_control(speed1, 1)

def main():
    motor_control(0, 0)
    while True:
        if GPIO.input(BT_1) == GPIO.LOW:
            button1_presssed()
            print(f"so lan bam nut 1: {count}")
            time.sleep(0.25)
        if GPIO.input(BT_2) == GPIO.LOW:
            button2_presssed()
            print(f"so lan bam nut 2: {count1}")
            time.sleep(0.25)

try:
    main()
except KeyboardInterrupt:
    pwm.stop()
    GPIO.cleanup()
