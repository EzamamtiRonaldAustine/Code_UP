import os
import glob
import time
import serial
import RPi.GPIO as GPIO
from datetime import datetime
import minimalmodbus
from RPLCD.i2c import CharLCD
import threading
from collections import deque
import requests
import csv
import json
import logging
from pathlib import Path
import sys

# Get directory where the script is located
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))

# Configure logging with proper path handling
LOG_FILE = os.path.join(SCRIPT_DIR, 'pond_monitor.log')

# Ensure log directory exists
os.makedirs(os.path.dirname(LOG_FILE), exist_ok=True)

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s',
    handlers=[
        logging.FileHandler(LOG_FILE),
        logging.StreamHandler()
    ]
)
logger = logging.getLogger(__name__)

# Load configuration from file
CONFIG_FILE = os.path.join(SCRIPT_DIR, 'pond_config.json')
DEFAULT_CONFIG = {
    "TEMP_READ_INTERVAL": 15,
    "LCD_REFRESH_INTERVAL": 5,
    "PUMP_RUN_DURATION": {"SHORT": 120, "NORMAL": 300, "LONG": 600},
    "SMS_COOLDOWN": 300,
    "CRITICAL_DURATION": 300,
    "HISTORY_SIZE": 5,
    "THINGSPEAK": {
        "URL": "https://api.thingspeak.com/update",
        "API_KEY": "A1NXZG51WFRS96Y7",
        "SEND_INTERVAL": 60,
        "BACKUP_FILE": os.path.join(SCRIPT_DIR, 'pond_thingspeak_backup.csv')
    },
    "GPIO": {
        "TURBIDITY_PIN": 17,
        "BUZZER_PIN": 18,
        "BLUE_LED_PIN": 27,
        "YELLOW_LED_PIN": 22,
        "RED_LED_PIN": 5,
        "PUMP_PIN": 16
    },
    "SENSORS": {
        "RS485_PORT": '/dev/ttyUSB0',
        "RS485_SLAVE_ID": 1,
        "GSM_PORT": "/dev/serial0",
        "GSM_BAUDRATE": 9600
    },
    "PHONE_NUMBERS": ["+256764152908", "+256770701680"]
}

def load_config():
    """Load configuration from file or create default config."""
    if os.path.exists(CONFIG_FILE):
        try:
        with open(CONFIG_FILE, 'r') as f:
                config = json.load(f)
                # Merge with defaults to ensure all keys exist
                merged_config = DEFAULT_CONFIG.copy()
                merged_config.update(config)
                return merged_config
        except Exception as e:
            logger.error(f"Error loading config: {e}. Using defaults.")
    else:
        # Create default config file
        try:
            with open(CONFIG_FILE, 'w') as f:
                json.dump(DEFAULT_CONFIG, f, indent=2)
            logger.info(f"Created default config file at {CONFIG_FILE}")
        except Exception as e:
            logger.error(f"Error creating config file: {e}")
    
    return DEFAULT_CONFIG

# Load configuration
config = load_config()

def ensure_directory_exists(file_path):
    """Ensure the directory for the file path exists."""
    directory = os.path.dirname(file_path)
    if directory and not os.path.exists(directory):
        try:
            os.makedirs(directory)
            logger.info(f"Created directory: {directory}")
            return True
        except Exception as e:
            logger.error(f"Error creating directory {directory}: {e}")
            return False
    return True

