import RPi.GPIO as GPIO
import time

# Khai báo chân
LCD_PINS = {'RS': 23, 'E': 27, 'D4': 18, 'D5': 17, 'D6': 14, 'D7': 3, 'BL': 2}
BTS = {"BT_1": 21, "BT_2": 26, "BT_3": 20}
PWM_PIN = 24
DIR_PIN = 25

# Cấu hình LCD
LCD_WIDTH = 16
LCD_CHR = True
LCD_CMD = False
LCD_LINE_1 = 0x80
LCD_LINE_2 = 0xC0
E_PULSE = 0.0005
E_DELAY = 0.0005

# Khởi tạo GPIO
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
GPIO.setup(PWM_PIN, GPIO.OUT)
GPIO.setup(DIR_PIN, GPIO.OUT)

# Khởi tạo PWM với tần số 1kHz
pwm = GPIO.PWM(PWM_PIN, 1000)
pwm.start(0)  # Bắt đầu với duty cycle 0%

# Thiết lập các nút bấm
for pin in BTS.values():
    GPIO.setup(pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)

# Hàm điều khiển LCD
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

def lcd_string(message, line=LCD_LINE_1):
    message = message.ljust(LCD_WIDTH, " ")
    lcd_byte(line, LCD_CMD)
    for char in message:
        lcd_byte(ord(char), LCD_CHR)

def lcd_clear():
    lcd_byte(0x01, LCD_CMD)

# Hàm cập nhật hiển thị LCD
def update_display(direction, speed):
    lcd_clear()
    direction_str = "Forward" if direction else "Reverse"
    lcd_string(f"Dir: {direction_str}", LCD_LINE_1)
    lcd_string(f"Speed: {speed}%", LCD_LINE_2)

# Hàm chính
def main():
    # Khởi tạo LCD
    lcd_init()
    lcd_clear()
    lcd_string("Motor Control", LCD_LINE_1)
    lcd_string("System Ready", LCD_LINE_2)
    time.sleep(2)
    
    # Biến trạng thái
    current_speed = 0
    current_direction = True  # True: forward, False: reverse
    motor_running = False
    emergency_stop = False
    
    try:
        while True:
            # Kiểm tra nút dừng khẩn cấp (BT_2)
            if GPIO.input(BTS["BT_2"]) == GPIO.LOW:
                pwm.ChangeDutyCycle(0)
                motor_running = False
                emergency_stop = True
                current_speed = 0
                update_display(current_direction, current_speed)
                lcd_string("EMERGENCY STOP!", LCD_LINE_1)
                time.sleep(1)  # Chống nhiễu
                while GPIO.input(BTS["BT_2"]) == GPIO.LOW:  # Chờ nhả nút
                    time.sleep(0.1)
                emergency_stop = False
                continue
            
            # Nếu không ở trạng thái dừng khẩn cấp
            if not emergency_stop:
                # Xử lý nút BT_1 (quay thuận)
                if GPIO.input(BTS["BT_1"]) == GPIO.LOW:
                    GPIO.output(DIR_PIN, GPIO.HIGH)  # Chiều thuận
                    current_direction = True
                    motor_running = True
                    
                    # Tăng tốc độ dần 10% mỗi giây
                    while GPIO.input(BTS["BT_1"]) == GPIO.LOW and current_speed < 100:
                        current_speed += 10
                        if current_speed > 100:
                            current_speed = 100
                        pwm.ChangeDutyCycle(current_speed)
                        update_display(current_direction, current_speed)
                        time.sleep(1)  # Tăng tốc mỗi giây
                    
                    # Duy trì tốc độ tối đa nếu vẫn giữ nút
                    while GPIO.input(BTS["BT_1"]) == GPIO.LOW:
                        pwm.ChangeDutyCycle(100)
                        current_speed = 100
                        update_display(current_direction, current_speed)
                        time.sleep(0.1)
                    
                    # Giảm tốc từ từ khi thả nút
                    while current_speed > 0 and motor_running:
                        current_speed -= 1
                        if current_speed < 0:
                            current_speed = 0
                        pwm.ChangeDutyCycle(current_speed)
                        update_display(current_direction, current_speed)
                        time.sleep(0.05)  # Giảm tốc mượt hơn
                    
                    motor_running = False
                
                # Xử lý nút BT_3 (quay ngược)
                elif GPIO.input(BTS["BT_3"]) == GPIO.LOW:
                    GPIO.output(DIR_PIN, GPIO.LOW)  # Chiều ngược
                    current_direction = False
                    motor_running = True
                    
                    # Tăng tốc độ dần 10% mỗi giây
                    while GPIO.input(BTS["BT_3"]) == GPIO.LOW and current_speed < 100:
                        current_speed += 10
                        if current_speed > 100:
                            current_speed = 100
                        pwm.ChangeDutyCycle(current_speed)
                        update_display(current_direction, current_speed)
                        time.sleep(1)  # Tăng tốc mỗi giây
                    
                    # Duy trì tốc độ tối đa nếu vẫn giữ nút
                    while GPIO.input(BTS["BT_3"]) == GPIO.LOW:
                        pwm.ChangeDutyCycle(100)
                        current_speed = 100
                        update_display(current_direction, current_speed)
                        time.sleep(0.1)
                    
                    # Giảm tốc từ từ khi thả nút
                    while current_speed > 0 and motor_running:
                        current_speed -= 1
                        if current_speed < 0:
                            current_speed = 0
                        pwm.ChangeDutyCycle(current_speed)
                        update_display(current_direction, current_speed)
                        time.sleep(0.05)  # Giảm tốc mượt hơn
                    
                    motor_running = False
                
                # Cập nhật hiển thị khi động cơ không hoạt động
                if not motor_running and current_speed == 0:
                    update_display(current_direction, current_speed)
            
            time.sleep(0.05)  # Giảm tải CPU
    
    except KeyboardInterrupt:
        print("Program terminated")
    finally:
        pwm.stop()
        GPIO.cleanup()
        lcd_clear()

if __name__ == "__main__":
    main()