from flask import Flask, render_template, jsonify, request

import RPi.GPIO as GPIO

import time

import threading

# -------------------------------

# Hardware Pin Setup

# -------------------------------

TRIG = 23

ECHO = 24

BUZZER = 18  # GPIO 18 supports hardware PWM

GPIO.setmode(GPIO.BCM)

GPIO.setup(TRIG, GPIO.OUT)

GPIO.setup(ECHO, GPIO.IN)

GPIO.setup(BUZZER, GPIO.OUT)

# Setup PWM on buzzer pin

buzzer_pwm = GPIO.PWM(BUZZER, 2000)  # 2000 Hz frequency

buzzer_pwm.start(0)  # Start with 0% duty cycle (OFF)

# Global variables

buzzer_auto_mode = False

safe_distance_threshold = 6  # cm

auto_control_active = False

# -------------------------------

# Flask App

# -------------------------------

app = Flask(__name__)

# Function to measure distance

def get_distance():

    GPIO.output(TRIG, False)

    time.sleep(0.05)

    GPIO.output(TRIG, True)

    time.sleep(0.00001)

    GPIO.output(TRIG, False)

    pulse_start = time.time()

    pulse_end = time.time()

    timeout = time.time() + 0.1  # 100ms timeout
    while GPIO.input(ECHO) == 0 and time.time() < timeout:
        pulse_start = time.time()

    while GPIO.input(ECHO) == 1 and time.time() < timeout:
        pulse_end = time.time()

    pulse_duration = pulse_end - pulse_start
    distance = round(pulse_duration * 17150, 2)
    return distance

def auto_buzzer_control():
    """Control buzzer automatically based on distance"""
    global auto_control_active
    auto_control_active = True
    print("Auto buzzer control started")

    while buzzer_auto_mode and auto_control_active:
        try:
            dist = get_distance()
            is_safe = dist > safe_distance_threshold

            if is_safe:
                # Safe distance - turn buzzer off
                buzzer_pwm.ChangeDutyCycle(0)
                print(f"Distance: {dist}cm - SAFE - Buzzer OFF")
            else:
                # Not safe distance - turn buzzer on
                buzzer_pwm.ChangeDutyCycle(50)
                print(f"Distance: {dist}cm - NOT SAFE - Buzzer ON")

            time.sleep(0.2)  # Check distance every 200ms

        except Exception as e:
            print(f"Error in auto control: {e}")
            break

    print("Auto buzzer control stopped")
    auto_control_active = False

@app.route("/")
def index():
    """Render main dashboard"""
    return render_template("index.html")
@app.route("/distance")
def distance():
    """Send ultrasonic distance as JSON"""
    dist = get_distance()
    label = "SAFE" if dist > safe_distance_threshold else "NOT SAFE"
    status = "safe" if label == "SAFE" else "danger"

    # If in auto mode, control buzzer based on this reading
    if buzzer_auto_mode:
        if dist > safe_distance_threshold:
            buzzer_pwm.ChangeDutyCycle(0)
        else:
            buzzer_pwm.ChangeDutyCycle(50)

    return jsonify({
        "distance": dist,
        "label": label,
        "status": status,
        "auto_mode": buzzer_auto_mode
    })

@app.route("/buzzer/on", methods=["POST"])
def buzzer_on():
    """Turn buzzer ON with PWM (manual mode)"""
    global buzzer_auto_mode
    buzzer_auto_mode = False  # Exit auto mode when manually controlling
    time.sleep(0.1)  # Let auto mode thread exit
    buzzer_pwm.ChangeDutyCycle(50)  # 50% duty cycle for louder sound
    print("Buzzer manually turned ON")
    return jsonify({"message": "Buzzer ON", "auto_mode": False})

@app.route("/buzzer/off", methods=["POST"])
def buzzer_off():
    """Turn buzzer OFF (manual mode)"""
    global buzzer_auto_mode
    buzzer_auto_mode = False  # Exit auto mode when manually controlling
    time.sleep(0.1)  # Let auto mode thread exit
    buzzer_pwm.ChangeDutyCycle(0)  # 0% duty cycle
    print("Buzzer manually turned OFF")
    return jsonify({"message": "Buzzer OFF", "auto_mode": False})

@app.route("/buzzer/auto", methods=["POST"])
def buzzer_auto():
    """Enable automatic buzzer control based on distance"""
    global buzzer_auto_mode, auto_control_active
    if not buzzer_auto_mode:
        buzzer_auto_mode = True

        # Start auto control in a separate thread if not already running
        if not auto_control_active:
            auto_thread = threading.Thread(target=auto_buzzer_control)
            auto_thread.daemon = True
            auto_thread.start()
            print("Auto mode started")
        else:
            print("Auto control already active")
    else:
        print("Auto mode already enabled")

    return jsonify({"message": "Buzzer Auto Mode ON", "auto_mode": True})

@app.route("/buzzer/stop", methods=["POST"])
def buzzer_stop():
    """Stop auto mode and turn off buzzer"""
    global buzzer_auto_mode, auto_control_active
    buzzer_auto_mode = False
    auto_control_active = False
    time.sleep(0.2)  # Let auto mode thread exit properly
    buzzer_pwm.ChangeDutyCycle(0)
    print("Auto mode stopped and buzzer turned off")
    return jsonify({"message": "Auto mode stopped", "auto_mode": False})

@app.route("/buzzer/status")
def buzzer_status():
    """Get current buzzer status and mode"""
    return jsonify({
        "auto_mode": buzzer_auto_mode,
        "safe_threshold": safe_distance_threshold,
        "active": auto_control_active
    })

@app.route("/settings/distance", methods=["POST"])
def set_safe_distance():
    """Update the safe distance threshold"""
    global safe_distance_threshold
    data = request.get_json()
    if data and 'distance' in data:
        safe_distance_threshold = float(data['distance'])
        return jsonify({"message": f"Safe distance set to {safe_distance_threshold}cm", "threshold": safe_distance_threshold})
    return jsonify({"error": "Invalid distance value"}), 400
# Test buzzer on startup
def test_buzzer():
    """Test the buzzer on startup"""
    print("Testing buzzer...")
    buzzer_pwm.ChangeDutyCycle(50)
    time.sleep(0.5)
    buzzer_pwm.ChangeDutyCycle(0)
    print("Buzzer test complete")

# Test buzzer when script starts
test_buzzer()

if __name__ == "__main__":
    try:
        print("Starting Flask server...")
        app.run(host="0.0.0.0", port=5000, debug=True, use_reloader=False)
    except KeyboardInterrupt:
        print("Shutting down...")
        buzzer_auto_mode = False
        auto_control_active = False
        time.sleep(0.3)
        buzzer_pwm.stop()
        GPIO.cleanup()

