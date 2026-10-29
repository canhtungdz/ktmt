import RPi.GPIO as GPIO
import time

# Khai báo chân GPIO
BT1 = 21
BT2 = 26
PWM_PIN = 24
DIR_PIN = 25

# Cấu hình GPIO
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
GPIO.setup(BT1, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(BT2, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(PWM_PIN, GPIO.OUT)
GPIO.setup(DIR_PIN, GPIO.OUT)

# Khởi tạo PWM
pwm = GPIO.PWM(PWM_PIN, 1000)  # Tần số PWM 1kHz
pwm.start(0)

# Hàm điều khiển động cơ
def motor_control(speed, direction):
    GPIO.output(DIR_PIN, direction)
    pwm.ChangeDutyCycle(speed)

def main():
    current_speed = 0
    direction = GPIO.HIGH  # Chiều quay mặc định (có thể thay đổi)
    accelerating = False
    last_time = time.time()
    
    try:
        while True:
            # Xử lý nút bấm 1 (tăng tốc)
            if GPIO.input(BT1) == GPIO.LOW:
                if not accelerating:
                    accelerating = True
                    last_time = time.time()
                    print("Bắt đầu tăng tốc")
                
                # Tăng tốc độ 10% mỗi giây
                if time.time() - last_time >= 1.0:
                    current_speed = min(current_speed + 10, 100)
                    motor_control(current_speed, direction)
                    print(f"Tốc độ hiện tại: {current_speed}%")
                    last_time = time.time()
            else:
                if accelerating:
                    accelerating = False
                    if current_speed > 0:
                        print("Dừng tăng tốc, duy trì tốc độ hiện tại")
            
            # Xử lý nút bấm 2 (dừng khẩn cấp)
            if GPIO.input(BT2) == GPIO.LOW:
                current_speed = 0
                motor_control(current_speed, direction)
                accelerating = False
                print("Dừng khẩn cấp - Động cơ đã dừng")
                time.sleep(0.5)  # Chống nhiễu
            
            time.sleep(0.05)  # Giảm tải CPU
    
    except KeyboardInterrupt:
        print("Dừng chương trình")
    finally:
        pwm.stop()
        GPIO.cleanup()

if __name__ == "__main__":
    main()