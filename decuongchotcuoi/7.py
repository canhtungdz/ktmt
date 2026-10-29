# Viết chương trình điều khiền tốc độ động cơ một chiều theo kịch bản sau: Ban đầu động cơ đứng yên, nhấn nút bẩm 1 lần 1 động cơ quay theo một chiều bất kỳ tốc độ 20%, nhấn nút bẩm 1 lần 2 động cơ tăng tốc lên 40%, nhấn nút bấm 1 lần 3 động cơ tăng tốc lên 100%, nhấn nút bấm 1 lần 4 động cơ dừng quay. Tương tự khi nhấn nút bấm 2 theo cùng kịch bản nhưng lúc này động cơ đảo chiều quay:
import RPi.GPIO as GPIO 
import time

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

# --- GIỮ NGUYÊN LOGIC CŨ (THEO YÊU CẦU) ---
def motor_control(speed, direction):
    GPIO.output(DIR_PIN, direction)
    if direction == 0:
        speed = speed
    else:
        # Giữ nguyên logic đảo xung cho chiều ngược lại
        speed = 100 - speed 
    pwm.ChangeDutyCycle(speed)

def button_1_pressed():
    global speed, count, count1
    
    # Reset bộ đếm của nút kia để đảm bảo kịch bản chạy đúng từ đầu
    count1 = 0 
    
    count += 1
    
    # SỬA LOGIC TĂNG TỐC: Gán trực tiếp giá trị theo đề bài
    if count == 1:
        speed = 20
    elif count == 2:
        speed = 40
    elif count == 3:
        speed = 100
    elif count >= 4:
        speed = 0
        count = 0
    # if speed >= 100:
    #     speed = 100
    
    # Gọi hàm điều khiển (Chiều 0)
    motor_control(speed, 0)

def button_2_pressed():
    global speed, count1, count
    
    # Reset bộ đếm của nút kia
    count = 0
    
    count1 += 1
    
    # SỬA LOGIC TĂNG TỐC: Gán trực tiếp giá trị theo đề bài
    if count1 == 1:
        speed = 20
    elif count1 == 2:
        speed = 40
    elif count1 == 3:
        speed = 100
    elif count1 >= 4:
        speed = 0
        count1 = 0
    # if speed >= 100:
    #     speed = 100
        
    # Gọi hàm điều khiển (Chiều 1)
    motor_control(speed, 1)

def main():
    motor_control(0, 0)
    while True:
        if GPIO.input(BT_1) == GPIO.LOW:
            button_1_pressed()
            print(f"Nut 1 (Chieu 0) - Lan bam: {count} - Toc do dat: {speed}%")
            time.sleep(0.25)
            
        if GPIO.input(BT_2) == GPIO.LOW:
            button_2_pressed()
            print(f"Nut 2 (Chieu 1) - Lan bam: {count1} - Toc do dat: {speed}%")
            time.sleep(0.25)

try:
    main()

except KeyboardInterrupt:
    pwm.stop()
    GPIO.cleanup()