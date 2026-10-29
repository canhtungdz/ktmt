import spidev
import time
import numpy as np
import RPi.GPIO as GPIO

# Thiết lập GPIO
GPIO.setmode(GPIO.BCM)
BT_1 = 21
GPIO.setup(BT_1, GPIO.IN, pull_up_down=GPIO.PUD_UP)

# Thiết lập SPI
spi = spidev.SpiDev()
spi.open(0, 0)
spi.max_speed_hz = 10000000
spi.mode = 0b00

# Khởi tạo MAX7219
def max7219_write(register, data):
    spi.xfer2([register, data])

def max7219_init():
    max7219_write(0x0C, 0x01)  # Bật chế độ hoạt động
    max7219_write(0x0B, 0x07)  # Quét tất cả 8 chữ số
    max7219_write(0x09, 0x00)  # Giải mã không
    max7219_write(0x0A, 0x00)  # Độ sáng
    max7219_write(0x0F, 0x00)  # Tắt chế độ test

# Hình trái tim
heart = [
    0b01100110,
    0b11111111,
    0b11111111,
    0b11111111,
    0b01111110,
    0b00111100,
    0b00011000,
    0b00000000
]

# Hiển thị hình ảnh lên LED matrix
def display_pattern(pattern):
    for row in range(8):
        max7219_write(row + 1, pattern[row])

# Biến trạng thái
blinking = False
last_state = True
current_state = True

# Khởi tạo MAX7219
max7219_init()

try:
    while True:
        # Đọc trạng thái nút nhấn
        current_state = GPIO.input(BT_1)
        
        # Phát hiện sườn xuống (khi nút được nhấn)
        if last_state == True and current_state == False:
            blinking = not blinking  # Đảo trạng thái nhấp nháy
            if not blinking:
                display_pattern([0] * 8)  # Tắt toàn bộ LED khi dừng nhấp nháy
        
        last_state = current_state
        
        if blinking:
            # Hiển thị hình trái tim
            display_pattern(heart)
            time.sleep(0.5)
            # Tắt toàn bộ LED
            display_pattern([0] * 8)
            time.sleep(0.5)
        
        time.sleep(0.05)  # Chống dội phím

except KeyboardInterrupt:
    # Dọn dẹp khi thoát chương trình
    spi.close()
    GPIO.cleanup()