class SmartFishPondMonitor:
    def __init__(self):
        # --- Initialize System State with Locks ---
        self.state = {
            'running': True,
            'pump': {
                'should_run': False,
                'is_running': False,
                'mode': "OFF",
                'start_time': 0
            },
            'indicators': {
                'last_status': 'GOOD',
                'lcd_screen': 0,
                'last_lcd_content': "",
                'lcd_error_count': 0
            },
            'sms': {
                'last_sent_time': 0
            },
            'critical': {
                'start_time': None,
                'sustained': False,
                'alert_sent': False
            },
            'thingspeak': {
                'last_sent_time': 0,
                'last_reading': {}
            },
            'sensor_errors': {
                'rs485_error_count': 0,
                'last_successful_read': None
            }
        }
        
        # Thread safety locks
        self.state_lock = threading.Lock()
        self.gsm_lock = threading.Lock()
        
        # Watchdog for thread monitoring
        self.thread_watchdog = {
            'monitor': time.time(),
            'display': time.time(),
            'pump': time.time(),
            'thingspeak': time.time()
        }
        
        # --- Initialize Historical Data ---
        self.history = {
            'temp': deque(maxlen=config['HISTORY_SIZE']),
            'ph': deque(maxlen=config['HISTORY_SIZE']),
            'ec': deque(maxlen=config['HISTORY_SIZE']),
            'nitrogen': deque(maxlen=config['HISTORY_SIZE']),
            'phosphorus': deque(maxlen=config['HISTORY_SIZE']),
            'turbidity': deque(maxlen=config['HISTORY_SIZE'])
        }

        # --- Initialize GPIO ---
        try:
            GPIO.setmode(GPIO.BCM)
            GPIO.setup(config['GPIO']['TURBIDITY_PIN'], GPIO.IN, pull_up_down=GPIO.PUD_UP)
            GPIO.setup(config['GPIO']['BLUE_LED_PIN'], GPIO.OUT)
            GPIO.setup(config['GPIO']['YELLOW_LED_PIN'], GPIO.OUT)
            GPIO.setup(config['GPIO']['RED_LED_PIN'], GPIO.OUT)
            GPIO.setup(config['GPIO']['BUZZER_PIN'], GPIO.OUT)
            GPIO.setup(config['GPIO']['PUMP_PIN'], GPIO.OUT)

            self.pwm_buzzer = GPIO.PWM(config['GPIO']['BUZZER_PIN'], 1000)
            self.pwm_buzzer.start(0)

            self.set_leds(0, 0, 0)
            GPIO.output(config['GPIO']['PUMP_PIN'], GPIO.HIGH)
            logger.info("GPIO initialized successfully")
        except Exception as e:
            logger.error(f"GPIO initialization failed: {e}")
            raise

        # --- Initialize Peripherals ---
        self.lcd = self._init_lcd()
        self.rs485_instrument = self._init_rs485()
        self.device_file = self._init_ds18b20()
        self.gsm = self._init_gsm()

        # --- Start Threads ---
        self.monitor_thread = threading.Thread(target=self.monitor_loop, name="Monitor")
        self.display_thread = threading.Thread(target=self.display_loop, name="Display")
        self.pump_thread = threading.Thread(target=self.pump_control_loop, name="Pump")
        self.thingspeak_thread = threading.Thread(target=self.thingspeak_loop, name="ThingSpeak")
        self.watchdog_thread = threading.Thread(target=self.watchdog_loop, name="Watchdog")

        for t in [self.monitor_thread, self.display_thread, self.pump_thread, 
                 self.thingspeak_thread, self.watchdog_thread]:
            t.daemon = True
            t.start()

    def _init_lcd(self):
        try:
            lcd = CharLCD('PCF8574', 0x27)
            lcd.clear()
            lcd.write_string("Initializing...")
            logger.info("LCD initialized")
            return lcd
        except Exception as e:
            logger.error(f"LCD initialization failed: {e}")
            return None

    def _init_rs485(self):
        try:
            instrument = minimalmodbus.Instrument(config['SENSORS']['RS485_PORT'], 
                                                   config['SENSORS']['RS485_SLAVE_ID'])
            instrument.serial.baudrate = 9600
            instrument.serial.bytesize = 8
            instrument.serial.parity = minimalmodbus.serial.PARITY_NONE
            instrument.serial.stopbits = 1
            instrument.serial.timeout = 1
            logger.info("RS485 sensor initialized")
            return instrument
        except Exception as e:
            logger.error(f"RS485 initialization failed: {e}")
            return None

    def _init_ds18b20(self):
        try:
            os.system('modprobe w1-gpio')
            os.system('modprobe w1-therm')
            base_dir = '/sys/bus/w1/devices/'
            device_folder = glob.glob(base_dir + '28-*')[0]
            device_file = device_folder + '/w1_slave'
            logger.info("DS18B20 temperature sensor initialized")
            return device_file
        except (IndexError, Exception) as e:
            logger.error(f"DS18B20 initialization failed: {e}")
            return None

    def _init_gsm(self):
        try:
            ser = serial.Serial(port=config['SENSORS']['GSM_PORT'], 
                              baudrate=config['SENSORS']['GSM_BAUDRATE'], timeout=5)
            self.send_at_command(ser, "AT", 1)
            self.send_at_command(ser, "ATE0", 1)
            self.send_at_command(ser, "AT+CMGF=1", 1)
            logger.info("GSM module initialized")
            return ser
        except Exception as e:
            logger.error(f"GSM initialization failed: {e}")
            return None

    def send_at_command(self, ser, command, delay=1):
        try:
            ser.write((command + "\r\n").encode())
            time.sleep(delay)
            return ser.read_all().decode(errors="ignore").strip()
        except Exception as e:
            logger.error(f"Error sending AT command '{command}': {e}")
            return ""

    def read_ds18b20_temp(self):
        if not self.device_file:
            return None
        try:
            with open(self.device_file, 'r') as f:
                lines = f.readlines()
            if lines and lines[0].strip().endswith('YES') and 't=' in lines[1]:
                equals_pos = lines[1].find('t=')
                if equals_pos != -1:
                    temp_c = float(lines[1][equals_pos + 2:]) / 1000.0
                    if -10 < temp_c < 60:
                        return temp_c
        except Exception as e:
            logger.error(f"Error reading DS18B20: {e}")
        return None

    def read_turbidity(self):
        try:
            return GPIO.input(config['GPIO']['TURBIDITY_PIN']) == 0
        except:
            return None

    def read_rs485_sensor(self):
        if not self.rs485_instrument:
            self.state['sensor_errors']['rs485_error_count'] += 1
            return {}
        
        try:
            data = {}
            registers = {
                'temperature': 19, 'ph': 13, 'ec': 7,
                'nitrogen': 4, 'phosphorus': 5, 'potassium': 6
            }
            
            # Read all registers in a try-except block
            try:
                temp_value = self._read_register_with_retry(registers['temperature'])
                data['temperature'] = temp_value

                for param, reg in registers.items():
                    if param == 'temperature':
                        continue
                    value = self._read_register_with_retry(reg)
                    if param == 'ph':
                        data['ph_raw'] = value
                        if value is not None and value > 0.5:
                            data[param] = self.calculate_ph(value, data.get('temperature', 25)
                        else:
                            data[param] = None
                    else:
                        data[param] = value
                
                # Reset error counter on successful read
                self.state['sensor_errors']['rs485_error_count'] = 0
                self.state['sensor_errors']['last_successful_read'] = time.time()
                return data
                
            except Exception as e:
                self.state['sensor_errors']['rs485_error_count'] += 1
                logger.error(f"RS485 sensor read error #{self.state['sensor_errors']['rs485_error_count']}: {e}")
                
                # If we've had multiple errors in a row, try to reinitialize sensor
                if self.state['sensor_errors']['rs485_error_count'] >= 3:
                    logger.warning("Multiple RS485 errors, attempting to reinitialize sensor")
                    self.rs485_instrument = self._init_rs485()
                    self.state['sensor_errors']['rs485_error_count'] = 0
                
                return {}
                
        except Exception as e:
            self.state['sensor_errors']['rs485_error_count'] += 1
            logger.error(f"Unexpected RS485 error: {e}")
            return {}

    def _read_register_with_retry(self, register, retries=2):
        for attempt in range(retries):
            try:
                value = self.rs485_instrument.read_register(register, 1, functioncode=3)
                return value
            except Exception as e:
                logger.debug(f"RS485 read attempt {attempt + 1} failed for reg {register}: {e}")
                if attempt < retries - 1:
                    time.sleep(0.1)
        return None

    def calculate_ph(self, raw_value, temperature):
        """
        Calculate pH with temperature compensation.
        Note: This is an empirical formula. For accurate measurements,
        consider sensor-specific calibration curves.
        """
        if raw_value is None or raw_value <= 0.5:
            return None
        ph = raw_value / 3.13
        temp_compensation = (temperature - 25) * 0.01
        return ph - temp_compensation

    def combine_temperatures(self, rs485_temp, ds18b20_temp):
        if rs485_temp is not None and ds18b20_temp is not None:
            return 0.6 * rs485_temp + 0.4 * ds18b20_temp
        elif rs485_temp is not None:
            return rs485_temp
        elif ds18b20_temp is not None:
            return ds18b20_temp
        return None

    def update_historical_data(self, data, ds18b20_temp):
        combined_temp = self.combine_temperatures(data.get('temperature'), ds18b20_temp)
        if combined_temp is not None:
            self.history['temp'].append(combined_temp)
        if data.get('ph') is not None:
            self.history['ph'].append(data['ph'])
        if data.get('ec') is not None:
            self.history['ec'].append(data['ec'])
        if data.get('nitrogen') is not None:
            self.history['nitrogen'].append(data['nitrogen'])
        if data.get('phosphorus') is not None:
            self.history['phosphorus'].append(data['phosphorus'])
        
        turbidity = self.read_turbidity()
        if turbidity is not None:
            self.history['turbidity'].append(1 if turbidity else 0)

    def get_average(self, history):
        if not history:
            return None
        return sum(history) / len(history)

    def get_trend(self, history):
        if len(history) < 3:
            return "STABLE"
        mid = len(history) // 2
        first_half_avg = sum(list(history)[:mid]) / mid
        second_half_avg = sum(list(history)[mid:]) / (len(history) - mid)
        diff = second_half_avg - first_half_avg
        threshold = max(0.1 * abs(first_half_avg), 0.2)
        
        if diff > threshold:
            return "INCREASING"
        elif diff < -threshold:
            return "DECREASING"
        return "STABLE"

    def get_water_quality_status(self, data, ds18b20_temp):
        self.update_historical_data(data, ds18b20_temp)
        
        status = {
            'overall': 'GOOD', 'score': 0, 'alerts': [], 
            'recommendations': set(), 'trends': {}
        }
        
        avg_temp = self.get_average(self.history['temp'])
        avg_ph = self.get_average(self.history['ph'])
        avg_ec = self.get_average(self.history['ec'])
        avg_nitrogen = self.get_average(self.history['nitrogen'])
        avg_phosphorus = self.get_average(self.history['phosphorus'])
        turbidity_ratio = sum(self.history['turbidity']) / len(self.history['turbidity']) if self.history['turbidity'] else 0
        
        status['trends']['temperature'] = self.get_trend(self.history['temp'])
        status['trends']['ph'] = self.get_trend(self.history['ph'])
        status['trends']['nitrogen'] = self.get_trend(self.history['nitrogen'])
        status['trends']['phosphorus'] = self.get_trend(self.history['phosphorus'])
        
        # Check if we have valid sensor data
        if not any([avg_temp, avg_ph, avg_ec, avg_nitrogen, avg_phosphorus]):
            status['alerts'].append('⚠️ No valid sensor data available')
            status['score'] += 50
            status['overall'] = 'WARNING'
            return status
        
        # Scoring and alert logic
        if avg_ph is None:
            status['alerts'].append('⚠️ pH sensor not in water or faulty')
            status['score'] += 30
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
        
        if avg_ec is not None and avg_ec > 1500:
            status['score'] += 30
            status['alerts'].append(f"🚨 EC {avg_ec:.0f} μS/cm is too high")
            status['recommendations'].add('Dilute with fresh water')
        
        if turbidity_ratio > 0.7:
            status['score'] += 25
            status['alerts'].append(f"⚠️ Water is consistently turbid")
            status['recommendations'].add('Check filter and perform water change')
        
        if avg_nitrogen is not None and avg_nitrogen > 5:
            status['score'] += 30
            status['alerts'].append(f"🚨 Nitrogen extremely high: {avg_nitrogen:.1f} mg/kg")
            status['recommendations'].add('Reduce feeding and perform water change')
        
        # Updated phosphorus threshold to match validation range
        if avg_phosphorus is not None and avg_phosphorus > 15:
            status['score'] += 30
            status['alerts'].append(f"🚨 Phosphorus extremely high: {avg_phosphorus:.1f} mg/kg")
            status['recommendations'].add('Reduce feeding and perform water change')
        
        if status['score'] >= 70:
            status['overall'] = 'CRITICAL'
        elif status['score'] >= 40:
            status['overall'] = 'WARNING'
        
        return status

    def set_leds(self, blue, yellow, red):
        GPIO.output(config['GPIO']['BLUE_LED_PIN'], blue)
        GPIO.output(config['GPIO']['YELLOW_LED_PIN'], yellow)
        GPIO.output(config['GPIO']['RED_LED_PIN'], red)

    def update_indicators(self, status):
        with self.state_lock:
            self.set_leds(0, 0, 0)
            self.pwm_buzzer.ChangeDutyCycle(0)

            if status['overall'] == 'GOOD':
                self.set_leds(1, 0, 0)
                self.state['pump']['should_run'] = False
                self.state['pump']['mode'] = "OFF"
            elif status['overall'] == 'WARNING':
                self.set_leds(0, 1, 0)
                threading.Timer(0.2, lambda: self.pwm_buzzer.ChangeDutyCycle(50)).start()
                threading.Timer(0.4, lambda: self.pwm_buzzer.ChangeDutyCycle(0)).start()
                threading.Timer(0.4, lambda: self.pwm_buzzer.ChangeDutyCycle(0)).start()
                self.state['pump']['should_run'] = False
            elif status['overall'] == 'CRITICAL':
                self.set_leds(0, 0, 1)
                threading.Timer(1.0, lambda: self.pwm_buzzer.ChangeDutyCycle(50)).start()
                threading.Timer(1.2, lambda: self.pwm_buzzer.ChangeDutyCycle(0)).start()
                
                if not self.state['pump']['is_running']:
                    self.state['pump']['should_run'] = True
                    self._determine_pump_mode(status)

    def _determine_pump_mode(self, status):
        avg_temp = self.get_average(self.history['temp'])
        avg_ph = self.get_average(self.history['ph'])
        turbidity_ratio = sum(self.history['turbidity']) / len(self.history['turbidity']) if self.history['turbidity'] else 0
        
        if avg_temp is not None and (avg_temp < 15 or avg_temp > 32):
            self.state['pump']['mode'] = "LONG"
        elif avg_ph is not None and (avg_ph < 6.0 or avg_ph > 9.0):
            self.state['pump']['mode'] = "SHORT"
        elif turbidity_ratio > 0.7:
            self.state['pump']['mode'] = "NORMAL"
        else:
            self.state['pump']['mode'] = "NORMAL"

    def handle_critical_state(self, status):
        """Consolidated method to handle critical state transitions and SMS alerts."""
        with self.state_lock:
            current_time = time.time()
            
            if status['overall'] == 'CRITICAL':
                if not self.state['critical']['sustained']:
                    # Start tracking critical condition
                    self.state['critical']['start_time'] = current_time
                    self.state['critical']['sustained'] = True
                    self.state['critical']['alert_sent'] = False
                    logger.info("Critical condition detected. Starting timer before SMS alert.")
                
                # Check if sustained critical duration has passed
                elif (not self.state['critical']['alert_sent'] and 
                      current_time - self.state['critical']['start_time'] > config['CRITICAL_DURATION']):
                    logger.info("Sustained critical condition confirmed. Sending SMS alert.")
                    self._send_sms_message(status)
                    self.state['sms']['last_sent_time'] = current_time
                    self.state['critical']['alert_sent'] = True
            
            else:
                # No longer critical
                if self.state['critical']['sustained']:
                    logger.info("Condition recovered. Resetting critical state.")
                    self.state['critical']['start_time'] = None
                    self.state['critical']['sustained'] = False
                    self.state['critical']['alert_sent'] = False

    def _send_sms_message(self, status):
        """Send SMS alert to configured phone numbers."""
        if not self.gsm:
            logger.error("GSM module not available for SMS")
            return
        
        message = f"🚨 POND ALERT ({status['overall']})\n"
        message += f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M')}\n\n"
        message += "Critical Issues:\n" + "\n".join(status['alerts'][:3])
        message += f"\nActions:\n" + "\n".join(list(status['recommendations'])[:2])

        with self.gsm_lock:
            for phone in config['PHONE_NUMBERS']:
                try:
                    self.gsm.write(f'AT+CMGS="{phone}"\r\n'.encode())
                    time.sleep(1)
                    self.gsm.write(message.encode())
                    time.sleep(0.5)
                    self.gsm.write(b'\x1A')
                    time.sleep(5)
                    final_response = self.gsm.read_all().decode(errors="ignore")
                    if "+CMGS:" in final_response:
                        logger.info(f"SMS sent to {phone}")
                    else:
                        logger.error(f"SMS failed to {phone}: {final_response.strip()}")
                except Exception as e:
                    logger.error(f"Error sending SMS to {phone}: {e}")

    def pump_control_loop(self):
        """Control pump operation based on system state."""
        while self.state['running']:
            try:
                with self.state_lock:
                    if self.state['pump']['should_run'] and not self.state['pump']['is_running']:
                        logger.info(f"Activating PUMP in {self.state['pump']['mode']} mode.")
                        GPIO.output(config['GPIO']['PUMP_PIN'], GPIO.LOW)
                        self.state['pump']['is_running'] = True
                        self.state['pump']['start_time'] = time.time()
                        self.state['pump']['should_run'] = False
                    
                    if self.state['pump']['is_running']:
                        run_duration = config['PUMP_RUN_DURATION'].get(self.state['pump']['mode'], 300)
                        if time.time() - self.state['pump']['start_time'] > run_duration:
                            logger.info(f"{self.state['pump']['mode']} pump cycle complete. Turning PUMP OFF.")
                            GPIO.output(config['GPIO']['PUMP_PIN'], GPIO.HIGH)
                            self.state['pump']['is_running'] = False
                            self.state['pump']['mode'] = "OFF"
                
                self.thread_watchdog['pump'] = time.time()
                time.sleep(1)
            except Exception as e:
                logger.error(f"Error in pump_control_loop: {e}")
                time.sleep(5)

    def _update_lcd_content(self, status):
        """Update LCD display with current status."""
        if not self.lcd:
            return
        
        try:
            content = ""
            if status['overall'] in ['WARNING', 'CRITICAL']:
                # For critical/warning states, show alert with asterisks for emphasis
                content = f"* {status['overall']} *\n{status['alerts'][0][:16]}"
            else:
                screen = self.state['indicators']['lcd_screen'] % 4
                if screen == 0:
                    temp = self.get_average(self.history['temp'])
                    ph = self.get_average(self.history['ph'])
                    content = f"Temp: {temp:.1f}C\npH: {ph:.1f}" if temp is not None and ph is not None else "Temp: N/A\npH: N/A"
                elif screen == 1:
                    ec = self.get_average(self.history['ec'])
                    turbidity_ratio = sum(self.history['turbidity']) / len(self.history['turbidity']) if self.history['turbidity'] else 0
                    turbidity_status = "TURBID" if turbidity_ratio > 0.5 else "CLEAR"
                    content = f"EC: {ec:.0f} uS/cm\nWater: {turbidity_status}" if ec is not None else "EC: N/A\nWater: N/A"
                elif screen == 2:
                    n = self.get_average(self.history['nitrogen'])
                    p = self.get_average(self.history['phosphorus'])
                    content = f"N: {n:.0f} mg/kg\nP: {p:.0f} mg/kg" if n is not None and p is not None else "N: N/A\nP: N/A"
                else:
                    temp_trend = status['trends'].get('temperature', 'STABLE')
                    ph_trend = status['trends'].get('ph', 'STABLE')
                    content = f"Temp: {temp_trend[:3]}\npH: {ph_trend[:3]}"
            
            if content != self.state['indicators']['last_lcd_content']:
                self.lcd.clear()
                self.lcd.write_string(content)
                self.state['indicators']['last_lcd_content'] = content
                
            # Reset error counter on successful update
            self.state['indicators']['lcd_error_count'] = 0
            
        except Exception as e:
            self.state['indicators']['lcd_error_count'] += 1
            logger.error(f"LCD error #{self.state['indicators']['lcd_error_count']}: {e}")
            
            # If we've had multiple errors, try to reinitialize LCD
            if self.state['indicators']['lcd_error_count'] >= 3:
                logger.warning("Multiple LCD errors, attempting to reinitialize")
                try:
                    if self.lcd:
                        self.lcd.close()
                    self.lcd = self._init_lcd()
                    self.state['indicators']['lcd_error_count'] = 0
                except Exception as init_error:
                    logger.error(f"Failed to reinitialize LCD: {init_error}")

    def display_loop(self):
        """Handle LCD display updates."""
        while self.state['running']:
            try:
                with self.state_lock:
                    if self.state.get('last_status_full'):
                        self._update_lcd_content(self.state['last_status_full'])
                    self.state['indicators']['lcd_screen'] += 1
                
                self.thread_watchdog['display'] = time.time()
                time.sleep(config['LCD_REFRESH_INTERVAL'])
            except Exception as e:
                logger.error(f"Error in display_loop: {e}")
                time.sleep(5)

    def validate_sensor_data(self, data):
        """Validate sensor data before sending to ThingSpeak."""
        valid_ranges = {
            'temperature': (-40, 80),
            'ph': (0, 14),
            'ec': (0, 5000),
            'nitrogen': (0, 100),
            'phosphorus': (0, 20),  # Increased max value from 10 to 20
            'quality_score': (0, 150)
        }
        
        # Flag to track if any data is out of range
        out_of_range = False
        
        for param, (min_val, max_val) in valid_ranges.items():
            value = data.get(param)
            # Skip validation if value is None - this is acceptable
            if value is None:
                continue
                
            try:
                val_float = float(value)
                if not (min_val <= val_float <= max_val):
                    logger.debug(f"{param} out of range: {val_float} (expected {min_val}-{max_val})")
                    
                    # For phosphorus, cap value at max_range instead of rejecting
                    if param == 'phosphorus' and val_float > max_val:
                        data[param] = max_val
                        logger.info(f"Capping {param} at {max_val}")
                        out_of_range = False  # Don't reject data since we're fixing it
                    else:
                        out_of_range = True
            except (ValueError, TypeError):
                logger.debug(f"{param} validation error: {value} - {e}")
                out_of_range = True
        
        # Validate quality_status
        quality_status = data.get('quality_status')
        if quality_status not in ['GOOD', 'WARNING', 'CRITICAL']:
            logger.debug(f"Invalid quality_status: {quality_status}")
            # Default to 'GOOD' if status is invalid
            data['quality_status'] = 'GOOD'
            logger.debug("Defaulting quality_status to 'GOOD'")
        
        # Return True if no critical errors (we're handling phosphorus by capping)
        return not out_of_range

    def has_any_valid_data(self, data):
        """Check if we have any valid sensor data to send to ThingSpeak."""
        return any(v is not None for k, v in data.items() 
                   if k not in ['quality_score', 'quality_status'])

    def send_to_thingspeak(self, data):
        """Send sensor data to ThingSpeak. Returns True on success."""
        if not config['THINGSPEAK']['API_KEY']:
            logger.warning("ThingSpeak API key not configured")
            return False
        
        # Validate data before sending
        if not self.validate_sensor_data(data):
            logger.debug("Data validation failed. Skipping send.")
            return False
        
        # Build payload, only including non-None values
        payload = {"api_key": config['THINGSPEAK']['API_KEY']}
        
        if data.get('temperature') is not None:
            payload['field1'] = data['temperature']
        if data.get('ph') is not None:
            payload['field2'] = data['ph']
        if data.get('ec') is not None:
            payload['field3'] = data['ec']
        if data.get('nitrogen') is not None:
            payload['field4'] = data['nitrogen']
        if data.get('phosphorus') is not None:
            payload['field5'] = data['phosphorus']
        if data.get('turbidity') is not None:
            payload['field6'] = 1 if data.get('turbidity') else 0
        if data.get('quality_score') is not None:
            payload['field7'] = data['quality_score']
        if data.get('quality_status') is not None:
            payload['field8'] = data['quality_status']
        
        try:
            r = requests.get(config['THINGSPEAK']['URL'], params=payload, timeout=10)
            if r.status_code == 200 and r.text.strip().isdigit():
                logger.info(f"Data sent to ThingSpeak (Entry ID: {r.text.strip()})")
                return True
            else:
                logger.error(f"ThingSpeak error: {r.status_code} - {r.text}")
                return False
        except requests.exceptions.RequestException as e:
            logger.error(f"Error connecting to ThingSpeak: {e}")
            return False
        except Exception as e:
            logger.error(f"Unexpected error: {e}")
            return False

    def save_thingspeak_backup(self, timestamp, data):
        """Save failed readings to local CSV backup."""
        backup_file = config['THINGSPEAK']['BACKUP_FILE']
        
        # Ensure directory exists
        if not ensure_directory_exists(backup_file):
            # Fallback to current directory if original path fails
            backup_file = os.path.basename(backup_file)
            logger.warning(f"Using fallback backup file: {backup_file}")
        
        header_needed = not os.path.exists(backup_file)
        try:
            with open(backup_file, "a", newline="") as f:
                writer = csv.writer(f)
                if header_needed:
                    writer.writerow(["timestamp", "temperature", "ph", "ec", "nitrogen", 
                                   "phosphorus", "turbidity", "quality_score", "quality_status"])
                writer.writerow([
                    timestamp,
                    data.get('temperature'),
                    data.get('ph'),
                    data.get('ec'),
                    data.get('nitrogen'),
                    data.get('phosphorus'),
                    data.get('turbidity'),
                    data.get('quality_score'),
                    data.get('quality_status')
                ])
            logger.info(f"Successfully saved backup to {backup_file}")
        except Exception as e:
            logger.error(f"Error saving ThingSpeak backup: {e}")

    def flush_thingspeak_backup(self):
        """Attempt to resend backed-up readings to ThingSpeak."""
        backup_file = config['THINGSPEAK']['BACKUP_FILE']
        if not os.path.exists(backup_file):
            return
        
        rows_to_keep = []
        try:
            with open(backup_file, "r", newline="") as f:
                reader = csv.reader(f)
                headers = next(reader, None)  # Skip header
                for row in reader:
                    if len(row) >= 9:  # Ensure valid data row
                        try:
                            row_dict = {
                                'timestamp': row[0],
                                'temperature': row[1],
                                'ph': row[2],
                                'ec': row[3],
                                'nitrogen': row[4],
                                'phosphorus': row[5],
                                'turbidity': row[6],
                                'quality_score': row[7],
                                'quality_status': row[8]
                            }
                            rows_to_keep.append(row_dict)
                        except (ValueError, IndexError):
                            continue
        except Exception as e:
            logger.error(f"Error reading backup file: {e}")
            return

        if not rows_to_keep:
            try:
                os.remove(backup_file)
            except OSError:
                pass
            return

        still_failed = []
        for row in rows_to_keep:
            data = {k: (float(v) if v and k != 'quality_status' else v) 
                   for k, v in row.items() if k != 'timestamp'}
            success = self.send_to_thingspeak(data)
            if not success:
                still_failed.append(row)
            else:
                logger.info(f"Flushed backup: {row['timestamp']}")
            time.sleep(15)  # Respect ThingSpeak rate limit

        # Write back only failed entries
        if still_failed:
            try:
                with open(backup_file, "w", newline="") as f:
                    writer = csv.writer(f)
                    writer.writerow(["timestamp", "temperature", "ph", "ec", "nitrogen", 
                                  "phosphorus", "turbidity", "quality_score", "quality_status"])
                    for row in still_failed:
                        writer.writerow(row.values())
            except Exception as e:
                logger.error(f"Error writing backup file: {e}")
        else:
            try:
                os.remove(backup_file)
                logger.info("All backup data sent to ThingSpeak successfully")
            except OSError:
                pass

    def thingspeak_loop(self):
        """Send sensor data to ThingSpeak at regular intervals."""
        while self.state['running']:
            try:
                with self.state_lock:
                    if time.time() - self.state['thingspeak']['last_sent_time'] >= config['THINGSPEAK']['SEND_INTERVAL']:
                        # Prepare data from current readings
                        data = {
                            'temperature': self.get_average(self.history['temp']),
                            'ph': self.get_average(self.history['ph']),
                            'ec': self.get_average(self.history['ec']),
                            'nitrogen': self.get_average(self.history['nitrogen']),
                            'phosphorus': self.get_average(self.history['phosphorus']),
                            'turbidity': sum(self.history['turbidity']) / len(self.history['turbidity']) if self.history['turbidity'] else 0,
                            'quality_score': self.state.get('last_status_full', {}).get('score', 0),
                            'quality_status': self.state.get('last_status_full', {}).get('overall', 'GOOD')  # Default to GOOD
                        }

                        # Only send if we have at least some valid data
                        if self.has_any_valid_data(data):
                            # Try to flush any backed-up data first
                            self.flush_thingspeak_backup()

                            # Send current reading
                            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                            if self.send_to_thingspeak(data):
                                self.state['thingspeak']['last_sent_time'] = time.time()
                            else:
                                logger.info("Saving to local backup...")
                                self.save_thingspeak_backup(timestamp, data)
                        else:
                                logger.info("Waiting for valid sensor data before sending to ThingSpeak")

                self.thread_watchdog['thingspeak'] = time.time()
                time.sleep(5)  # Check every 5 seconds if it's time to send
            except Exception as e:
                logger.error(f"Error in thingspeak_loop: {e}")
                time.sleep(10)

    def watchdog_loop(self):
        """Monitor thread health and restart if necessary."""
        while self.state['running']:
            try:
                current_time = time.time()
                timeout = 60  # 60 seconds timeout for threads
                
                for thread_name, last_update in self.thread_watchdog.items():
                    if current_time - last_update > timeout:
                        logger.error(f"Thread {thread_name} appears to be stuck!")
                        # In a production system, you might want to restart the thread here
                
                time.sleep(30)  # Check every 30 seconds
            except Exception as e:
                logger.error(f"Error in watchdog_loop: {e}")
                time.sleep(30)

    def monitor_loop(self):
        """Main monitoring loop with detailed console output."""
        # Initial message for first cycle
        first_cycle = True
        
        while self.state['running']:
            try:
                # --- 1. READ ALL SENSORS ---
                rs485_data = self.read_rs485_sensor()
                ds18b20_temp = self.read_ds18b20_temp()
                
                # --- 2. CHECK FOR SENSOR READ FAILURE ---
                if not rs485_data:
                    if first_cycle:
                        print("\n" + "="*60)
                        print(f"  POND MONITORING REPORT - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
                        print("="*60)
                        print("\n❌ ERROR: Failed to read from RS485 sensor. Check wiring and power.")
                        print("Waiting for sensor data...")
                        first_cycle = False
                    time.sleep(config['TEMP_READ_INTERVAL'])
                    continue  # Skip to next loop iteration

                # --- 3. UPDATE HISTORICAL DATA ---
                self.update_historical_data(rs485_data, ds18b20_temp)

                # --- 4. ASSESS WATER QUALITY ---
                status = self.get_water_quality_status(rs485_data, ds18b20_temp)
                
                # Store status for other threads to use
                with self.state_lock:
                    self.state['last_status_full'] = status

                # --- 5. PRINT DETAILED REPORT TO CONSOLE ---
                print("\n" + "="*60)
                print(f"  POND MONITORING REPORT - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
                print("="*60)

                print("\n--- SENSOR READINGS ---")
                print(f"DS18B20 Temp:      {ds18b20_temp:.1f}°C" if ds18b20_temp is not None else "DS18B20 Temp:      N/A")
                print(f"RS485 Temp:        {rs485_data.get('temperature', 'N/A'):.1f}°C" if rs485_data.get('temperature') is not None else "RS485 Temp:        N/A")
                print(f"Combined Temp:     {self.get_average(self.history['temp']):.1f}°C" if self.get_average(self.history['temp']) is not None else "Combined Temp:     N/A")
                
                turbidity = self.read_turbidity()
                print(f"Turbidity:         {'TURBID' if turbidity else 'CLEAR'}" if turbidity is not None else "Turbidity:         N/A")
                
                print("\n--- RS485 PROBE DATA (UNITS: mg/kg, μS/cm) ---")
                print(f"pH:                {rs485_data.get('ph', 'N/A'):.1f}" if rs485_data.get('ph') is not None else "pH:                N/A")
                print(f"EC:                {rs485_data.get('ec', 'N/A'):.0f} μS/cm" if rs485_data.get('ec') is not None else "EC:                N/A")
                print(f"Nitrogen (N):      {rs485_data.get('nitrogen', 'N/A'):.1f} mg/kg" if rs485_data.get('nitrogen') is not None else "Nitrogen (N):      N/A")
                print(f"Phosphorus (P):    {rs485_data.get('phosphorus', 'N/A'):.1f} mg/kg" if rs485_data.get('phosphorus', 'N/A') is not None else "Phosphorus (P):    N/A")
                print(f"Potassium (K):     {rs485_data.get('potassium', 'N/A'):.0f} mg/kg" if rs485_data.get('potassium', 'N/A') is not None else "Potassium (K):     N/A")
                
                print("\n--- HISTORICAL AVERAGES ---")
                print(f"Avg Temp:          {self.get_average(self.history['temp']):.1f}°C" if self.get_average(self.history['temp']) is not None else "Avg Temp:          N/A")
                print(f"Avg pH:            {self.get_average(self.history['ph']):.1f}" if self.get_average(self.history['ph']) is not None else "Avg pH:            N/A")
                print(f"Avg EC:            {self.get_average(self.history['ec']):.0f} μS/cm" if self.get_average(self.history['ec']) is not None else "Avg EC:            N/A")
                print(f"Avg Nitrogen:      {self.get_average(self.history['nitrogen']):.1f} mg/kg" if self.get_average(self.history['nitrogen']) is not None else "Avg Nitrogen:      N/A")
                print(f"Avg Phosphorus:    {self.get_average(self.history['phosphorus'):.1f} mg/kg" if self.get_average(self.history['phosphorus']) is not None else "Avg Phosphorus:    N/A")
                turbidity_ratio = sum(self.history['turbidity']) / len(self.history['turbidity']) if self.history['turbidity'] else 0
                print(f"Turbidity Ratio:   {turbidity_ratio:.0%}" if self.history['turbidity'] else "Turbidity Ratio:   N/A")
                
                print("\n--- TRENDS ---")
                print(f"Temperature Trend:  {status['trends'].get('temperature', 'STABLE')
                print(f"pH Trend:          {status['trends'].get('ph', 'STABLE')
                print(f"Nitrogen Trend:    {status['trends'].get('nitrogen', 'STABLE')
                print(f"Phosphorus Trend:  {status['trends'].get('phosphorus', 'STABLE')
                
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

                # --- 6. HANDLE CRITICAL STATE AND SMS ALERTS ---
                self.handle_critical_state(status)
                
                # --- 7. TRIGGER LOCAL ALERTS (LEDs, Buzzer, Pump) ---
                self.update_indicators(status)
                
                # --- 8. UPDATE STATE FOR OTHER THREADS ---
                with self.state_lock:
                    self.state['indicators']['last_status'] = status['overall']

                self.thread_watchdog['monitor'] = time.time()
                time.sleep(config['TEMP_READ_INTERVAL'])
            except KeyboardInterrupt:
                self.state['running'] = False
                break
            except Exception as e:
                logger.error(f"Error in monitor_loop: {e}")
                time.sleep(5)

    def cleanup(self):
        """Clean up resources on shutdown."""
        logger.info("Starting cleanup...")
        self.state['running'] = False
        
        # Wait for threads to finish with shorter timeout and ignore KeyboardInterrupt
        for t in [self.monitor_thread, self.display_thread, self.pump_thread, 
                 self.thingspeak_thread, self.watchdog_thread]:
            if t.is_alive():
                try:
                    t.join(timeout=2)
                except KeyboardInterrupt:
                    pass
        
        self.set_leds(0, 0, 0)
        if self.pwm_buzzer:
            self.pwm_buzzer.stop()
        if self.lcd:
            try:
                self.lcd.clear()
                self.lcd.write_string("System stopped")
            except:
                pass  # Ignore LCD errors during cleanup
        
        GPIO.output(config['GPIO']['PUMP_PIN'], GPIO.HIGH)
        logger.info("Pump turned OFF.")
        
        if self.gsm:
            self.gsm.close()
            logger.info("GSM module closed.")
        
        GPIO.cleanup()
        logger.info("System cleanup complete")

def main():
    logger.info("Smart Fish Pond Monitoring System v5.10 (Fixed ThingSpeak)")
    try:
        monitor = SmartFishPondMonitor()
        logger.info("System initialized. Monitoring started. Press Ctrl+C to stop.")
        while monitor.state['running']:
            time.sleep(1)
    except KeyboardInterrupt:
        logger.info("Stopping system...")
        monitor.cleanup()
    except Exception as e:
        logger.error(f"Fatal error: {e}")
        monitor.cleanup()

if __name__ == "__main__":
    main()