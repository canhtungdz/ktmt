# 4.Viết chương trình nhập mật khẩu từ các nút bấm, hiển thị lên LCD 16x2 theo kịch bản sau. Khi nhấn nút bấm 1 trong khoảng thời gian 0.55 sẽ 
#     cho các lựa chọn các số từ 0 đến 9, khi nhà nút bầm 1 thì số cuối cùng hiện lên màn hình sẽ là số được lựa chọn. Sau khi lựa chọn, các số hiển 
#     thị trên màn hình sẽ chuyển sang ký tự **** đề bảo mật. Kiểm tra điều kiện nếu mật khẩu nhận được là "999" thì sẽ đóng rơ-le 1 và hiện thông báo
#     "thành công" trên màn hình LCD 16x2 

import RPi.GPIO as GPIO
import time

# Khai báo chân GPIO
BT_1 = 21
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
GPIO.setup(RELAY_PIN, GPIO.OUT)
GPIO.output(RELAY_PIN, GPIO.HIGH)  # Relay OFF ban đầu

# Biến toàn cục
password = ""
display_password = ""
current_number = 0
numbers = [str(i) for i in range(10)]  # Danh sách số 0-9
success = False

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

def update_display():
    lcd_clear()
    lcd_string("Nhap mat khau:", LCD_LINE_1)
    lcd_string(display_password, LCD_LINE_2)

def show_success():
    global success
    lcd_clear()
    lcd_string("THANH CONG!", LCD_LINE_1)
    lcd_string("Relay da dong", LCD_LINE_2)
    GPIO.output(RELAY_PIN, GPIO.LOW)  # Bật relay
    time.sleep(3)
    success = True  # Đánh dấu thành công để thoát chương trình

def check_password():
    if len(password) == 3:  # Khi đủ 3 số
        if password == "999":
            show_success()
        else:
            lcd_clear()
            lcd_string("Mat khau sai!", LCD_LINE_1)
            time.sleep(2)
            reset_password()
        update_display()

def reset_password():
    global password, display_password
    password = ""
    display_password = ""

def main():
    global password, display_password, current_number, success
    
    lcd_init()
    GPIO.output(LCD_PINS['BL'], True)
    update_display()
    
    last_bt1_state = GPIO.HIGH
    
    try:
        while not success:  # Thoát khi nhập đúng mật khẩu
            # Đọc trạng thái nút
            bt1_state = GPIO.input(BT_1)
            
            # Xử lý nút chọn số (BT_1)
            if last_bt1_state == GPIO.HIGH and bt1_state == GPIO.LOW:
                # Bắt đầu giữ nút
                start_time = time.time()
                while GPIO.input(BT_1) == GPIO.LOW and not success:
                    # Hiển thị các số từ 0-9 khi giữ nút
                    elapsed = time.time() - start_time
                    index = int(elapsed * 2) % 10  # Thay đổi số mỗi 0.5s
                    current_number = numbers[index]
                    lcd_string("Chon so: " + current_number, LCD_LINE_2)
                    time.sleep(0.05)
                
                # Khi thả nút, thêm số vào mật khẩu (nếu chưa thành công)
                if not success:
                    password += current_number
                    display_password += "*"
                    update_display()
                    check_password()  # Tự động kiểm tra khi đủ 3 số
            
            last_bt1_state = bt1_state
            time.sleep(0.05)
    
    except KeyboardInterrupt:
        pass
    finally:
        lcd_clear()
        GPIO.output(RELAY_PIN, GPIO.HIGH)  # Đảm bảo relay tắt
        GPIO.cleanup()

if __name__ == "__main__":
    main()