# 1.Viết chương trình theo kịch bản sau, nhấn lần lượt theo thứ tự nút bấm 1, nút bấm 2 thì LED sáng, nhấn lần lượt theo thứ tự nút bấm 3, nút 
#     bấm 4 thì đèn nền LCD sáng, nhấn giữ đồng thời nút bầm 1 và nút bấm 3 thì cả hai LED và đến nền LCD tắt 
# da test ok

import RPi.GPIO as GPIO
import time

# Thiết lập các chân GPIO
BT_1 = 21
BT_2 = 26
BT_3 = 20
BT_4 = 19
LED = 13

LCD_PINS = {'RS': 23, 'E': 27, 'D4': 18, 'D5': 17, 'D6': 14, 'D7': 3, 'BL': 2}
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

# Thiết lập các nút bấm
GPIO.setup(BT_1, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(BT_2, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(BT_3, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(BT_4, GPIO.IN, pull_up_down=GPIO.PUD_UP)

# Thiết lập LED
GPIO.setup(LED, GPIO.OUT)
GPIO.output(LED, GPIO.LOW)

# Thiết lập LCD
def lcd_init():
    for pin in LCD_PINS.values():
        GPIO.setup(pin, GPIO.OUT)
    lcd_byte(0x33, LCD_CMD)
    lcd_byte(0x32, LCD_CMD)
    lcd_byte(0x28, LCD_CMD)
    lcd_byte(0x0C, LCD_CMD)
    lcd_byte(0x06, LCD_CMD)
    lcd_byte(0x01, LCD_CMD)
    time.sleep(E_DELAY)

def lcd_byte(bits, mode):
    GPIO.output(LCD_PINS['RS'], mode)
    
    # High bits
    GPIO.output(LCD_PINS['D4'], GPIO.LOW)
    GPIO.output(LCD_PINS['D5'], GPIO.LOW)
    GPIO.output(LCD_PINS['D6'], GPIO.LOW)
    GPIO.output(LCD_PINS['D7'], GPIO.LOW)
    if bits & 0x10 == 0x10:
        GPIO.output(LCD_PINS['D4'], GPIO.HIGH)
    if bits & 0x20 == 0x20:
        GPIO.output(LCD_PINS['D5'], GPIO.HIGH)
    if bits & 0x40 == 0x40:
        GPIO.output(LCD_PINS['D6'], GPIO.HIGH)
    if bits & 0x80 == 0x80:
        GPIO.output(LCD_PINS['D7'], GPIO.HIGH)
    
    # Toggle 'Enable' pin
    time.sleep(E_DELAY)
    GPIO.output(LCD_PINS['E'], GPIO.HIGH)
    time.sleep(E_PULSE)
    GPIO.output(LCD_PINS['E'], GPIO.LOW)
    time.sleep(E_DELAY)
    
    # Low bits
    GPIO.output(LCD_PINS['D4'], GPIO.LOW)
    GPIO.output(LCD_PINS['D5'], GPIO.LOW)
    GPIO.output(LCD_PINS['D6'], GPIO.LOW)
    GPIO.output(LCD_PINS['D7'], GPIO.LOW)
    if bits & 0x01 == 0x01:
        GPIO.output(LCD_PINS['D4'], GPIO.HIGH)
    if bits & 0x02 == 0x02:
        GPIO.output(LCD_PINS['D5'], GPIO.HIGH)
    if bits & 0x04 == 0x04:
        GPIO.output(LCD_PINS['D6'], GPIO.HIGH)
    if bits & 0x08 == 0x08:
        GPIO.output(LCD_PINS['D7'], GPIO.HIGH)
    
    # Toggle 'Enable' pin
    time.sleep(E_DELAY)
    GPIO.output(LCD_PINS['E'], GPIO.HIGH)
    time.sleep(E_PULSE)
    GPIO.output(LCD_PINS['E'], GPIO.LOW)
    time.sleep(E_DELAY)

def lcd_toggle_backlight(state):
    GPIO.output(LCD_PINS['BL'], state)

def lcd_string(message, line):
    message = message.ljust(LCD_WIDTH, " ")
    lcd_byte(line, LCD_CMD)
    for i in range(LCD_WIDTH):
        lcd_byte(ord(message[i]), LCD_CHR)

# Khởi tạo LCD
lcd_init()
lcd_toggle_backlight(False)
lcd_string("System Ready", LCD_LINE_1)

# Biến trạng thái
led_state = False
backlight_state = False
button_sequence = []

try:
    while True:
        # Đọc trạng thái các nút bấm
        bt1_state = not GPIO.input(BT_1)
        bt2_state = not GPIO.input(BT_2)
        bt3_state = not GPIO.input(BT_3)
        bt4_state = not GPIO.input(BT_4)
        
        # Kiểm tra nhấn giữ đồng thời BT1 và BT3
        if bt1_state and bt3_state:
            led_state = False
            backlight_state = False
            GPIO.output(LED, GPIO.LOW)
            lcd_toggle_backlight(False)
            lcd_string("Both OFF", LCD_LINE_2)
            button_sequence = []
            time.sleep(0.5)  # Chống dội
            continue
        
        # Kiểm tra thứ tự nút bấm cho LED
        if bt1_state and len(button_sequence) == 0:
            button_sequence.append(1)
            time.sleep(0.2)  # Chống dội
        elif bt2_state and len(button_sequence) == 1 and button_sequence[0] == 1:
            led_state = not led_state
            GPIO.output(LED, led_state)
            lcd_string(f"LED: {'ON' if led_state else 'OFF'}", LCD_LINE_2)
            button_sequence = []
            time.sleep(0.2)  # Chống dội
        
        # Kiểm tra thứ tự nút bấm cho đèn nền LCD
        if bt3_state and len(button_sequence) == 0:
            button_sequence.append(3)
            time.sleep(0.2)  # Chống dội
        elif bt4_state and len(button_sequence) == 1 and button_sequence[0] == 3:
            backlight_state = not backlight_state
            lcd_toggle_backlight(backlight_state)
            lcd_string(f"LCD BL: {'ON' if backlight_state else 'OFF'}", LCD_LINE_2)
            button_sequence = []
            time.sleep(0.2)  # Chống dội
        
        # Reset sequence nếu nhấn sai
        if (bt2_state and len(button_sequence) > 0 and button_sequence[0] != 1) or \
           (bt4_state and len(button_sequence) > 0 and button_sequence[0] != 3):
            button_sequence = []
            lcd_string("Wrong sequence", LCD_LINE_2)
            time.sleep(0.5)
            lcd_string("", LCD_LINE_2)
        
        time.sleep(0.05)

except KeyboardInterrupt:
    GPIO.cleanup()