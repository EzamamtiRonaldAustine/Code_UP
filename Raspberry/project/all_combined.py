# =============================================================================
# COMBINED CODE FROM ALL FILES IN RASPBERRY/PROJECT/
# This file contains all the code from the individual Python files in the
# Raspberry/project/ directory, properly separated and commented for clarity.
# Each section is marked with the original filename and includes the full code.
# Note: This is a compilation for reference; individual scripts may need to be
# run separately due to potential conflicts in GPIO setups or infinite loops.
# =============================================================================

# =============================================================================
# Code from buzzer.py
# Description: Passive buzzer test using PWM to produce a tone.
# =============================================================================
import RPi.GPIO as GPIO
import time

BUZZ = 18

GPIO.setmode(GPIO.BCM)
GPIO.setup(BUZZ, GPIO.OUT)

pwm = GPIO.PWM(BUZZ, 440)  # 440 Hz (A4 tone)

print("Passive buzzer test")

try:
    while True:
        pwm.start(50)
        time.sleep(0.5)
        pwm.stop()
        time.sleep(0.5)
except KeyboardInterrupt:
    pwm.stop()
    GPIO.cleanup()

# =============================================================================
# Code from LCD.py
# Description: LCD display test using I2C interface to show messages.
# =============================================================================
from RPLCD.i2c import CharLCD
import time

# Using I2C address 0x27
lcd = CharLCD('PCF8574', 0x27)

lcd.clear()
lcd.write_string("Smart Fish Pond")
time.sleep(2)

lcd.clear()
lcd.write_string("LCD Working OK!")
time.sleep(2)

# =============================================================================
# Code from Leds.py
# Description: LED testing script that cycles through multiple LEDs.
# =============================================================================
import RPi.GPIO as GPIO
import time

GPIO.setmode(GPIO.BCM)

leds = [27, 5, 6]
for led in leds:
    GPIO.setup(led, GPIO.OUT)

print("Testing LEDs. . . ")

while True:
    for led in leds:
        GPIO.output(led, 1)
        time.sleep(0.5)
        GPIO.output(led, 0)
        time.sleep(0.5)

# =============================================================================
# Code from network_monitoring.py
# Description: Network monitoring script for SIM800C module, checking
# registration status and signal strength.
# =============================================================================
import serial
import time

def send_cmd(ser, cmd, delay=1):
    """Send AT command and return response"""
    ser.write((cmd + "\r\n").encode())
    time.sleep(delay)
    reply = ser.read_all().decode(errors="ignore")
    return reply

def main():
    try:
        ser = serial.Serial(
            port="/dev/serial0",
            baudrate=9600,
            timeout=1
        )
        print("=== Network Monitor ===")
        print("Press Ctrl+C to stop\n")
        time.sleep(2)
    except serial.SerialException as e:
        print(f"Error: {e}")
        return

    # Initialize
    send_cmd(ser, "AT")
    send_cmd(ser, "ATE0")

    try:
        while True:
            # Check registration
            creg = send_cmd(ser, "AT+CREG?")

            # Parse registration status
            if "+CREG: 0,1" in creg:
                status = "✅ Registered (Home)"
            elif "+CREG: 0,5" in creg:
                status = "✅ Registered (Roaming)"
            elif "+CREG: 0,2" in creg:
                status = "🔍 Searching..."
            elif "+CREG: 0,3" in creg:
                status = "❌ Registration Denied"
            elif "+CREG: 0,0" in creg:
                status = "⚠️ Not Registered"
            else:
                status = f"❓ Unknown: {creg.strip()}"

            # Check signal
            csq = send_cmd(ser, "AT+CSQ")
            signal = "Unknown"
            if "+CSQ:" in csq:
                try:
                    sig_val = csq.split("+CSQ: ")[1].split(",")[0]
                    signal = f"{sig_val}/31"
                except:
                    signal = csq.strip()

            # Display
            timestamp = time.strftime("%H:%M:%S")
            print(f"[{timestamp}] Status: {status} | Signal: {signal}")

            time.sleep(3)

    except KeyboardInterrupt:
        print("\n\nMonitoring stopped.")

    ser.close()

