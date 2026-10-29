import RPi.GPIO as GPIO
import time

# Khai báo chân GPIO
BT_1 = 21
BT_2 = 26  # Nút xác nhận
RELAY_PIN = 16
LCD_PINS = {'RS': 23, 'E': 27, 'D4': 18, 'D5': 17, 'D6': 14, 'D7': 3, 'BL': 2}

# Cấu hình LCD
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
GPIO.setup(BT_1, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(BT_2, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(RELAY_PIN, GPIO.OUT)
GPIO.output(RELAY_PIN, GPIO.HIGH)  # Relay OFF ban đầu

# Biến toàn cục
password = ""
display_password = ""
current_number = 0
numbers = [str(i) for i in range(10)]  # Danh sách số 0-9

# Khởi tạo LCD
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
        GPIO.output(LCD_PINS[f'D{bit_num+4}'], bits & (1 << bit_num)) != 0)
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

def update_display():
    lcd_clear()
    lcd_string("Nhap mat khau:", LCD_LINE_1)
    lcd_string(display_password, LCD_LINE_2)

def show_success():
    lcd_clear()
    lcd_string("THANH CONG!", LCD_LINE_1)
    lcd_string("Relay da dong", LCD_LINE_2)
    GPIO.output(RELAY_PIN, GPIO.LOW)  # Bật relay
    time.sleep(3)
    GPIO.output(RELAY_PIN, GPIO.HIGH)  # Tắt relay sau 3 giây

def main():
    global password, display_password, current_number
    
    lcd_init()
    GPIO.output(LCD_PINS['BL'], True)
    update_display()
    
    last_bt1_state = GPIO.HIGH
    last_bt2_state = GPIO.HIGH
    
    try:
        while True:
            # Đọc trạng thái nút
            bt1_state = GPIO.input(BT_1)
            bt2_state = GPIO.input(BT_2)
            
            # Xử lý nút chọn số (BT_1)
            if last_bt1_state == GPIO.HIGH and bt1_state == GPIO.LOW:
                # Bắt đầu giữ nút
                start_time = time.time()
                while GPIO.input(BT_1) == GPIO.LOW:
                    # Hiển thị các số từ 0-9 khi giữ nút
                    elapsed = time.time() - start_time
                    index = int(elapsed * 2) % 10  # Thay đổi số mỗi 0.5s
                    current_number = numbers[index]
                    lcd_string("Chon so: " + current_number, LCD_LINE_2)
                    time.sleep(0.05)
                
                # Khi thả nút, thêm số vào mật khẩu
                password += current_number
                display_password += "*"  # Hiển thị dấu * thay vì số
                update_display()
            
            # Xử lý nút xác nhận (BT_2)
            if last_bt2_state == GPIO.HIGH and bt2_state == GPIO.LOW:
                if len(password) == 3:  # Mật khẩu phải đủ 3 số
                    if password == "999":
                        show_success()
                    else:
                        lcd_clear()
                        lcd_string("Mat khau sai!", LCD_LINE_1)
                        time.sleep(2)
                
                # Reset mật khẩu sau khi kiểm tra
                password = ""
                display_password = ""
                update_display()
                
                time.sleep(0.2)  # Chống dội phím
            
            last_bt1_state = bt1_state
            last_bt2_state = bt2_state
            time.sleep(0.05)
    
    except KeyboardInterrupt:
        lcd_clear()
        GPIO.cleanup()

if __name__ == "__main__":
    main()