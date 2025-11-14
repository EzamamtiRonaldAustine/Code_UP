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
from statistics import median

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
NUM_SAMPLES = 3             # number of readings to average for stability

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


def get_distance():
    """Return distance in cm (rounded). Uses timeouts to avoid blocking indefinitely."""
    GPIO.output(TRIG, True)
    time.sleep(0.00001)
    GPIO.output(TRIG, False)

    # Wait for ECHO to go HIGH
    start_time = time.time()
    timeout = start_time + 0.02
    while GPIO.input(ECHO) == 0:
        if time.time() > timeout:
            return None
        start_time = time.time()

    # Wait for ECHO to go LOW
    end_time = time.time()
    timeout = end_time + 0.02
    while GPIO.input(ECHO) == 1:
        if time.time() > timeout:
            return None
        end_time = time.time()

    duration = end_time - start_time
    
    # Calculate distance
    distance_cm = (duration * 34300) / 2
    
    # Validate reading (HC-SR04 range: 2cm - 400cm)
    if distance_cm > 400 or distance_cm < 2:
        return None
    
    return round(distance_cm, 2)


def get_stable_distance():
    """Take multiple readings and return the median for stability."""
    readings = []
    for _ in range(NUM_SAMPLES):
        dist = get_distance()
        if dist is not None:
            readings.append(dist)
        time.sleep(0.06)  # Small delay between readings (60ms)
    
    if not readings:
        return None
    
    # Return median to filter out outliers
    return round(median(readings), 2)


def save_local(timestamp, distance):
    """Save failed readings to local CSV backup."""
    header_needed = not os.path.exists(BACKUP_FILE)
    with open(BACKUP_FILE, "a", newline="") as f:
        writer = csv.writer(f)
        if header_needed:
            writer.writerow(["timestamp", "distance_cm"])
        writer.writerow([timestamp, distance])


def send_to_thingspeak(distance):
    """Send distance reading to ThingSpeak. Returns True on success."""
    payload = {"api_key": API_KEY, "field1": distance}
    try:
        r = requests.get(THINGSPEAK_URL, params=payload, timeout=10)
        return r.status_code == 200 and r.text.strip().isdigit()
    except requests.RequestException as e:
        print(f"  Error: {e}")
        return False


def flush_backup():
    """Attempt to resend backed-up readings to ThingSpeak."""
    if not os.path.exists(BACKUP_FILE):
        return
    
    rows_to_keep = []
    with open(BACKUP_FILE, "r", newline="") as f:
        reader = csv.reader(f)
        header = next(reader, None)
        for row in reader:
            if len(row) >= 2:
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
            print(f"  Flushed backup: {ts}, {dist} cm")
            time.sleep(1)  # Respect ThingSpeak rate limits

    # Write back only failed entries
    if still_failed:
        with open(BACKUP_FILE, "w", newline="") as f:
            writer = csv.writer(f)
            writer.writerow(["timestamp", "distance_cm"])
            writer.writerows(still_failed)
    else:
        try:
            os.remove(BACKUP_FILE)
            print("  All backup data sent successfully")
        except OSError:
            pass


def control_buzzer(distance):
    """Control buzzer based on distance. Returns current PWM state."""
    global pwm_started
    
    if distance is None:
        # Invalid reading - turn off buzzer
        if pwm_started:
            pwm.stop()
            pwm_started = False
        return pwm_started
    
    # Valid reading - check distance threshold
    if distance < ALERT_DISTANCE_CM:
        if not pwm_started:
            pwm.start(60)  # 60% duty cycle for louder sound
            pwm_started = True
            print(f"  ⚠️  ALERT: Object detected at {distance} cm!")
    else:
        if pwm_started:
            pwm.stop()
            pwm_started = False
    
    return pwm_started


try:
    print("Starting ultrasonic monitor...")
    print(f"Alert distance: {ALERT_DISTANCE_CM} cm")
    print(f"Update interval: {SLEEP_SECONDS} seconds\n")
    
    while True:
        # Get stable distance reading
        distance = get_stable_distance()
        now = time.strftime("%Y-%m-%d %H:%M:%S")
        
        # Display reading
        if distance is not None:
            print(f"{now} | Distance: {distance:6.2f} cm", end="")
        else:
            print(f"{now} | Distance: INVALID", end="")
        
        # Control buzzer based on distance
        control_buzzer(distance)
        
        # Attempt to flush any backed-up readings first
        flush_backup()
        
        # Send current reading to ThingSpeak
        if distance is not None:
            ok = send_to_thingspeak(distance)
            if ok:
                print(" | ✓ Sent to ThingSpeak")
            else:
                print(" | ✗ Failed - saved locally")
                save_local(now, distance)
        else:
            print(" | Skipped (invalid reading)")
        
        time.sleep(SLEEP_SECONDS)

except KeyboardInterrupt:
    print("\n\nStopping...")

finally:
    if pwm_started:
        pwm.stop()
    GPIO.output(BUZZER, False)
    GPIO.cleanup()
    print("Cleanup complete. Goodbye!")