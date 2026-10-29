# Viết chương trình thực hiện chức năng của menu tương tác 4 cấp sử dụng màn hình LCD và các nút bẩm. Nút bẩm 1 đóng vai trò phím quay lại, nút bẩm 2 và 3 đóng vai trò di chuyến lên xuống, nút bẩm 4 đóng vai trò chọn menu.
# Câp 1 là menu chính, cáp 2 chứa các menu 1, menu 2, cp 3 chứa các menu 1_1 và menu 2 2, cấp 4 chứa các chương trình bật LED, bật rơ-le 1 và bật rơ-le 2
import RPi.GPIO as GPIO
import time

# --- Định nghĩa các chân kết nối (Trang 91) ---
LCD_PINS = {'RS': 23, 'E': 27, 'D4': 18, 
            'D5': 17, 'D6': 14, 'D7': 3, 'BL': 2}
BTS = {"BT_1": 21, "BT_2": 26, "BT_3": 20, 
       "BT_4": 19}
RLS = {"RELAY_1": 16, "RELAY_2": 12, 
       "LED": 13}

def pull_up_bts():
    for pin in BTS.values():
        GPIO.setup(pin, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    for pin in RLS.values():
        GPIO.setup(pin, GPIO.OUT)

# --- Các tham số LCD (Trang 91) ---
LCD_WIDTH = 16
LCD_CHR = True
LCD_CMD = False
LCD_LINE_1 = 0x80
LCD_LINE_2 = 0xC0
E_PULSE = 0.0005
E_DELAY = 0.0005
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

# --- Khởi tạo LCD (Trang 92) ---
def lcd_init():
    for pin in LCD_PINS.values():
        GPIO.setup(pin, GPIO.OUT)
    for byte in [0x33, 0x32, 0x28, 0x0C, 0x06, 0x01]:
        lcd_byte(byte, LCD_CMD)

def lcd_clear():
    lcd_byte(0x01, LCD_CMD)

def lcd_byte(bits, mode):
    GPIO.output(LCD_PINS['RS'], mode)
    # Gửi 4 bit cao
    for bit_num in range(4):
        GPIO.output(LCD_PINS[f'D{bit_num+4}'],
                    bits & (1 << (4 + bit_num)) != 0)
    time.sleep(E_DELAY)
    GPIO.output(LCD_PINS['E'], True)
    time.sleep(E_PULSE)
    GPIO.output(LCD_PINS['E'], False)
    time.sleep(E_DELAY)
    # Gửi 4 bit thấp
    for bit_num in range(4):
        GPIO.output(LCD_PINS[f'D{bit_num+4}'],
                    bits & (1 << bit_num) != 0)
    time.sleep(E_DELAY)
    GPIO.output(LCD_PINS['E'], True)
    time.sleep(E_PULSE)
    GPIO.output(LCD_PINS['E'], False)
    time.sleep(E_DELAY)

def lcd_display_string(message, line):
    lcd_byte(LCD_LINE_1 if line == 1 else LCD_LINE_2, LCD_CMD)
    for char in message:
        lcd_byte(ord(char), LCD_CHR)

# --- Xử lý Menu (Trang 93) ---
def display_menu(menu_name):
    lcd_clear()
    lcd_display_string(menu_name, 1)

current_menu = "Main"
current_level = 1
current_pos = 1

def on_button1_pressed():
    """Nút bấm 1: Quay lại (Back)"""
    global current_menu, current_level, current_pos
    if current_level > 1:
        current_level -= 1
        current_pos = 1
        current_menu = f"Menu {current_level}.{current_pos}"
        display_menu(current_menu)

def on_button2_pressed():
    """Nút bấm 2: Di chuyển lên (Up/Previous)"""
    global current_menu, current_level, current_pos
    if current_pos > 1:
        current_pos = current_pos - 1
        current_menu = f"Menu {current_level}.{current_pos}"
        display_menu(current_menu)

def on_button3_pressed():
    """Nút bấm 3: Di chuyển xuống (Down/Next) (Trang 94)"""
    global current_menu, current_level, current_pos
    current_pos = current_pos + 1
    current_menu = f"Menu {current_level}.{current_pos}"
    display_menu(current_menu)

def on_button4_pressed():
    """Nút bấm 4: Chọn menu (Select) (Trang 94)"""
    global current_menu, current_level, current_pos
    if current_level < 4:
        current_level += 1
        current_pos = 1
        current_menu = f"Menu {current_level}.{current_pos}"
        display_menu(current_menu)
    elif current_level == 4:
        if current_menu == "Menu 4.1":
            lcd_display_string("LED On", 2)
            GPIO.output(RLS['LED'], True)
        elif current_menu == "Menu 4.2":
            lcd_display_string("Relay 1 On", 2)
            GPIO.output(RLS['RELAY_1'], True)
        elif current_menu == "Menu 4.3":
            lcd_display_string("Relay 2 On", 2)
            GPIO.output(RLS['RELAY_2'], True)

# --- Chương trình chính (Trang 94 & 95) ---
def main():
    lcd_init()
    pull_up_bts()
    display_menu(current_menu)
    GPIO.output(LCD_PINS['BL'], True)
    
    while True:
        if GPIO.input(BTS["BT_1"]) == GPIO.LOW:
            on_button1_pressed()
            time.sleep(0.25)
        if GPIO.input(BTS["BT_2"]) == GPIO.LOW:
            on_button2_pressed()
            time.sleep(0.25)
        if GPIO.input(BTS["BT_3"]) == GPIO.LOW:
            on_button3_pressed()
            time.sleep(0.25)
        if GPIO.input(BTS["BT_4"]) == GPIO.LOW:
            on_button4_pressed()
            time.sleep(0.25)

if __name__ == "__main__":
    try:
        main()
    except KeyboardInterrupt:
        lcd_clear()
        GPIO.cleanup()