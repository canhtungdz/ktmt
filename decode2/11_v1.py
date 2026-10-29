import RPi.GPIO as GPIO
import time

# Khai báo chân GPIO
SERVO = 6
BT_1 = 21
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
GPIO.setup(SERVO, GPIO.OUT)
GPIO.setup(BT_1, GPIO.IN, pull_up_down=GPIO.PUD_UP)

# Khởi tạo PWM cho servo
pwm = GPIO.PWM(SERVO, 50)  # Tần số 50Hz
pwm.start(0)

# Góc ban đầu
current_angle = 10

# Hàm điều khiển servo
def set_servo_angle(angle):
    duty = angle / 18 + 2  # Công thức chính xác hơn
    pwm.ChangeDutyCycle(duty)
    time.sleep(0.5)
    pwm.ChangeDutyCycle(0)  # Dừng xung để tránh servo rung

# Hàm khởi tạo LCD
def lcd_init():
    for pin in LCD_PINS.values():
        GPIO.setup(pin, GPIO.OUT)
    for byte in [0x33, 0x32, 0x28, 0x0C, 0x06, 0x01]:
        lcd_byte(byte, LCD_CMD)

def lcd_clear():
    lcd_byte(0x01, LCD_CMD)

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

def lcd_display_string(message, line): 
    lcd_byte(LCD_LINE_1 if line == 1 else LCD_LINE_2, LCD_CMD) 
    for char in message: 
        lcd_byte(ord(char), LCD_CHR) 

def update_display(angle):
    lcd_clear()
    lcd_display_string(f"Goc quay: {angle} *", LCD_LINE_1)

def main():
    global current_angle
    
    # Khởi tạo
    lcd_init()
    GPIO.output(LCD_PINS['BL'], True)
    set_servo_angle(current_angle)
    update_display(current_angle)
    
    last_bt_state = GPIO.input(BT_1)
    
    try:
        while True:
            current_bt_state = GPIO.input(BT_1)
            
            # Phát hiện sườn xuống (nút được nhấn)
            if last_bt_state == GPIO.HIGH and current_bt_state == GPIO.LOW:
                current_angle += 10
                
                # Reset về 10° nếu vượt quá 160°
                if current_angle > 160:
                    current_angle = 10
                
                # Cập nhật servo và hiển thị
                set_servo_angle(current_angle)
                update_display(current_angle)
                
                # Chống dội phím
                time.sleep(0.2)
            
            last_bt_state = current_bt_state
            time.sleep(0.05)
    
    except KeyboardInterrupt:
        pwm.stop()
        lcd_clear()
        GPIO.cleanup()

if __name__ == "__main__":
    main()