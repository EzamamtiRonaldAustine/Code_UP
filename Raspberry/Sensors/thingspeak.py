#!/usr/bin/env python3
"""
thingspeak_ultrasonic.py
Read HC-SR04 distance, buzz when too close, send to ThingSpeak, backup locally on failure.
"""

import RPi.GPIO as GPIO
import time
import requests
import csv
import os

# ---------------- ThingSpeak ----------------
THINGSPEAK_URL = "https://api.thingspeak.com/update"
API_KEY = "YOUR_WRITE_API_KEY"   # <-- REPLACE this with your Write API Key

# ---------------- GPIO pins (BCM) ----------------
TRIG = 23
ECHO = 24
BUZZER = 18

# ---------------- Settings ----------------
ALERT_DISTANCE_CM = 10     # buzzer threshold (cm)
SLEEP_SECONDS = 15         # must be >= 15 for free ThingSpeak
BACKUP_FILE = "/home/pi/thingspeak_backup.csv"

# ---------------- Setup ----------------
GPIO.setmode(GPIO.BCM)
GPIO.setup(TRIG, GPIO.OUT)
GPIO.setup(ECHO, GPIO.IN)
GPIO.setup(BUZZER, GPIO.OUT)
GPIO.output(TRIG, False)
GPIO.output(BUZZER, False)
time.sleep(2)


def get_distance():
    """Return distance in cm (rounded). Uses timeouts to avoid blocking indefinitely."""
    # Trigger pulse
    GPIO.output(TRIG, True)
    time.sleep(0.00001)
    GPIO.output(TRIG, False)

    # Wait for echo start
    start_time = time.time()
    timeout = start_time + 0.02  # 20 ms timeout to start
    while GPIO.input(ECHO) == 0 and time.time() < timeout:
        start_time = time.time()

    # Wait for echo end
    end_time = time.time()
    timeout = end_time + 0.02  # 20 ms timeout for end
    while GPIO.input(ECHO) == 1 and time.time() < timeout:
        end_time = time.time()

    duration = end_time - start_time
    if duration <= 0:
        return float('nan')  # no reading
    # speed of sound ~34300 cm/s, divide by 2 for round trip
    distance_cm = (duration * 34300) / 2
    # Ignore unreasonable values
    if distance_cm > 400 or distance_cm <= 0:
        return float('nan')
    return round(distance_cm, 2)


def save_local(timestamp, distance):
    header_needed = not os.path.exists(BACKUP_FILE)
    with open(BACKUP_FILE, "a", newline="") as f:
        writer = csv.writer(f)
        if header_needed:
            writer.writerow(["timestamp", "distance_cm"])
        writer.writerow([timestamp, distance])


def send_to_thingspeak(distance):
    payload = {"api_key": API_KEY, "field1": distance}
    try:
        r = requests.get(THINGSPEAK_URL, params=payload, timeout=10)
        return r.status_code == 200 and r.text.strip().isdigit()
    except requests.RequestException:
        return False


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
    if not rows_to_keep:
        try:
            os.remove(BACKUP_FILE)
        except OSError:
            pass
        return

    still_failed = []
    for row in rows_to_keep:
        ts, dist = row[0], row[1]
        success = send_to_thingspeak(dist)
        if not success:
            still_failed.append(row)
        else:
            time.sleep(1)  # small delay to avoid rate limits

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


try:
    while True:
        distance = get_distance()
        now = time.strftime("%Y-%m-%d %H:%M:%S")
        print(f"{now} Distance: {distance} cm")

        # Local buzzer alert (only if reading is valid)
        if not (distance != distance):  # NaN check: NaN != NaN is True -> invert
            if distance < ALERT_DISTANCE_CM:
                GPIO.output(BUZZER, True)
            else:
                GPIO.output(BUZZER, False)
        else:
            # invalid reading -> turn buzzer off
            GPIO.output(BUZZER, False)

        # Try to send backups first
        flush_backup()

        # Send current reading
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
    GPIO.output(BUZZER, False)
    GPIO.cleanup()
