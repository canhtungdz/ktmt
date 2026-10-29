import RPi.GPIO as GPIO
import time

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

CLK = 11 #clock
DIN = 10 #MOSI
CS = 8 #chip select
GPIO.setup(CLK, GPIO.OUT)
GPIO.setup(DIN, GPIO.OUT)
GPIO.setup(CS, GPIO.OUT)

BT1 = 21
GPIO.setup(BT1, GPIO.IN, pull_up_down=GPIO.PUD_UP)

heart = [
    0b00010000,
    0b00111000,
    0b00111100,
    0b01111110,
    0b11111111,
    0b11111111,
    0b11111111,
    0b01100110
]

def spi_send_byte(register, data):
    GPIO.output(CS, GPIO.LOW)
    for bit in range(8):
        GPIO.output(CLK, GPIO.LOW)
        GPIO.output(DIN, (register >> (7 - bit)) & 1) #MSB
        GPIO.output(CLK, GPIO.HIGH)
    for bit in range(8):
        GPIO.output(CLK, GPIO.LOW)
        GPIO.output(DIN, (data >> (7 - bit)) & 1)
        GPIO.output(CLK, GPIO.HIGH)
    GPIO.output(CS, GPIO.HIGH)


def max7219_init():
    spi_send_byte(0x09, 0x00) # tat chế độ decode
    spi_send_byte(0x0A, 0x08) # độ sáng
    spi_send_byte(0x0B, 0x07) # quét 8 hàng
    spi_send_byte(0x0C, 0x01)  # cho phép hiển thị
    spi_send_byte(0x0F, 0x00)  # tắt display test

def display_pattern(pattern):
    for row in range(8):
        spi_send_byte(row + 1, pattern[row])

def clear_display():
    for row in range(1, 9):
        spi_send_byte(row, 0x00)

def main():
    max7219_init()
    display_pattern(heart)
    blinking = False

    while True:
        if GPIO.input(BT1) == 0:
            blinking  = True
            time.sleep(0.3)  

        if blinking:
            display_pattern(heart)
            time.sleep(1)
            clear_display()
            time.sleep(1)

try:
    main()
except KeyboardInterrupt:
    clear_display()
    GPIO.cleanup()
