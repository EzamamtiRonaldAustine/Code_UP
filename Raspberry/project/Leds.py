import RPi.GPIO as GPIO
import time

GPIO. setmode (GPIO.BCM)

leds = [27, 5,6]
for led in leds:
GPIO.setup (led, GPIO.OUT)

print ("Testing LEDs. . . ")

while True:
    for led in leds:
    GPIO.output (led, 1)
    time.sleep (0.5)
    GPIO.output (led, 0)
    time.sleep (0.5)