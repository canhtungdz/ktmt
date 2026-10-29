import cv2
import numpy as np
import RPi.GPIO as GPIO
import time

# Cấu hình LCD theo cách của bạn
LCD_PINS = {'RS': 23, 'E': 27, 'D4': 18, 'D5': 17, 'D6': 14, 'D7': 3, 'BL': 2}
BT_1 = 21
BT_2 = 26
LCD_WIDTH = 16
LCD_CHR = True
LCD_CMD = False
LCD_LINE_1 = 0x80
LCD_LINE_2 = 0xC0
E_PULSE = 0.0005
E_DELAY = 0.0005

# Khởi tạo GPIO và LCD
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
GPIO.setup(BT_1, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(BT_2, GPIO.IN, pull_up_down=GPIO.PUD_UP)

def lcd_init():
    for pin in LCD_PINS.values():
        GPIO.setup(pin, GPIO.OUT)
    for byte in [0x33, 0x32, 0x28, 0x0C, 0x06, 0x01]:
        lcd_byte(byte, LCD_CMD)

def lcd_string(message, line=LCD_LINE_1):
    message = message.center(LCD_WIDTH, " ")
    lcd_byte(line, LCD_CMD)
    for char in message:
        lcd_byte(ord(char), LCD_CHR)

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

def capture_image(cap):
    ret, frame = cap.read()
    if ret:
        return frame
    return None

def detect_red_pixels(image):
    # Chuyển ảnh sang HSV để dễ dàng phát hiện màu đỏ
    hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
    
    # Định nghĩa khoảng màu đỏ trong HSV
    lower_red1 = np.array([0, 120, 70])
    upper_red1 = np.array([10, 255, 255])
    lower_red2 = np.array([170, 120, 70])
    upper_red2 = np.array([180, 255, 255])
    
    # Tạo mask cho màu đỏ
    mask1 = cv2.inRange(hsv, lower_red1, upper_red1)
    mask2 = cv2.inRange(hsv, lower_red2, upper_red2)
    red_mask = mask1 + mask2
    
    # Đếm số pixel màu đỏ
    red_pixel_count = cv2.countNonZero(red_mask)
    
    return red_pixel_count

def main():
    cap = cv2.VideoCapture(0)
    print("Capture is ok")
    lcd_init()
    lcd_clear()
    lcd_display_string("System Ready", 1)
    
    captured_image = None
    
    try:
        while True:
            # Kiểm tra nút BT1 (chụp ảnh)
            if GPIO.input(BT_1) == GPIO.LOW:
                print("Button 1 pressed - Capturing image...")
                captured_image = capture_image(cap)
                if captured_image is not None:
                    lcd_clear()
                    lcd_display_string("Image captured!", 1)
                    time.sleep(1)
                else:
                    lcd_clear()
                    lcd_display_string("Capture failed!", 1)
                    time.sleep(1)
            
            # Kiểm tra nút BT2 (đếm pixel đỏ)
            if GPIO.input(BT_2) == GPIO.LOW and captured_image is not None:
                print("Button 2 pressed - Counting red pixels...")
                red_pixels = detect_red_pixels(captured_image)
                lcd_clear()
                lcd_display_string("Red pixels:", 1)
                lcd_display_string(str(red_pixels), 2)
                print(f"Red pixels: {red_pixels}")
                time.sleep(0.5)  # Chống nhiễu nút nhấn
            
            time.sleep(0.1)  # Giảm tải CPU
    
    except KeyboardInterrupt:
        print("Program terminated")
    finally:
        cap.release()
        GPIO.cleanup()
        lcd_clear()

if __name__ == "__main__":
    main()