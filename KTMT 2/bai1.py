from multiprocessing import Process, Value
import RPi.GPIO as GPIO
import time

BT1 = 21
BT2 = 26
BT3 = 20
BT4 = 19
LED = 13
LCD = 2

def handle_buttons(step_led, step_lcd):
    while True:
        if GPIO.input(BT1) == GPIO.LOW and GPIO.input(BT3) == GPIO.LOW:
            print("BT1 + BT3 pressed -> Turn OFF LED & LCD")
            GPIO.output(LED, GPIO.LOW)
            GPIO.output(LCD, GPIO.LOW)
            step_led.value = 0
            step_lcd.value = 0
            time.sleep(0.3)
            continue

        if GPIO.input(BT1) == GPIO.LOW:
            print("BT1 pressed")
            step_led.value = 1
            time.sleep(0.2)

        if GPIO.input(BT2) == GPIO.LOW and step_led.value == 1:
            print("BT2 pressed after BT1 -> LED ON")
            GPIO.output(LED, GPIO.HIGH)
            step_led.value = 0
            time.sleep(0.2)

        if GPIO.input(BT3) == GPIO.LOW:
            print("BT3 pressed")
            step_lcd.value = 1
            time.sleep(0.2)

        if GPIO.input(BT4) == GPIO.LOW and step_lcd.value == 1:
            print("BT4 pressed after BT3 -> LCD ON")
            GPIO.output(LCD, GPIO.HIGH)
            step_lcd.value = 0
            time.sleep(0.2)

        time.sleep(0.05)

def main():
    GPIO.setmode(GPIO.BCM)
    GPIO.setwarnings(False)
    GPIO.setup([BT1, BT2, BT3, BT4], GPIO.IN, pull_up_down=GPIO.PUD_UP)
    GPIO.setup([LED, LCD], GPIO.OUT)

    step_led = Value('i', 0)
    step_lcd = Value('i', 0)

    Process(target=handle_buttons, args=(step_led, step_lcd)).start()

try:
    main()
except KeyboardInterrupt:
    GPIO.cleanup()
