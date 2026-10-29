import RPi.GPIO as GPIO
import time
GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
ledPin = 13
GPIO.setup(ledPin, GPIO.OUT)
count = 0

def led_on(pin:int, dur:int):
    GPIO.output(pin, GPIO.HIGH)
    time.sleep(dur)
    GPIO.output(pin, GPIO.LOW)

try:
    while  True:
        led_on(ledPin, 1)
        time.sleep(2)
        led_on(ledPin, 3)
        time.sleep(1)
except KeyboardInterrupt:
    GPIO.cleanup()

