import cv2
import RPi.GPIO as GPIO
import time
import numpy as np

# --- Cấu hình GPIO và LCD ---
BT1 = 21  # Button 1 (Chụp ảnh)
BT2 = 26  # Button 2 (Xử lý ảnh và hiện vật đỏ)
LCD_PINS = {'RS': 23, 'E': 27, 'D4': 18, 'D5': 17, 'D6': 14, 'D7': 3, 'BL': 2}
LCD_WIDTH = 16
LCD_CHR = True
LCD_CMD = False
LCD_LINE_1 = 0x80
LCD_LINE_2 = 0xC0
E_PULSE = 0.0005
E_DELAY = 0.0005

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

# --- Các hàm điều khiển LCD ---
def lcd_init():
    for pin in LCD_PINS.values():
        GPIO.setup(pin, GPIO.OUT)
    lcd_byte(0x33, LCD_CMD)
    lcd_byte(0x32, LCD_CMD)
    lcd_byte(0x28, LCD_CMD)
    lcd_byte(0x0C, LCD_CMD)
    lcd_byte(0x06, LCD_CMD)
    lcd_byte(0x01, LCD_CMD)

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
    # Căn giữa text cho đẹp
    message = message.ljust(LCD_WIDTH, " ")
    for char in message:
        lcd_byte(ord(char), LCD_CHR)

# --- Hàm chụp ảnh ---
def capture_image():
    capture = cv2.VideoCapture(0)
    # Đợi một chút để camera khởi động và cân bằng sáng
    time.sleep(0.5) 
    ret, frame = capture.read()
    capture.release()
    if ret:
        cv2.imshow("Anh chup camera (Goc)", frame)
        cv2.waitKey(2000)  # Hiện ảnh gốc 2 giây
        # cv2.destroyWindow("Anh chup camera (Goc)") # Đóng cửa sổ này lại
    return frame if ret else None

# --- Hàm xử lý ảnh: Đếm và Lấy ảnh vật đỏ ---
def process_red_objects(image):
    hsv_image = cv2.cvtColor(image, cv2.COLOR_BGR2HSV)
    

    lower_red1 = np.array([0, 120, 70])
    upper_red1 = np.array([10, 255, 255])
    lower_red2 = np.array([170, 120, 70])
    upper_red2 = np.array([180, 255, 255])


    # lower_red1 = np.array([0, 150, 150])
    # upper_red1 = np.array([10, 255, 255])
    # lower_red2 = np.array([170, 150, 150])
    # upper_red2 = np.array([180, 255, 255])
    
    # lower_red1 = np.array([0, 50, 50])
    # upper_red1 = np.array([15, 255, 255])
    # lower_red2 = np.array([165, 50, 50])
    # upper_red2 = np.array([180, 255, 255])


    # Tạo mask
    mask1 = cv2.inRange(hsv_image, lower_red1, upper_red1)
    mask2 = cv2.inRange(hsv_image, lower_red2, upper_red2)
    red_mask = mask1 + mask2
    
    # 1. Đếm số điểm ảnh
    red_pixel_count = cv2.countNonZero(red_mask)
    
    # 2. Tạo ảnh kết quả (Chỉ giữ lại phần màu đỏ, phần còn lại màu đen)
    # bitwise_and giúp cắt ảnh gốc dựa theo mask
    result_image = cv2.bitwise_and(image, image, mask=red_mask)
    
    # return red_pixel_count, result_image
    return red_pixel_count, red_mask


# --- Chương trình chính ---
def main():
    GPIO.setup(BT1, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    GPIO.setup(BT2, GPIO.IN, pull_up_down=GPIO.PUD_UP)
    lcd_init()
    lcd_clear()
    lcd_display_string("System Ready", 1)
    
    captured_image = None # Biến lưu ảnh đã chụp

    try:
        while True:
            # --- BUTTON 1: CHỤP ẢNH ---
            if GPIO.input(BT1) == GPIO.LOW:
                lcd_clear()
                lcd_display_string("Capturing...", 1)
                print("Dang chup anh...")
                
                captured_image = capture_image()
                
                if captured_image is not None:
                    lcd_clear()
                    lcd_display_string("Image Captured!", 1)
                    print("Da chup xong.")
                else:
                    lcd_clear()
                    lcd_display_string("Capture Failed!", 1)
                    print("Loi camera.")
                
                # Chống dội phím (debounce) thủ công
                while GPIO.input(BT1) == GPIO.LOW: time.sleep(0.1)

            # --- BUTTON 2: XỬ LÝ VÀ HIỆN ẢNH ĐỎ ---
            if GPIO.input(BT2) == GPIO.LOW:
                if captured_image is not None:
                    lcd_clear()
                    lcd_display_string("Processing...", 1)
                    print("Dang xu ly...")
                    
                    # Gọi hàm xử lý, nhận về cả số lượng VÀ ảnh kết quả
                    red_pixel_count, red_object_img = process_red_objects(captured_image)
                    
                    # Hiển thị thông tin lên LCD
                    lcd_clear()
                    lcd_display_string("Red Pixels:", 1)
                    lcd_display_string(str(red_pixel_count), 2)
                    print(f"Red Pixels: {red_pixel_count}")
                    
                    # --- HIỂN THỊ ẢNH VẬT ĐỎ LÊN MÀN HÌNH ---
                    cv2.imshow("Cac vat the mau do", red_object_img)
                    
                    # Giữ ảnh trong 3 giây (3000ms) rồi tự tắt
                    # Trong thời gian này LCD vẫn hiện kết quả
                    # cv2.waitKey() 
                    # cv2.destroyAllWindows()
                    
                    # Quay về trạng thái chờ
                    lcd_clear()
                    lcd_display_string("System Ready", 1)
                else:
                    lcd_clear()
                    lcd_display_string("No Image!", 1)
                    lcd_display_string("Press BT1 first", 2)
                    time.sleep(2)
                    lcd_clear()
                    lcd_display_string("System Ready", 1)

                # Chống dội phím
                while GPIO.input(BT2) == GPIO.LOW: time.sleep(0.1)

            time.sleep(0.1)

    except KeyboardInterrupt:
        lcd_clear()
        GPIO.cleanup()
        cv2.destroyAllWindows()
        print("System exited.")

if __name__ == "__main__":
    main()