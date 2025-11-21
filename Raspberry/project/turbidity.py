import RPi.GPIO as GPIO
import time

GPIO.setmode(GPIO.BCM)
TURBIDITY_PIN = 17

GPIO.setup(TURBIDITY_PIN, GPIO.IN)

print("Turbidity Sensor Test (Digital) ...")

while True:
    value = GPIO.input(TURBIDITY_PIN)
    if value == 0:
        print("Water is TURBID / DIRTY")
    else:
        print("Water is CLEAR")
    time.sleep(1)
