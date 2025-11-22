import os
import glob
import time
import RPi.GPIO as GPIO
from datetime import datetime
import minimalmodbus
from RPLCD.i2c import CharLCD
import threading
from collections import deque

# --- Configuration ---
TEMP_READ_INTERVAL = 15  # seconds between readings
LCD_REFRESH_INTERVAL = 5 # seconds between LCD screen changes
PUMP_RUN_DURATION = {
    "SHORT": 120,   # 2 minutes
    "NORMAL": 300,  # 5 minutes
    "LONG": 600     # 10 minutes
}
HISTORY_SIZE = 5  # number of readings to keep for trend analysis

# --- GPIO Pin Assignments ---
TURBIDITY_PIN = 17
BUZZER_PIN = 18
BLUE_LED_PIN = 27
YELLOW_LED_PIN = 22
RED_LED_PIN = 5
PUMP_PIN = 16  # GPIO pin for pump relay

# --- RS485 Sensor Configuration ---
RS485_PORT = '/dev/ttyUSB0'
RS485_SLAVE_ID = 1

# --- Global Variables ---
current_lcd_screen = 0
sensor_data = {}
current_status = {}  # Store the last computed status to avoid recalculation
pwm_buzzer = None # PWM object for the buzzer
pump_should_run = False
pump_is_running = False
pump_mode = "OFF"  # Can be "OFF", "SHORT", "NORMAL", "LONG"

# Historical data storage (using deque for efficient appends and pops)
temp_history = deque(maxlen=HISTORY_SIZE)
ph_history = deque(maxlen=HISTORY_SIZE)
ec_history = deque(maxlen=HISTORY_SIZE)
nitrogen_history = deque(maxlen=HISTORY_SIZE)
phosphorus_history = deque(maxlen=HISTORY_SIZE)
turbidity_history = deque(maxlen=HISTORY_SIZE)

# --- IMPORTANT SETUP NOTE ---
# Before running, you MUST enable the 1-Wire interface:
# 1. Run: sudo raspi-config
# 2. Go to 'Interface Options' -> '1-Wire' -> 'Enable'
# 3. Reboot the Raspberry Pi: sudo reboot