if __name__ == "__main__":
    main()

# =============================================================================
# Code from pump.py
# Description: Empty file - no code present.
# =============================================================================
# (No code in this file)

# =============================================================================
# Code from sim800c.py
# Description: SIM800C module initialization and SMS sending script.
# =============================================================================
import serial
import time

def send_cmd(ser, cmd, delay=1):
    """Send AT command to SIM800C and return response"""
    ser.write((cmd + "\r\n").encode())
    time.sleep(delay)
    reply = ser.read_all().decode(errors="ignore")
    print(f">>> {cmd}")
    print(reply)
    return reply

def wait_for_network(ser, timeout=60):
    """Wait for network registration"""
    print("Waiting for network registration...")
    start = time.time()

    while time.time() - start < timeout:
        reply = send_cmd(ser, "AT+CREG?", delay=1)

        # Check if registered (0,1 = home network, 0,5 = roaming)
        if "+CREG: 0,1" in reply or "+CREG: 0,5" in reply:
            print("✅ Registered on network!")
            return True

        # Check signal strength
        signal = send_cmd(ser, "AT+CSQ", delay=1)
        print(f"Signal check: {signal.strip()}")

        time.sleep(3)

    print("❌ Failed to register on network within timeout")
    return False

def main():
    try:
        ser = serial.Serial(
            port="/dev/serial0",
            baudrate=9600,
            timeout=2
        )
        print("Initializing SIM800C...")
        time.sleep(5)  # Longer initial delay
    except serial.SerialException as e:
        print(f"Error opening serial port: {e}")
        return

    # Test communication
    send_cmd(ser, "AT")
    time.sleep(1)

    # Disable echo
    send_cmd(ser, "ATE0")
    time.sleep(1)

    # Check SIM status (with retries)
    for i in range(3):
        reply = send_cmd(ser, "AT+CPIN?", delay=2)
        if "READY" in reply:
            print("✅ SIM card ready")
            break
        time.sleep(2)

    # Wait for network registration
    if not wait_for_network(ser, timeout=60):
        print("Cannot proceed without network registration")
        ser.close()
        return

    # Check final signal strength
    signal = send_cmd(ser, "AT+CSQ")
    if "+CSQ: 0," in signal or "+CSQ: 99," in signal:
        print("⚠️ WARNING: Signal strength is still very weak or undetectable")
        print("Consider moving antenna to better location")

    # Set SMS text mode
    send_cmd(ser, "AT+CMGF=1")
    time.sleep(1)

    # Set SMS character set to GSM
    send_cmd(ser, "AT+CSCS=\"GSM\"")
    time.sleep(1)

    PHONE = "+256763583059"
    MESSAGE = "Hello from Raspberry Pi and SIM800C!"

    print(f"\n--- Attempting to send SMS to {PHONE} ---")

    # Tell SIM800C we want to send an SMS
    reply = send_cmd(ser, f'AT+CMGS="{PHONE}"', delay=2)

    if ">" in reply:
        print("Prompt received, sending SMS text...")

        # Send message text
        ser.write(MESSAGE.encode())
        time.sleep(0.5)

        # Send Ctrl+Z to terminate
        ser.write(b'\x1A')

        # Wait for transmission with progressive reading
        print("Waiting for network confirmation...")
        final_reply = ""

        for i in range(20):  # Wait up to 20 seconds
            time.sleep(1)
            chunk = ser.read_all().decode(errors="ignore")
            final_reply += chunk

            # Check if we got a response
            if "+CMGS:" in final_reply or "ERROR" in final_reply:
                break

        print("Final response from module:")
        print(final_reply)

        if "+CMGS:" in final_reply:
            print("\n✅ SMS sent successfully!")
        elif "ERROR" in final_reply:
            print("\n❌ SMS send failed with ERROR")
            # Check specific error
            error_reply = send_cmd(ser, "AT+CMEE=2", delay=1)  # Enable verbose errors
            print("Error details:", error_reply)
        else:
            print("\n❌ No response from module (timeout)")
            print("Possible reasons:")
            print("- Network congestion")
            print("- SMS service not activated on SIM")
            print("- Module needs reset")
    else:
        print("No > prompt received. SMS cannot be sent.")

    ser.close()
    print("Serial connection closed.")

