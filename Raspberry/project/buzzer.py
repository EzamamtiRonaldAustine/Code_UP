import RPi.GPIO as GPIO
import time

BUZZ = 18

GPIO. setmode (GPIO.BCM)
GPIO. setup (BUZZ, GPIO. OUT)

pwm = GPIO. PWM (BUZZ, 440) #440 Hz (A4 tone)




print ("Passive buzzer test")

try:
    while True:
        pwm. start (50)
        time.sleep (0.5)
        pwm. stop ()
        time.sleep (0.5)
except KeyboardInterrupt:
    pwm. stop ()
    GPIO.cleanup ()