import RPi.GPIO as GPIO 
import time 
SERVO = 6 
buttons = {'BT_1': 21, 'BT_2': 26, 'BT_3': 20}
GPIO.setmode(GPIO.BCM) 
GPIO.setup(SERVO, GPIO.OUT) 
for button in buttons.values():
 GPIO.setup(button, GPIO.IN, pull_up_down=GPIO.PUD_UP) 
pwm = GPIO.PWM(SERVO, 50) 
pwm.start(0) 
def set_servo_angle(angle): 
 duty = angle / 18 
 pwm.ChangeDutyCycle(duty) 
 time.sleep(0.5) 
 pwm.ChangeDutyCycle(0) 
def main(): 
 while True: 
  if GPIO.input (buttons['BT_1']) == GPIO.LOW: 
   set_servo_angle(20) 
  elif GPIO.input(buttons['BT_2']) == GPIO.LOW: 
   set_servo_angle(60) 
  elif GPIO.input(buttons['BT_3']) == GPIO.LOW: 
   set_servo_angle(160) 
  time.sleep(0.1) 
try: 
 main() 
except KeyboardInterrupt:  
 pwm.stop() 
 GPIO.cleanup()