if __name__ == "__main__":
    main()

# =============================================================================
# Code from soil_sensor1.py
# Description: Comprehensive soil/water quality monitoring system for smart fish pond.
# Reads multiple parameters and provides detailed status reports.
# =============================================================================
import minimalmodbus
import time
from datetime import datetime

PORT = '/dev/ttyUSB0'
SLAVE_ID = 1

instrument = minimalmodbus.Instrument(PORT, SLAVE_ID)
instrument.serial.baudrate = 9600
instrument.serial.bytesize = 8
instrument.serial.parity = minimalmodbus.serial.PARITY_NONE
instrument.serial.stopbits = 1
instrument.serial.timeout = 1

# Register mapping
REGISTERS = {
    'nitrogen': 4,
    'phosphorus': 5,
    'potassium': 6,
    'ec': 7,
    'moisture': 9,      # For soil/sediment monitoring
    'ph': 13,
    'temperature': 19,
}

def read_register(reg):
    try:
        return instrument.read_register(reg, 1, functioncode=3)
    except:
        return None

def read_register_no_decimals(reg):
    try:
        return instrument.read_register(reg, 0, functioncode=3)
    except:
        return None

def get_water_quality_status(ph, temp, ec):
    """Assess water quality based on parameters"""
    status = {
        'overall': 'GOOD',
        'ph_status': '',
        'temp_status': '',
        'ec_status': '',
        'alerts': [],
        'recommendations': []
    }

    # pH Assessment (Most Critical for Fish Health)
    if ph is None or ph < 0.5:
        status['ph_status'] = 'NO READING'
        status['alerts'].append('⚠️ pH sensor not in water')
    elif ph < 4.0:
        status['ph_status'] = '🔴 LETHAL - EXTREME ACID'
        status['overall'] = 'CRITICAL'
        status['alerts'].append('🚨 EMERGENCY: pH < 4.0 - FISH WILL DIE!')
        status['recommendations'].append('Immediate water change (50-75%)')
        status['recommendations'].append('Add lime/baking soda gradually')
    elif ph < 6.0:
        status['ph_status'] = '🔴 CRITICAL - TOO ACIDIC'
        status['overall'] = 'CRITICAL'
        status['alerts'].append('🚨 DANGER: pH < 6.0 - Fish stress, gill damage, mortality risk')
        status['recommendations'].append('Add agricultural lime (CaCO₃): 1kg per 1000L')
        status['recommendations'].append('Or baking soda: 1 tsp per 10 gallons')
    elif ph < 6.5:
        status['ph_status'] = '⚠️ WARNING - ACIDIC'
        status['overall'] = 'WARNING'
        status['alerts'].append('⚠️ pH low - Monitor closely, fish may be stressed')
        status['recommendations'].append('Consider gradual pH adjustment')
    elif ph <= 8.5:
        status['ph_status'] = '✅ OPTIMAL'
    elif ph <= 9.0:
        status['ph_status'] = '⚠️ WARNING - ALKALINE'
        status['overall'] = 'WARNING'
        status['alerts'].append('⚠️ pH high - Ammonia becomes MORE toxic at high pH!')
        status['recommendations'].append('Check ammonia levels immediately')
    elif ph <= 10.0:
        status['ph_status'] = '🔴 CRITICAL - TOO ALKALINE'
        status['overall'] = 'CRITICAL'
        status['alerts'].append('🚨 DANGER: pH > 9.0 - Ammonia toxicity, gill damage')
        status['recommendations'].append('Partial water change with acidic water')
        status['recommendations'].append('Add organic matter to lower pH')
    else:
        status['ph_status'] = '🔴 LETHAL - EXTREME ALKALINE'
        status['overall'] = 'CRITICAL'
        status['alerts'].append('🚨 EMERGENCY: pH > 10.0 - FISH WILL DIE!')
        status['recommendations'].append('Emergency 75% water change')

    # Temperature Assessment (Critical for Metabolism & Oxygen)
    if temp is not None:
        if temp < 10:
            status['temp_status'] = '🔵 TOO COLD - Fish dormant/dying'
            status['overall'] = 'CRITICAL'
            status['alerts'].append('🚨 Temperature < 10°C - Tropical fish cannot survive')
            status['recommendations'].append('Add pond heater immediately')
        elif temp < 15:
            status['temp_status'] = '⚠️ COLD - Fish stressed, immune system weak'
            if status['overall'] == 'GOOD':
                status['overall'] = 'WARNING'
            status['recommendations'].append('Increase temperature gradually (1°C per day)')
        elif temp < 20:
            status['temp_status'] = '⚠️ COOL - Reduced feeding, slow growth'
            if status['overall'] == 'GOOD':
                status['overall'] = 'WARNING'
        elif temp <= 28:
            status['temp_status'] = '✅ OPTIMAL (20-28°C)'
        elif temp <= 32:
            status['temp_status'] = '⚠️ WARM - Low oxygen risk'
            if status['overall'] == 'GOOD':
                status['overall'] = 'WARNING'
            status['alerts'].append('⚠️ Warm water holds less oxygen')
            status['recommendations'].append('Increase aeration/circulation')
            status['recommendations'].append('Reduce feeding (waste produces ammonia)')
        elif temp <= 35:
            status['temp_status'] = '🔴 TOO HOT - Fish gasping, stress'
            status['overall'] = 'CRITICAL'
            status['alerts'].append('🚨 High temperature + low oxygen = fish death')
            status['recommendations'].append('Add shade/cover to pond')
            status['recommendations'].append('Add cool water slowly')
            status['recommendations'].append('MAXIMIZE aeration')
        else:
            status['temp_status'] = '🔴 LETHAL - Above survival limit'
            status['overall'] = 'CRITICAL'
            status['alerts'].append('🚨 EMERGENCY: Temp > 35°C - Immediate fish death risk')
            status['recommendations'].append('Emergency cooling required')

    # EC/TDS Assessment (Dissolved Solids - affects osmoregulation)
    if ec is not None:
        if ec < 30:
            status['ec_status'] = '⚠️ Very low - Mineral deficient water'
            status['recommendations'].append('Water too pure - add mineral salts')
        elif ec < 50:
            status['ec_status'] = '⚠️ Low conductivity'
        elif ec <= 300:
            status['ec_status'] = '✅ OPTIMAL for freshwater fish'
        elif ec <= 800:
            status['ec_status'] = '✅ Good - Acceptable range'
        elif ec <= 1500:
            status['ec_status'] = '⚠️ Elevated - Monitor salinity'
            if status['overall'] == 'GOOD':
                status['overall'] = 'WARNING'
            status['recommendations'].append('Check for excess dissolved solids')
        elif ec <= 3000:
            status['ec_status'] = '🔴 HIGH - Brackish conditions'
            status['overall'] = 'CRITICAL'
            status['alerts'].append('🚨 High salinity - Freshwater fish stressed')
            status['recommendations'].append('Dilute with fresh water')
        else:
            status['ec_status'] = '🔴 EXTREME - Nearly seawater'
            status['overall'] = 'CRITICAL'
            status['alerts'].append('🚨 EMERGENCY: Freshwater fish cannot survive')
            status['recommendations'].append('Immediate water change required')

    return status

