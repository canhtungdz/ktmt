import RPi.GPIO as GPIO
import time

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
ledPin = 13
bt4 = 19
GPIO.setup(ledPin, GPIO.OUT)
GPIO.setup(bt4, GPIO.IN, pull_up_down=GPIO.PUD_UP)

def turn_on(pin:int, dur=0):
    GPIO.output(pin, GPIO.HIGH)
    time.sleep(dur)
    GPIO.output(pin, GPIO.LOW)


def turn_off(pin:int):
    GPIO.output(pin, GPIO.LOW)

def turn(pin:int, state):
    GPIO.output(pin, state)

try:
    state = GPIO.LOW
    state_bt4 = GPIO.HIGH
    while True:
        if GPIO.input(bt4) == GPIO.LOW and GPIO.input(bt4) != state_bt4:
            state_bt4 = GPIO.LOW
            state = not state
            turn(ledPin, state)
            time.sleep(0.25)
        if GPIO.input(bt4) == GPIO.HIGH:
            state_bt4 = GPIO.HIGH


except KeyboardInterrupt:
    GPIO.cleanup()
        