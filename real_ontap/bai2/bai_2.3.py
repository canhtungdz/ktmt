import RPi.GPIO as GPIO
import time

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
ledPin = 13
blPin = 2
GPIO.setup(ledPin, GPIO.OUT)
GPIO.setup(blPin, GPIO.OUT)

def turn_on(pin:int, dur:int):
    GPIO.output(pin, GPIO.HIGH)
    time.sleep(dur)
    GPIO.output(pin, GPIO.LOW)
def turn_off(pin:int):
    GPIO.output(pin, GPIO.LOW)


try:
    turn_off(ledPin)
    turn_off(blPin)
    while True:
        turn_on(ledPin, 1)
        # time.sleep(1)
        turn_on(blPin, 1)
except KeyboardInterrupt:
    GPIO.cleanup()