def read_pond_sensors():
    """Read all water quality sensors"""
    data = {}

    # Temperature
    temp = read_register(REGISTERS['temperature'])
    data['temperature'] = temp

    # pH with correct formula
    ph_raw = read_register(REGISTERS['ph'])
    if ph_raw is not None and ph_raw > 0.5:
        data['ph'] = ph_raw / 3.13
        data['ph_raw'] = ph_raw
    else:
        data['ph'] = None
        data['ph_raw'] = None

    # EC (Electrical Conductivity)
    data['ec'] = read_register(REGISTERS['ec'])

    # Nutrients (important for algae control)
    data['nitrogen'] = read_register(REGISTERS['nitrogen'])
    data['phosphorus'] = read_register(REGISTERS['phosphorus'])
    data['potassium'] = read_register(REGISTERS['potassium'])

    return data

def display_pond_status(data, status):
    """Display formatted water quality report"""
    print("\n" + "="*60)
    print(f"  SMART FISH POND MONITOR - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
    print("="*60)

    # Overall Status Banner
    if status['overall'] == 'CRITICAL':
        print(f"\n🚨🚨🚨 OVERALL STATUS: {status['overall']} 🚨🚨🚨")
    elif status['overall'] == 'WARNING':
        print(f"\n⚠️  OVERALL STATUS: {status['overall']} ⚠️")
    else:
        print(f"\n✅  OVERALL STATUS: {status['overall']} ✅")

    # Critical Parameters
    print("\n--- CRITICAL WATER PARAMETERS ---")

    # pH
    if data['ph'] is not None:
        ph_icon = "💧"
        if data['ph'] < 6.5:
            ph_icon = "🔴"
        elif data['ph'] > 8.5:
            ph_icon = "🔵"
        else:
            ph_icon = "✅"

        print(f"{ph_icon} pH Level:        {data['ph']:.1f}")
        print(f"   Status:         {status['ph_status']}")

        # Show acidity/alkalinity
        if data['ph'] < 7.0:
            print(f"   Type:           ACIDIC (below neutral)")
        elif data['ph'] > 7.0:
            print(f"   Type:           ALKALINE (above neutral)")
        else:
            print(f"   Type:           NEUTRAL (perfect)")
    else:
        print(f"🔴 pH Level:        NO READING (sensor not in water)")

    # Temperature
    if data['temperature'] is not None:
        temp_icon = "🌡️" if 20 <= data['temperature'] <= 30 else "⚠️"
        print(f"{temp_icon} Temperature:     {data['temperature']:.1f}°C")
        print(f"   Status:         {status['temp_status']}")

    # EC
    if data['ec'] is not None:
        print(f"⚡ Conductivity:    {data['ec']:.0f} μS/cm")
        print(f"   Status:         {status['ec_status']}")

    # Nutrients
    print("\n--- NUTRIENT LEVELS ---")
    print("(High nutrients → Algae blooms → Low oxygen → Fish death)")

    if data['nitrogen'] is not None:
        n_icon = "✅"
        n_status = "Normal"
        if data['nitrogen'] > 10:
            n_icon = "🔴"
            n_status = "CRITICAL - Major algae/toxicity risk"
            status['alerts'].append('🚨 Nitrogen extremely high - water change needed')
        elif data['nitrogen'] > 5:
            n_icon = "⚠️"
            n_status = "High - Algae bloom risk"
        elif data['nitrogen'] > 2:
            n_icon = "⚠️"
            n_status = "Elevated - Monitor"
        print(f"{n_icon} Nitrogen (N):    {data['nitrogen']:.1f} mg/kg - {n_status}")
        print(f"   Safe: <2 mg/kg | Warning: 2-5 | Danger: >5")

    if data['phosphorus'] is not None:
        p_icon = "✅"
        p_status = "Normal"
        if data['phosphorus'] > 5:
            p_icon = "🔴"
            p_status = "CRITICAL - Severe algae risk"
            status['alerts'].append('🚨 Phosphorus extremely high - algae explosion imminent')
        elif data['phosphorus'] > 1:
            p_icon = "⚠️"
            p_status = "High - Algae bloom risk"
        elif data['phosphorus'] > 0.5:
            p_icon = "⚠️"
            p_status = "Elevated - Monitor"
        print(f"{p_icon} Phosphorus (P):  {data['phosphorus']:.1f} mg/kg - {p_status}")
        print(f"   Safe: <0.5 mg/kg | Warning: 0.5-1 | Danger: >1")

    if data['potassium'] is not None:
        k_icon = "✅"
        k_status = "Normal (less critical)"
        if data['potassium'] > 100:
            k_icon = "⚠️"
            k_status = "High but not directly toxic"
        print(f"{k_icon} Potassium (K):   {data['potassium']:.0f} mg/kg - {k_status}")
        print(f"   Typical range: 5-50 mg/kg")

    # Important: Explain the algae-oxygen-death cycle
    if (data['nitrogen'] and data['nitrogen'] > 5) or (data['phosphorus'] and data['phosphorus'] > 1):
        print("\n💀 ALGAE DANGER CHAIN:")
        print("   High N/P → Algae bloom → Blocks sunlight → Dead algae")
        print("   → Bacteria consume oxygen → Fish suffocate at night!")
        status['recommendations'].append('Reduce feeding (main N/P source)')
        status['recommendations'].append('Remove dead organic matter')
        status['recommendations'].append('Increase aeration at night')

    # Alerts & Recommendations
    if status['alerts'] or status['recommendations']:
        print("\n" + "="*60)
        print("⚠️  ALERTS & ACTIONS REQUIRED:")
        print("="*60)

        for alert in status['alerts']:
            print(f"  {alert}")

        if status['recommendations']:
            print("\n💡 RECOMMENDED ACTIONS:")
            for i, rec in enumerate(status['recommendations'], 1):
                print(f"  {i}. {rec}")

        # pH-specific recommendations
        if data['ph'] is not None:
            if data['ph'] < 6.5:
                print("\n📋 TO RAISE pH (reduce acidity):")
                print("   • Add agricultural lime: 1kg per 1000L water")
                print("   • Add baking soda: 1 tsp per 10 gallons")
                print("   • Remove decaying organic matter")
                print("   • Increase water changes")
            elif data['ph'] > 8.5:
                print("\n📋 TO LOWER pH (reduce alkalinity):")
                print("   • 25-50% water change with neutral pH water")
                print("   • Add peat moss or driftwood")
                print("   • Reduce algae (photosynthesis raises pH)")
                print("   • Check for limestone/concrete contamination")

    print("\n" + "="*60 + "\n")

# Main monitoring loop
print("="*60)
print("  SMART FISH POND MONITORING SYSTEM")
print("  Sensor: 7-in-1 Soil/Water Quality Sensor")
print("  Configuration: 9600 baud, Register 13 for pH")
print("="*60)
print("\n⚠️  IMPORTANT: Submerge sensor probe in pond water")
print("   Wait 30 seconds for pH reading to stabilize\n")

while True:
    try:
        # Read all sensors
        data = read_pond_sensors()

        # Assess water quality
        status = get_water_quality_status(data['ph'], data['temperature'], data['ec'])

        # Display report
        display_pond_status(data, status)

        # Update interval
        time.sleep(10)  # Read every 10 seconds

    except KeyboardInterrupt:
        print("\n\n👋 Monitoring stopped by user")
        print("Stay vigilant about your fish pond water quality!")
        break
    except Exception as e:
        print(f"\n❌ Error: {e}")
        time.sleep(5)

# =============================================================================
# Code from temp_sensor.py
# Description: Temperature sensor reading using 1-Wire DS18B20 sensor.
# =============================================================================
import os
import glob
import time

# Load 1-Wire modules
os.system('modprobe w1-gpio')
os.system('modprobe w1-therm')

base_dir = '/sys/bus/w1/devices/'
device_folder = glob.glob(base_dir + '28-*')[0]
device_file = device_folder + '/w1_slave'

def read_temp_raw():
    with open(device_file, 'r') as f:
        return f.readlines()

def read_temp():
    lines = read_temp_raw()

    # Wait until CRC = YES
    while lines[0].strip()[-3:] != 'YES':
        time.sleep(0.2)
        lines = read_temp_raw()

    equals_pos = lines[1].find('t=')
    if equals_pos != -1:
        temp_string = lines[1][equals_pos + 2:]
        temp_c = float(temp_string) / 1000.0
        return temp_c

    return None

while True:
    print("Temperature:", read_temp(), "C")
    time.sleep(1)

# =============================================================================
# Code from turbidity.py
# Description: Turbidity sensor test using digital input to detect water clarity.
# =============================================================================
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

# =============================================================================
# END OF COMBINED CODE
# =============================================================================
