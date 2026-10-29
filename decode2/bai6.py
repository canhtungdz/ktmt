#bấm 1 tăng người, bấm 2 giảm người, có người đo nhiệt độ, độ ẩm, điều khiển relay

import RPi.GPIO as GPIO
import time
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)

BTS = {"BT1" : 21, "BT2" : 26}
for bt in BTS.values():
    GPIO.setup(bt, GPIO.IN, pull_up_down=GPIO.PUD_UP)

RLS = {"RELAY_1" : 16, "RELAY_2" : 12}
for rls in RLS.values():
    GPIO.setup(rls, GPIO.OUT)
    GPIO.output(rls, GPIO.LOW)

DHT11_PIN = 7
ROOM_TEMP = 25
ROOM_HUMIDITY = 50

def read_dht11():
	GPIO.setup(DHT11_PIN, GPIO.OUT)
	GPIO.output(DHT11_PIN, GPIO.LOW)
	time.sleep(0.02)
	GPIO.output(DHT11_PIN, GPIO.HIGH)
	GPIO.setup(DHT11_PIN, GPIO.IN)

	while GPIO.input(DHT11_PIN) == GPIO.LOW:
		pass
	while GPIO.input(DHT11_PIN) == GPIO.HIGH:
		pass

	data = []
	for i in range(40):
		while GPIO.input(DHT11_PIN) == GPIO.LOW:
			pass
		count = 0
		while GPIO.input(DHT11_PIN) == GPIO.HIGH:
			count += 1
			if count > 100:
				break
		if count > 8:
			data.append(1)
		else:
			data.append(0)

	humidity_bit = data[0:8]
	humidity_point_bit = data[8:16]
	temperature_bit = data[16:24]
	temperature_point_bit = data[24:32]
	check_bit = data[32:40]

	humidity = 0
	humidity_point = 0
	temperature = 0
	temperature_point = 0
	checksum = 0

	for i in range(8):
		humidity += humidity_bit[i] * 2 ** (7 - i)
		humidity_point += humidity_point_bit[i] * 2 ** (7 - i)
		temperature += temperature_bit[i] * 2 ** (7 - i)
		temperature_point += temperature_point_bit[i] * 2 ** (7 - i)
		checksum += check_bit[i] * 2 ** (7 - i)

	check = humidity + humidity_point + temperature + temperature_point
	if checksum == check:
		return temperature + temperature_point, humidity + humidity_point
	else:
		return None, None

LCD_PINS = {'RS': 23, 'E': 27, 'D4': 18, 'D5': 17, 'D6': 14, 'D7': 3, 'BL':2}
LCD_WIDTH = 16
LCD_CHR = True
LCD_CMD = False
LCD_LINE_1 = 0x80
LCD_LINE_2 = 0xC0
E_PULSE = 0.0005
E_DELAY = 0.0005

def lcd_init():
    for pin in LCD_PINS.values():
        GPIO.setup(pin, GPIO.OUT)
    for byte in [0x33, 0x32, 0x28, 0x0C, 0x06, 0x01]:
        lcd_byte(byte, LCD_CMD)
    GPIO.output(LCD_PINS['BL'], GPIO.HIGH)

def lcd_clear():
    lcd_byte(0x01, LCD_CMD)

def lcd_byte(bits, mode):
    GPIO.output (LCD_PINS['RS'], mode)
    for bit_num in range(4):
        GPIO.output(LCD_PINS[f'D{bit_num + 4}'], bits & (1 << (4 + bit_num)) != 0)
    time.sleep(E_DELAY)
    GPIO.output(LCD_PINS['E'], True)
    time.sleep(E_PULSE)
    GPIO.output(LCD_PINS['E'], False)
    time.sleep(E_DELAY)
    for bit_num in range(4):
        GPIO.output(LCD_PINS[f'D{bit_num + 4}'], bits & (1 << bit_num) != 0)
    time.sleep(E_DELAY)
    GPIO.output(LCD_PINS['E'], True)
    time.sleep(E_PULSE)
    GPIO.output(LCD_PINS['E'], False)
    time.sleep(E_DELAY)

def lcd_display_string(message, line):
    lcd_byte(LCD_LINE_1 if line == 1 else LCD_LINE_2, LCD_CMD)
    for char in message:
        lcd_byte(ord(char), LCD_CHR)

def control_relay(temperature, humidity):
    if temperature < ROOM_TEMP and humidity < ROOM_HUMIDITY:
        GPIO.output(RLS["RELAY_1"], GPIO.HIGH)
        GPIO.output(RLS["RELAY_2"], GPIO.LOW)
    elif temperature > ROOM_TEMP and humidity > ROOM_HUMIDITY:
        GPIO.output(RLS["RELAY_2"], GPIO.HIGH)
        GPIO.output(RLS["RELAY_1"], GPIO.LOW)
    else:
        GPIO.output(RLS["RELAY_1"], GPIO.LOW)
        GPIO.output(RLS["RELAY_2"], GPIO.LOW)

def main():
    lcd_init()
    people_inside = 0
    was_error = False
    last_temp, last_humidity = None, None  
    while True:
        if GPIO.input(BTS["BT1"]) == 0:
            time.sleep(0.5)
            people_inside += 1
            time.sleep(0.5)

        elif GPIO.input(BTS["BT2"]) == 0:
            time.sleep(0.5)
            people_inside -= 1
            if people_inside < 0:
                people_inside = 0

        if people_inside > 0:
            temperature, humidity = read_dht11()
            print(temperature, humidity)
            if humidity is not None and temperature is not None:
                last_temp, last_humidity = temperature, humidity  
                lcd_clear()
                lcd_display_string(' {:.1f}C - {:.1f}%'.format(temperature, humidity), 1)
                lcd_display_string(f"People inside: {people_inside}", 2)
                control_relay(temperature, humidity)
                was_error = False
            else:
                if not was_error and last_temp is None:
                    lcd_clear()
                    lcd_display_string("Sensor Error", 1)
                    lcd_display_string(f"People inside: {people_inside}", 2)
                elif last_temp is not None and not was_error:
                    lcd_clear()
                    lcd_display_string(' {:.1f}C - {:.1f}%'.format(last_temp, last_humidity), 1)
                    lcd_display_string(f"People inside: {people_inside}", 2)
                    control_relay(last_temp, last_humidity)
                was_error = True
        else:
            lcd_clear()
            GPIO.output(RLS['RELAY_1'], GPIO.LOW)
            GPIO.output(RLS['RELAY_2'], GPIO.LOW)
            lcd_display_string(f"People inside: {people_inside}", 2)
        time.sleep(1)

try:
    main()
except KeyboardInterrupt:
    lcd_clear()
    GPIO.cleanup()
        