class SmartFishPondMonitor:
    def __init__(self):
        global pwm_buzzer
        # Initialize GPIO
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(TURBIDITY_PIN, GPIO.IN)
        GPIO.setup(BLUE_LED_PIN, GPIO.OUT)
        GPIO.setup(YELLOW_LED_PIN, GPIO.OUT)
        GPIO.setup(RED_LED_PIN, GPIO.OUT)
        GPIO.setup(BUZZER_PIN, GPIO.OUT)
        GPIO.setup(PUMP_PIN, GPIO.OUT)

        # Initialize Buzzer with PWM for a proper tone
        pwm_buzzer = GPIO.PWM(BUZZER_PIN, 1000) # 1000 Hz frequency
        pwm_buzzer.start(0) # Start with 0% duty cycle (off)

        # Initialize all indicators to OFF
        self.set_leds(0, 0, 0)
        # Initialize pump to OFF (HIGH for low-triggered relay)
        GPIO.output(PUMP_PIN, GPIO.HIGH)

        # Initialize LCD
        try:
            self.lcd = CharLCD('PCF8574', 0x27)
            self.lcd.clear()
            self.lcd.write_string("Initializing...")
        except Exception as e:
            print(f"LCD initialization failed: {e}")
            self.lcd = None

        # Initialize RS485 sensor
        self.rs485_instrument = self.init_rs485()

        # Initialize DS18B20 temperature sensor
        self.device_file = self.init_ds18b20()

        # Start threads
        self.running = True
        self.monitor_thread = threading.Thread(target=self.monitor_loop)
        self.display_thread = threading.Thread(target=self.display_loop)
        self.pump_thread = threading.Thread(target=self.pump_control_loop)
        
        self.monitor_thread.daemon = True
        self.display_thread.daemon = True
        self.pump_thread.daemon = True
        
        self.monitor_thread.start()
        self.display_thread.start()
        self.pump_thread.start()

    def init_rs485(self):
        try:
            instrument = minimalmodbus.Instrument(RS485_PORT, RS485_SLAVE_ID)
            instrument.serial.baudrate = 9600
            instrument.serial.bytesize = 8
            instrument.serial.parity = minimalmodbus.serial.PARITY_NONE
            instrument.serial.stopbits = 1
            instrument.serial.timeout = 1
            print("✅ RS485 sensor initialized")
            return instrument
        except Exception as e:
            print(f"❌ RS485 initialization failed: {e}")
            return None

    def init_ds18b20(self):
        try:
            base_dir = '/sys/bus/w1/devices/'
            device_folder = glob.glob(base_dir + '28-*')[0]
            device_file = device_folder + '/w1_slave'
            print("✅ DS18B20 temperature sensor initialized")
            return device_file
        except (IndexError, Exception) as e:
            print(f"❌ DS18B20 initialization failed: {e}. Check 1-Wire is enabled in raspi-config.")
            return None

    def read_ds18b20_temp(self):
        if not self.device_file:
            return None
        try:
            with open(self.device_file, 'r') as f:
                lines = f.readlines()
            if lines[0].strip()[-3:] == 'YES':
                equals_pos = lines[1].find('t=')
                if equals_pos != -1:
                    temp_c = float(lines[1][equals_pos + 2:]) / 1000.0
                    return temp_c
        except Exception as e:
            print(f"Error reading DS18B20: {e}")
        return None

    def read_turbidity(self):
        try:
            return GPIO.input(TURBIDITY_PIN) == 0  # 0 = turbid, 1 = clear
        except:
            return None

    def read_rs485_sensor(self):
        if not self.rs485_instrument:
            return {}
        data = {}
        
        # Read temperature first to ensure it's available for pH calculation
        try:
            temp_value = self.rs485_instrument.read_register(19, 1, functioncode=3)
            data['temperature'] = temp_value
        except Exception as e:
            print(f"Error reading RS485 temperature: {e}")
            data['temperature'] = None
        
        # Now read other parameters
        registers = {
            'nitrogen': 4,
            'phosphorus': 5,
            'potassium': 6,
            'ec': 7,
            'ph': 13,
        }
        
        try:
            for param, reg in registers.items():
                value = self.rs485_instrument.read_register(reg, 1, functioncode=3)
                if param == 'ph':
                    data['ph_raw'] = value
                    if value is not None and value > 0.5:
                        # Use the temperature we already read
                        data[param] = self.calculate_ph(value, data.get('temperature', 25))
                    else:
                        data[param] = None
                else:
                    data[param] = value
        except Exception as e:
            # Return empty dict to signal a failed read
            return {}
        return data

    def calculate_ph(self, raw_value, temperature):
        """Calculate pH with temperature compensation"""
        # Base calculation
        ph = raw_value / 3.13
        
        # Temperature compensation (simplified)
        # Adjust pH based on temperature deviation from 25°C
        temp_compensation = (temperature - 25) * 0.01
        ph_adjusted = ph - temp_compensation
        
        return ph_adjusted

    def combine_temperatures(self, rs485_temp, ds18b20_temp):
        """Combine RS485 and DS18B20 temperatures into a single value"""
        if rs485_temp is not None and ds18b20_temp is not None:
            # Weighted average: 60% RS485, 40% DS18B20
            return 0.6 * rs485_temp + 0.4 * ds18b20_temp
        elif rs485_temp is not None:
            return rs485_temp
        elif ds18b20_temp is not None:
            return ds18b20_temp
        else:
            return None

    def update_historical_data(self, data, ds18b20_temp):
        """Update historical data with new readings"""
        global temp_history, ph_history, ec_history, nitrogen_history, phosphorus_history, turbidity_history
        
        # Update temperature history with combined value
        combined_temp = self.combine_temperatures(data.get('temperature'), ds18b20_temp)
        if combined_temp is not None:
            temp_history.append(combined_temp)
        
        # Update pH history
        ph = data.get('ph')
        if ph is not None:
            ph_history.append(ph)
        
        # Update EC history
        ec = data.get('ec')
        if ec is not None:
            ec_history.append(ec)
        
        # Update nitrogen history
        nitrogen = data.get('nitrogen')
        if nitrogen is not None:
            nitrogen_history.append(nitrogen)
        
        # Update phosphorus history
        phosphorus = data.get('phosphorus')
        if phosphorus is not None:
            phosphorus_history.append(phosphorus)
        
        # Update turbidity history
        turbidity = self.read_turbidity()
        if turbidity is not None:
            turbidity_history.append(1 if turbidity else 0)  # 1 for turbid, 0 for clear

    def get_average(self, history):
        """Calculate average of historical data"""
        if not history:
            return None
        return sum(history) / len(history)

    def get_trend(self, history):
        """Determine if values are increasing, decreasing, or stable"""
        if len(history) < 3:
            return "STABLE"  # Not enough data for trend
        
        # Simple trend calculation: compare first half to second half
        mid = len(history) // 2
        first_half_avg = sum(list(history)[:mid]) / mid
        second_half_avg = sum(list(history)[mid:]) / (len(history) - mid)
        
        diff = second_half_avg - first_half_avg
        threshold = 0.1 * first_half_avg  # 10% change threshold
        
        if diff > threshold:
            return "INCREASING"
        elif diff < -threshold:
            return "DECREASING"
        else:
            return "STABLE"

    def get_water_quality_status(self, data):
        """Assess water quality using weighted scoring and historical data"""
        status = {
            'overall': 'GOOD',
            'score': 0,  # 0-100, higher is worse
            'alerts': [],
            'recommendations': set(),  # Use a set to avoid duplicate recommendations
            'trends': {}
        }
        
        # Get averages for more stable assessment
        avg_temp = self.get_average(temp_history)
        avg_ph = self.get_average(ph_history)
        avg_ec = self.get_average(ec_history)
        avg_nitrogen = self.get_average(nitrogen_history)
        avg_phosphorus = self.get_average(phosphorus_history)
        turbidity_ratio = sum(turbidity_history) / len(turbidity_history) if turbidity_history else 0
        
        # Get trends
        status['trends']['temperature'] = self.get_trend(temp_history)
        status['trends']['ph'] = self.get_trend(ph_history)
        status['trends']['nitrogen'] = self.get_trend(nitrogen_history)
        status['trends']['phosphorus'] = self.get_trend(phosphorus_history)
        
        # pH Assessment (weight: 25%)
        if avg_ph is None:
            status['alerts'].append('⚠️ pH sensor not in water or faulty')
            status['score'] += 30  # Add to score but not critical
        elif avg_ph < 6.0:
            status['score'] += 40
            status['alerts'].append(f"🚨 DANGER: pH {avg_ph:.1f} is too acidic")
            status['recommendations'].add('Add agricultural lime (CaCO₃) or baking soda')
        elif avg_ph < 6.5:
            status['score'] += 20
            status['alerts'].append(f"⚠️ pH {avg_ph:.1f} is slightly acidic")
        elif avg_ph > 9.0:
            status['score'] += 40
            status['alerts'].append(f"🚨 DANGER: pH {avg_ph:.1f} is too alkaline")
            status['recommendations'].add('Perform partial water change with neutral pH water')
        elif avg_ph > 8.5:
            status['score'] += 20
            status['alerts'].append(f"⚠️ pH {avg_ph:.1f} is slightly alkaline")
        
        # Temperature Assessment (weight: 20%)
        if avg_temp is not None:
            if avg_temp < 15:
                status['score'] += 35
                status['alerts'].append(f"🚨 Temperature {avg_temp:.1f}°C is too cold")
                status['recommendations'].add('Add pond heater')
            elif avg_temp < 20:
                status['score'] += 15
                status['alerts'].append(f"⚠️ Temperature {avg_temp:.1f}°C is cool")
            elif avg_temp > 32:
                status['score'] += 35
                status['alerts'].append(f"🚨 Temperature {avg_temp:.1f}°C is too hot")
                status['recommendations'].add('Add shade and increase aeration')
            elif avg_temp > 28:
                status['score'] += 15
                status['alerts'].append(f"⚠️ Temperature {avg_temp:.1f}°C is warm")
        
        # EC Assessment (weight: 10%)
        if avg_ec is not None:
            if avg_ec > 1500:
                status['score'] += 30
                status['alerts'].append(f"🚨 EC {avg_ec:.0f} μS/cm is too high")
                status['recommendations'].add('Dilute with fresh water')
            elif avg_ec > 800:
                status['score'] += 15
                status['alerts'].append(f"⚠️ EC {avg_ec:.0f} μS/cm is elevated")
        
        # Turbidity Assessment (weight: 10%)
        if turbidity_ratio > 0.7:  # More than 70% turbid readings
            status['score'] += 25
            status['alerts'].append(f"⚠️ Water is consistently turbid")
            status['recommendations'].add('Check filter and perform water change')
        elif turbidity_ratio > 0.4:  # More than 40% turbid readings
            status['score'] += 15
            status['alerts'].append(f"⚠️ Water is occasionally turbid")
        
        # Nutrient Assessment (weight: 35%)
        if avg_nitrogen is not None and avg_nitrogen > 5:  # Threshold for mg/kg
            status['score'] += 30
            status['alerts'].append(f"🚨 Nitrogen extremely high: {avg_nitrogen:.1f} mg/kg")
            status['recommendations'].add('Reduce feeding and perform water change')
        elif avg_nitrogen is not None and avg_nitrogen > 2:
            status['score'] += 15
            status['alerts'].append(f"⚠️ Nitrogen elevated: {avg_nitrogen:.1f} mg/kg")
        
        if avg_phosphorus is not None and avg_phosphorus > 1:  # Threshold for mg/kg
            status['score'] += 30
            status['alerts'].append(f"🚨 Phosphorus extremely high: {avg_phosphorus:.1f} mg/kg")
            status['recommendations'].add('Reduce feeding and perform water change')
        elif avg_phosphorus is not None and avg_phosphorus > 0.5:
            status['score'] += 15
            status['alerts'].append(f"⚠️ Phosphorus elevated: {avg_phosphorus:.1f} mg/kg")
        
        # Determine overall status based on score
        if status['score'] >= 70:
            status['overall'] = 'CRITICAL'
        elif status['score'] >= 40:
            status['overall'] = 'WARNING'
        else:
            status['overall'] = 'GOOD'
        
        return status

    def set_leds(self, blue, yellow, red):
        GPIO.output(BLUE_LED_PIN, blue)
        GPIO.output(YELLOW_LED_PIN, yellow)
        GPIO.output(RED_LED_PIN, red)

    def update_indicators(self, status):
        global pwm_buzzer, pump_should_run, pump_mode, pump_is_running
        self.set_leds(0, 0, 0)  # Turn off all LEDs first
        pwm_buzzer.ChangeDutyCycle(0)  # Turn off buzzer

        if status['overall'] == 'GOOD':
            self.set_leds(1, 0, 0)  # Blue LED ON
            pump_should_run = False  # Ensure pump is off if status is good
            pump_mode = "OFF"
        elif status['overall'] == 'WARNING':
            self.set_leds(0, 1, 0)  # Yellow LED ON
            pwm_buzzer.ChangeDutyCycle(50)  # Beep
            time.sleep(0.2)
            pwm_buzzer.ChangeDutyCycle(0)  # Off
            pump_should_run = False
            pump_mode = "OFF"
        elif status['overall'] == 'CRITICAL':
            self.set_leds(0, 0, 1)  # Red LED ON
            pwm_buzzer.ChangeDutyCycle(50)  # Beep
            time.sleep(1)
            pwm_buzzer.ChangeDutyCycle(0)  # Off
            
            # Only set pump_should_run if pump is not already running (latch mechanism)
            if not pump_is_running:
                pump_should_run = True  # Activate pump for critical status
                
                # Determine pump mode based on critical factors
                avg_temp = self.get_average(temp_history)
                avg_ph = self.get_average(ph_history)
                avg_nitrogen = self.get_average(nitrogen_history)
                avg_phosphorus = self.get_average(phosphorus_history)
                turbidity_ratio = sum(turbidity_history) / len(turbidity_history) if turbidity_history else 0
                
                if avg_temp is not None and (avg_temp < 15 or avg_temp > 32):
                    pump_mode = "LONG"  # 10 minutes for temperature issues
                elif avg_ph is not None and (avg_ph < 6.0 or avg_ph > 9.0):
                    pump_mode = "SHORT"  # 2 minutes for pH issues
                elif (avg_nitrogen is not None and avg_nitrogen > 5) or \
                     (avg_phosphorus is not None and avg_phosphorus > 1) or \
                     turbidity_ratio > 0.7:
                    pump_mode = "NORMAL"  # 5 minutes for nutrient/turbidity issues
                else:
                    pump_mode = "NORMAL"  # Default to 5 minutes

    def pump_control_loop(self):
        """Dedicated thread to control water pump with different modes."""
        global pump_should_run, pump_is_running, pump_mode
        pump_start_time = 0

        while self.running:
            if pump_should_run and not pump_is_running:
                print(f"  -> ACTION: Activating PUMP in {pump_mode} mode to improve water quality.")
                GPIO.output(PUMP_PIN, GPIO.LOW)  # Turn pump ON
                pump_is_running = True
                pump_start_time = time.time()
                # Reset pump_should_run to prevent retriggering
                pump_should_run = False
            
            if pump_is_running:
                # Determine run time based on pump mode
                run_duration = PUMP_RUN_DURATION.get(pump_mode, 300)  # Default to 5 minutes
                if time.time() - pump_start_time > run_duration:
                    print(f"  -> ACTION: {pump_mode} pump cycle complete. Turning PUMP OFF.")
                    GPIO.output(PUMP_PIN, GPIO.HIGH)  # Turn pump OFF
                    pump_is_running = False
                    pump_mode = "OFF"
            
            time.sleep(1)  # Check every second

    def update_lcd(self, status):
        """Update LCD display with current status (no recalculation)"""
        if not self.lcd: 
            return
        global current_lcd_screen
        self.lcd.clear()
        try:
            if status['overall'] in ['WARNING', 'CRITICAL']:
                self.lcd.write_string(f"Status: {status['overall']}")
                self.lcd.cursor_pos = (1, 0)
                self.lcd.write_string(status['alerts'][0][:16])
            else:
                if current_lcd_screen % 4 == 0:  # Added a fourth screen for trends
                    temp = self.get_average(temp_history)
                    ph = self.get_average(ph_history)
                    # Fixed None value check
                    if temp is not None:
                        self.lcd.write_string(f"Temp: {temp:.1f}C")
                    else:
                        self.lcd.write_string("Temp: N/A")
                    self.lcd.cursor_pos = (1, 0)
                    if ph is not None:
                        self.lcd.write_string(f"pH: {ph:.1f}")
                    else:
                        self.lcd.write_string("pH: N/A")
                elif current_lcd_screen % 4 == 1:
                    ec = self.get_average(ec_history)
                    turbidity_ratio = sum(turbidity_history) / len(turbidity_history) if turbidity_history else 0
                    turbidity_status = "TURBID" if turbidity_ratio > 0.5 else "CLEAR"
                    # Fixed None value check
                    if ec is not None:
                        self.lcd.write_string(f"EC: {ec:.0f} uS/cm")
                    else:
                        self.lcd.write_string("EC: N/A")
                    self.lcd.cursor_pos = (1, 0)
                    self.lcd.write_string(f"Water: {turbidity_status}")
                elif current_lcd_screen % 4 == 2:
                    n = self.get_average(nitrogen_history)
                    p = self.get_average(phosphorus_history)
                    # Fixed None value check
                    if n is not None:
                        self.lcd.write_string(f"N: {n:.0f} mg/kg")
                    else:
                        self.lcd.write_string("N: N/A")
                    self.lcd.cursor_pos = (1, 0)
                    if p is not None:
                        self.lcd.write_string(f"P: {p:.0f} mg/kg")
                    else:
                        self.lcd.write_string("P: N/A")
                else:  # Show trends
                    temp_trend = status['trends'].get('temperature', 'STABLE')
                    ph_trend = status['trends'].get('ph', 'STABLE')
                    self.lcd.write_string(f"Temp: {temp_trend[:3]}")
                    self.lcd.cursor_pos = (1, 0)
                    self.lcd.write_string(f"pH: {ph_trend[:3]}")
                current_lcd_screen += 1
        except Exception as e:
            print(f"Error updating LCD: {e}")

    def monitor_loop(self):
        global current_status  # Use global to store the last computed status
        while self.running:
            try:
                # --- 1. READ ALL SENSORS ---
                rs485_data = self.read_rs485_sensor()
                ds18b20_temp = self.read_ds18b20_temp()
                
                # --- 2. CHECK FOR SENSOR READ FAILURE ---
                if not rs485_data:
                    print("\n" + "="*60)
                    print(f"  POND MONITORING REPORT - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
                    print("="*60)
                    print("\n❌ ERROR: Failed to read from RS485 sensor. Check wiring and power.")
                    print("Skipping assessment for this cycle.")
                    time.sleep(TEMP_READ_INTERVAL)
                    continue  # Skip to the next loop iteration

                # --- 3. UPDATE HISTORICAL DATA ---
                self.update_historical_data(rs485_data, ds18b20_temp)

                # --- 4. ASSESS WATER QUALITY ---
                status = self.get_water_quality_status(rs485_data)
                
                # Store the status for other threads to use
                current_status = status.copy()

                # --- 5. PRINT DETAILED REPORT TO CONSOLE ---
                print("\n" + "="*60)
                print(f"  POND MONITORING REPORT - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
                print("="*60)

                print("\n--- SENSOR READINGS ---")
                print(f"DS18B20 Temp:      {ds18b20_temp:.1f}°C" if ds18b20_temp is not None else "DS18B20 Temp:      N/A")
                print(f"RS485 Temp:        {rs485_data.get('temperature', 'N/A'):.1f}°C" if rs485_data.get('temperature') is not None else "RS485 Temp:        N/A")
                print(f"Combined Temp:     {self.get_average(temp_history):.1f}°C" if self.get_average(temp_history) is not None else "Combined Temp:     N/A")
                
                turbidity = self.read_turbidity()
                print(f"Turbidity:         {'TURBID' if turbidity else 'CLEAR'}" if turbidity is not None else "Turbidity:         N/A")
                
                print("\n--- RS485 PROBE DATA (UNITS: mg/kg, μS/cm) ---")
                print(f"pH:                {rs485_data.get('ph', 'N/A'):.1f}" if rs485_data.get('ph') is not None else "pH:                N/A")
                print(f"EC:                {rs485_data.get('ec', 'N/A'):.0f} μS/cm" if rs485_data.get('ec') is not None else "EC:                N/A")
                print(f"Nitrogen (N):      {rs485_data.get('nitrogen', 'N/A'):.1f} mg/kg" if rs485_data.get('nitrogen') is not None else "Nitrogen (N):      N/A")
                print(f"Phosphorus (P):    {rs485_data.get('phosphorus', 'N/A'):.1f} mg/kg" if rs485_data.get('phosphorus') is not None else "Phosphorus (P):    N/A")
                print(f"Potassium (K):     {rs485_data.get('potassium', 'N/A'):.0f} mg/kg" if rs485_data.get('potassium') is not None else "Potassium (K):     N/A")
                
                print("\n--- HISTORICAL AVERAGES ---")
                print(f"Avg Temp:          {self.get_average(temp_history):.1f}°C" if self.get_average(temp_history) is not None else "Avg Temp:          N/A")
                print(f"Avg pH:            {self.get_average(ph_history):.1f}" if self.get_average(ph_history) is not None else "Avg pH:            N/A")
                print(f"Avg EC:            {self.get_average(ec_history):.0f} μS/cm" if self.get_average(ec_history) is not None else "Avg EC:            N/A")
                print(f"Avg Nitrogen:      {self.get_average(nitrogen_history):.1f} mg/kg" if self.get_average(nitrogen_history) is not None else "Avg Nitrogen:      N/A")
                print(f"Avg Phosphorus:    {self.get_average(phosphorus_history):.1f} mg/kg" if self.get_average(phosphorus_history) is not None else "Avg Phosphorus:    N/A")
                turbidity_ratio = sum(turbidity_history) / len(turbidity_history) if turbidity_history else 0
                print(f"Turbidity Ratio:   {turbidity_ratio:.0%}" if turbidity_history else "Turbidity Ratio:   N/A")
                
                print("\n--- TRENDS ---")
                print(f"Temperature Trend:  {status['trends'].get('temperature', 'STABLE')}")
                print(f"pH Trend:          {status['trends'].get('ph', 'STABLE')}")
                print(f"Nitrogen Trend:    {status['trends'].get('nitrogen', 'STABLE')}")
                print(f"Phosphorus Trend:  {status['trends'].get('phosphorus', 'STABLE')}")
                
                print("\n--- SYSTEM ASSESSMENT ---")
                print(f"Overall Status:    {status['overall']} (Score: {status['score']}/100)")
                if status['alerts']:
                    print("Alerts Triggered:")
                    for alert in status['alerts']:
                        print(f"  - {alert}")
                if status['recommendations']:
                    print("Recommendations:")
                    for rec in status['recommendations']:
                        print(f"  - {rec}")

                # --- 6. TRIGGER LOCAL ALERTS (LEDs, Buzzer, Pump) ---
                self.update_indicators(status)

                # Update sensor data for display thread
                global sensor_data
                sensor_data = rs485_data

                time.sleep(TEMP_READ_INTERVAL)
            except KeyboardInterrupt: 
                self.running = False
                break
            except Exception as e:
                print(f"Error in monitor_loop: {e}")
                time.sleep(5)

    def display_loop(self):
        """Display loop that uses the last computed status without recalculation"""
        global current_status
        while self.running:
            try:
                # Only update LCD if we have a valid status
                if current_status:
                    self.update_lcd(current_status)
                time.sleep(LCD_REFRESH_INTERVAL)
            except Exception as e:
                print(f"Error in display_loop: {e}")
                time.sleep(5)

    def cleanup(self):
        global pwm_buzzer
        self.running = False
        self.set_leds(0, 0, 0)
        if pwm_buzzer:
            pwm_buzzer.stop()
        if self.lcd:
            self.lcd.clear()
            self.lcd.write_string("System stopped")
        
        # Ensure pump is OFF on exit
        GPIO.output(PUMP_PIN, GPIO.HIGH)
        print("Pump turned OFF.")
        
        GPIO.cleanup()
        print("\n✅ System cleanup complete")

def main():
    print("Smart Fish Pond Monitoring System v2.1 (Bug Fixes)")
    print("Initializing sensors and components...")
    try:
        monitor = SmartFishPondMonitor()
        print("✅ System initialized. Monitoring started. Press Ctrl+C to stop.")
        while monitor.running:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nStopping system...")
        monitor.cleanup()

if __name__ == "__main__":
    main()