import RPi.GPIO as GPIO
import time

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
ledPin = 13
bt4 = 19
GPIO.setup(ledPin, GPIO.OUT)
GPIO.setup(bt4, GPIO.IN, pull_up_down=GPIO.PUD_UP)

def turn_on(pin:int, dur:int):
    GPIO.output(pin, GPIO.HIGH)
    time.sleep(dur)
    GPIO.output(pin, GPIO.LOW)

def turn_on(pin:int):
    GPIO.output(pin, GPIO.HIGH)

def turn_off(pin:int):
    GPIO.output(pin, GPIO.LOW)

try:
    while True:
        if GPIO.input(bt4) == GPIO.LOW:
            turn_on(ledPin)
        else:
            turn_off(ledPin)
except KeyboardInterrupt:
    GPIO.cleanup()