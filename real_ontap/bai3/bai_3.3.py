import RPi.GPIO as GPIO
import time

GPIO.setmode(GPIO.BCM)
GPIO.setwarnings(False)
ledPin = 13
bt1 = 21
bt2 = 26
bt3 = 20
bt4 = 19
GPIO.setup(ledPin, GPIO.OUT)
GPIO.setup(bt1, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(bt2, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(bt3, GPIO.IN, pull_up_down=GPIO.PUD_UP)
GPIO.setup(bt4, GPIO.IN, pull_up_down=GPIO.PUD_UP)


def turn_on_time(pin:int, dur=0):
    GPIO.output(pin, GPIO.HIGH)
    time.sleep(dur)
    GPIO.output(pin, GPIO.LOW)

def turn_on(pin:int):
    GPIO.output(pin, GPIO.HIGH)
    
def turn_off(pin:int):
    GPIO.output(pin, GPIO.LOW)

def turn(pin:int, state):
    GPIO.output(pin, state)

def handle_bt4():
    global state_bt4, led_state
    if GPIO.input(bt4) == GPIO.LOW and GPIO.input(bt4) != state_bt4:
        state_bt4 = GPIO.LOW
        led_state = not led_state
        turn(ledPin, led_state)
        time.sleep(0.25)
    if GPIO.input(bt4) == GPIO.HIGH:
        state_bt4 = GPIO.HIGH
def handle_bt1():
    turn_on(ledPin)
def handle_bt2():
    turn_off(ledPin)
def handle_bt3():
    turn_on_time(ledPin, 1)
    time.sleep(1)

def handle_bt():
    global state
    if GPIO.input(bt1) == GPIO.LOW:
        state = 1
    elif GPIO.input(bt2) == GPIO.LOW:
        state = 2
    elif GPIO.input(bt3) == GPIO.LOW:
        state = 3
    elif GPIO.input(bt4) == GPIO.LOW:
        state = 4
try:
    state = 1
    prev = 1
    state_bt4 = GPIO.HIGH
    led_state = GPIO.LOW

    while True:
        handle_bt()
        if state == 1:
            handle_bt1()

        elif state == 2:
            handle_bt2()

        elif state == 3:
            handle_bt3()

        elif state == 4:
            handle_bt4()
            
        if state != prev:
            print(state)
            prev = state
        

        


except KeyboardInterrupt:
    GPIO.cleanup()
        