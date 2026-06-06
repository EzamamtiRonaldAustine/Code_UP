#!/usr/bin/env python3
"""
thingspeak_ultrasonic.py
Read HC-SR04 distance, buzz when too close (louder tone with PWM),
send to ThingSpeak, backup locally on failure.
"""

import RPi.GPIO as GPIO
import time
import requests
import csv
import os

# ---------------- ThingSpeak ----------------
THINGSPEAK_URL = "https://api.thingspeak.com/update"
API_KEY = ""   # <-- REPLACE this with your Write API Key

# ---------------- GPIO pins (BCM) ----------------
TRIG = 23
ECHO = 24
BUZZER = 18

# ---------------- Settings ----------------
ALERT_DISTANCE_CM = 15      # buzzer threshold (cm) — adjust to your setup
SLEEP_SECONDS = 15          # must be >= 15 for free ThingSpeak
BACKUP_FILE = "/home/pi/thingspeak_backup.csv"

# ---------------- Setup ----------------
GPIO.setmode(GPIO.BCM)
GPIO.setup(TRIG, GPIO.OUT)
GPIO.setup(ECHO, GPIO.IN)
GPIO.setup(BUZZER, GPIO.OUT)
GPIO.output(TRIG, False)
GPIO.output(BUZZER, False)
time.sleep(2)

# Create PWM object ONCE — outside the loop
# 2000 Hz = slightly higher pitch and more volume
pwm = GPIO.PWM(BUZZER, 2000)
pwm_started = False

# Returns distance in cm, or NaN on timeout/invalid reading. Uses timeouts to avoid blocking indefinitely.
def get_distance():
    """Return distance in cm (rounded). Uses timeouts to avoid blocking indefinitely."""
    GPIO.output(TRIG, True)
    time.sleep(0.00001)
    GPIO.output(TRIG, False)

    start_time = time.time()
    timeout = start_time + 0.02
    while GPIO.input(ECHO) == 0 and time.time() < timeout:
        start_time = time.time()

    end_time = time.time()
    timeout = end_time + 0.02
    while GPIO.input(ECHO) == 1 and time.time() < timeout:
        end_time = time.time()

    duration = end_time - start_time
    if duration <= 0:
        return float('nan')

    distance_cm = (duration * 34300) / 2
    if distance_cm > 400 or distance_cm <= 0:
        return float('nan')
    return round(distance_cm, 2)

# Save failed entries locally in a CSV file. Each row: timestamp, distance. We can try to resend these later.
def save_local(timestamp, distance):
    header_needed = not os.path.exists(BACKUP_FILE)
    with open(BACKUP_FILE, "a", newline="") as f:
        writer = csv.writer(f)
        if header_needed:
            writer.writerow(["timestamp", "distance_cm"])
        writer.writerow([timestamp, distance])

# Returns True if successful, False on failure (network error or non-200 response)
def send_to_thingspeak(distance):
    payload = {"api_key": API_KEY, "field1": distance}
    try:
        r = requests.get(THINGSPEAK_URL, params=payload, timeout=10)
        return r.status_code == 200 and r.text.strip().isdigit()
    except requests.RequestException:
        return False

# Try to resend any failed entries from the backup file. If all succeed, delete the file.
def flush_backup():
    if not os.path.exists(BACKUP_FILE):
        return
    rows_to_keep = []
    with open(BACKUP_FILE, "r", newline="") as f:
        reader = csv.reader(f)
        header = next(reader, None)
        for row in reader:
            if len(row) < 2:
                continue
            rows_to_keep.append(row)
# If we had no valid rows, just delete the backup file. Otherwise, try to resend each entry. If it still fails, keep it in the backup file for next time.
    if not rows_to_keep:
        try:
            os.remove(BACKUP_FILE)
        except OSError:
            pass
        return
# Try to resend each entry. If it still fails, keep it in the backup file for next time.
    still_failed = []
    for row in rows_to_keep:
        ts, dist = row[0], row[1]
        success = send_to_thingspeak(dist)
        if not success:
            still_failed.append(row)
        else:
            time.sleep(1)
# If we had any entries that still failed, rewrite the backup file with just those. Otherwise, delete the backup file.
    if still_failed:
        with open(BACKUP_FILE, "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["timestamp", "distance_cm"])
            writer.writerows(still_failed)
    else:
        try:
            os.remove(BACKUP_FILE)
        except OSError:
            pass

# ---------------- Main loop ----------------
try:
    while True:
        distance = get_distance()
        now = time.strftime("%Y-%m-%d %H:%M:%S")
        print(f"{now} Distance: {distance} cm")

        # --- Buzzer logic ---
        if not (distance != distance):  # valid reading
            if distance < ALERT_DISTANCE_CM:
                if not pwm_started:
                    pwm.start(60)  # 80% duty cycle for louder sound
                    pwm_started = True
            else:
                if pwm_started:
                    pwm.stop()
                    pwm_started = False
        else:
            if pwm_started:
                pwm.stop()
                pwm_started = False

        # --- ThingSpeak updates ---
        flush_backup()
        ok = send_to_thingspeak(distance if not (distance != distance) else "")
        if ok:
            print("Sent to ThingSpeak")
        else:
            print("Failed to send — saving locally")
            save_local(now, distance)

        time.sleep(SLEEP_SECONDS)

except KeyboardInterrupt:
    print("Stopping...")

finally:
    pwm.stop()
    GPIO.output(BUZZER, False)
    GPIO.cleanup()
