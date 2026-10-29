import cv2
import numpy as np
import RPi.GPIO as GPIO
import time
import os
import subprocess

# Cấu hình LCD
LCD_PINS = {'RS': 23, 'E': 27, 'D4': 18, 'D5': 17, 'D6': 14, 'D7': 3, 'BL': 2}
BT_1 = 21
BT_2 = 26
RELAY_1 = 16  # Chân điều khiển Relay 1
RELAY_2 = 12   # Chân điều khiển Relay 2
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
GPIO.setup(RELAY_1, GPIO.OUT)
GPIO.setup(RELAY_2, GPIO.OUT)
GPIO.output(RELAY_1, GPIO.LOW)  # Relay OFF (active HIGH - LOW = OFF)
GPIO.output(RELAY_2, GPIO.LOW)  # Relay OFF

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
        # Tạo tên file với timestamp để tránh trùng lặp
        timestamp = time.strftime("%Y%m%d-%H%M%S")
        filename = f"/home/pi/captured_image_{timestamp}.jpg"
        cv2.imwrite(filename, frame)
        return frame, filename
    return None, None

def detect_colors(image):
    # Chuyển ảnh sang HSV
    hsv = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
    
    # Định nghĩa khoảng màu đỏ trong HSV
    lower_red1 = np.array([0, 120, 70])
    upper_red1 = np.array([10, 255, 255])
    lower_red2 = np.array([170, 120, 70])
    upper_red2 = np.array([180, 255, 255])
    
    # Định nghĩa khoảng màu xanh lá cây trong HSV
    lower_green = np.array([35, 50, 50])
    upper_green = np.array([85, 255, 255])
    
    # Tạo mask cho màu đỏ
    mask_red1 = cv2.inRange(hsv, lower_red1, upper_red1)
    mask_red2 = cv2.inRange(hsv, lower_red2, upper_red2)
    red_mask = mask_red1 + mask_red2
    
    # Tạo mask cho màu xanh lá cây
    green_mask = cv2.inRange(hsv, lower_green, upper_green)
    
    # Đếm số pixel
    red_pixels = cv2.countNonZero(red_mask)
    green_pixels = cv2.countNonZero(green_mask)
    
    return red_pixels, green_pixels

def control_relays(red_pixels, green_pixels):
    if red_pixels > green_pixels:
        GPIO.output(RELAY_1, GPIO.HIGH)  # Bật Relay 1 (active HIGH)
        GPIO.output(RELAY_2, GPIO.LOW)   # Tắt Relay 2
        return "RED > GREEN", 1
    else:
        GPIO.output(RELAY_1, GPIO.LOW)   # Tắt Relay 1
        GPIO.output(RELAY_2, GPIO.HIGH)  # Bật Relay 2
        return "GREEN >= RED", 2

def show_image(filename):
    try:
        # Mở ảnh bằng trình xem ảnh mặc định trên Raspberry Pi
        subprocess.run(["xdg-open", filename])
    except Exception as e:
        print(f"Error opening image: {e}")

def main():
    cap = cv2.VideoCapture(0)
    print("Capture is ok")
    lcd_init()
    lcd_clear()
    lcd_display_string("System Ready", 1)
    
    captured_image = None
    last_image_path = None
    
    try:
        while True:
            # Kiểm tra nút BT1 (chụp ảnh)
            if GPIO.input(BT_1) == GPIO.LOW:
                print("Button 1 pressed - Capturing image...")
                captured_image, image_path = capture_image(cap)
                if captured_image is not None:
                    lcd_clear()
                    lcd_display_string("Image captured!", 1)
                    lcd_display_string("Saving...", 2)
                    last_image_path = image_path
                    time.sleep(1)
                    
                    # Hiển thị ảnh vừa chụp
                    lcd_clear()
                    lcd_display_string("Showing image...", 1)
                    show_image(image_path)
                    time.sleep(1)
                else:
                    lcd_clear()
                    lcd_display_string("Capture failed!", 1)
                    time.sleep(1)
            
            # Kiểm tra nút BT2 (đếm pixel và điều khiển relay)
            if GPIO.input(BT_2) == GPIO.LOW and captured_image is not None:
                print("Button 2 pressed - Processing image...")
                red_pixels, green_pixels = detect_colors(captured_image)
                result, relay_state = control_relays(red_pixels, green_pixels)
                
                lcd_clear()
                lcd_display_string(f"R:{red_pixels} G:{green_pixels}", 1)
                lcd_display_string(result, 2)
                
                print(f"Red pixels: {red_pixels}, Green pixels: {green_pixels}")
                print(f"Relay {relay_state} activated")
                time.sleep(0.5)  # Chống nhiễu nút nhấn
            
            time.sleep(0.1)  # Giảm tải CPU
    
    except KeyboardInterrupt:
        print("Program terminated")
    finally:
        cap.release()
        GPIO.output(RELAY_1, GPIO.LOW)  # Tắt Relay khi kết thúc
        GPIO.output(RELAY_2, GPIO.LOW)  # Tắt Relay khi kết thúc
        GPIO.cleanup()
        lcd_clear()

if __name__ == "__main__":
    main()