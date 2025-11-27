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
import socket
import subprocess

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
        "API_KEY": "",
        "SEND_INTERVAL": 60,
        "BACKUP_FILE": os.path.join(SCRIPT_DIR, 'pond_thingspeak_backup.csv'),
        "MAX_RETRIES": 3,
        "RETRY_DELAY": 30,
        "MAX_RETRY_DELAY": 300
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

def check_network_connectivity():
    """Check if the device has internet connectivity by resolving Google's DNS."""
    try:
        socket.gethostbyname('8.8.8.8')
        return True
    except socket.gaierror:
        logger.warning("Network connectivity check failed: Name resolution failed.")
        return False
    except Exception as e:
        logger.error(f"Error during network check: {e}")
        return False

def restart_network_interface():
    """Attempt to restart the network interface using systemd (common on RPi OS)."""
    try:
        logger.info("Attempting to restart network interface 'wlan0' and 'eth0'...")
        subprocess.run(["sudo", "ifdown", "wlan0", "eth0"], check=True, stderr=subprocess.PIPE, stdout=subprocess.PIPE)
        subprocess.run(["sudo", "ifup", "wlan0", "eth0"], check=True, stderr=subprocess.PIPE, stdout=subprocess.PIPE)
        try:
            subprocess.run(["sudo", "systemctl", "restart", "NetworkManager"], check=True)
        except subprocess.CalledProcessError:
             subprocess.run(["sudo", "systemctl", "restart", "networking"], check=True)
        
        logger.info("Network interface restart commands issued. Waiting 15 seconds for connection...")
        time.sleep(15)
        if check_network_connectivity():
            logger.info("Network connectivity restored after restart.")
            return True
        else:
            logger.warning("Network connectivity still down after restart attempt.")
            return False
    except subprocess.CalledProcessError as e:
        logger.error(f"Failed to restart network interface commands: {e.stderr.decode().strip()}")
        return False
    except Exception as e:
        logger.error(f"An unexpected error occurred during network restart: {e}")
        return False

def load_config():
    """Load configuration from file or create default config."""
    if os.path.exists(CONFIG_FILE):
        try:
            with open(CONFIG_FILE, 'r') as f:
                user_config = json.load(f)
                # Merge with defaults to ensure all keys exist
                merged_config = DEFAULT_CONFIG.copy()
                # Deep merge for nested dictionaries
                for key, value in user_config.items():
                    if key in merged_config and isinstance(merged_config[key], dict) and isinstance(value, dict):
                        merged_config[key].update(value)
                    else:
                        merged_config[key] = value
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

def ensure_backup_file_exists():
    """Create the ThingSpeak backup file if it doesn't exist."""
    backup_file = config.get('THINGSPEAK', {}).get('BACKUP_FILE')
    if not backup_file:
        logger.error("BACKUP_FILE not found in configuration.")
        return False
        
    if not os.path.exists(backup_file):
        logger.info(f"Backup file not found. Creating new one at: {backup_file}")
        try:
            ensure_directory_exists(backup_file)
            with open(backup_file, 'w', newline='') as f:
                writer = csv.writer(f)
                writer.writerow(["timestamp", "temperature", "ph", "ec", "nitrogen",
                              "phosphorus", "turbidity", "quality_score", "quality_status"])
            logger.info(f"Successfully created new backup file.")
            return True
        except Exception as e:
            logger.error(f"Failed to create backup file: {e}")
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
                'lcd_error_count': 0,
                'lcd_available': True
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
                'last_reading': {},
                'connection_errors': 0,
                'last_network_check': 0,
                'network_error_count': 0
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
            'temp': deque(maxlen=config.get('HISTORY_SIZE', 5)),
            'ph': deque(maxlen=config.get('HISTORY_SIZE', 5)),
            'ec': deque(maxlen=config.get('HISTORY_SIZE', 5)),
            'nitrogen': deque(maxlen=config.get('HISTORY_SIZE', 5)),
            'phosphorus': deque(maxlen=config.get('HISTORY_SIZE', 5)),
            'turbidity': deque(maxlen=config.get('HISTORY_SIZE', 5))
        }

        # --- Initialize GPIO ---
        try:
            GPIO.setmode(GPIO.BCM)
            GPIO.setup(config.get('GPIO', {}).get('TURBIDITY_PIN', 17), GPIO.IN, pull_up_down=GPIO.PUD_UP)
            GPIO.setup(config.get('GPIO', {}).get('BLUE_LED_PIN', 27), GPIO.OUT)
            GPIO.setup(config.get('GPIO', {}).get('YELLOW_LED_PIN', 22), GPIO.OUT)
            GPIO.setup(config.get('GPIO', {}).get('RED_LED_PIN', 5), GPIO.OUT)
            GPIO.setup(config.get('GPIO', {}).get('BUZZER_PIN', 18), GPIO.OUT)
            GPIO.setup(config.get('GPIO', {}).get('PUMP_PIN', 16), GPIO.OUT)

            self.pwm_buzzer = GPIO.PWM(config.get('GPIO', {}).get('BUZZER_PIN', 18), 1000)
            self.pwm_buzzer.start(0)

            self.set_leds(0, 0, 0)
            GPIO.output(config.get('GPIO', {}).get('PUMP_PIN', 16), GPIO.HIGH)
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
        max_retries = 3
        for attempt in range(max_retries):
            try:
                lcd = CharLCD('PCF8574', 0x27)
                lcd.clear()
                lcd.write_string("Initializing...")
                logger.info("LCD initialized")
                return lcd
            except Exception as e:
                logger.error(f"LCD initialization failed (attempt {attempt + 1}/{max_retries}): {e}")
                if attempt < max_retries - 1:
                    time.sleep(2)

        with self.state_lock:
            self.state['indicators']['lcd_available'] = False
        return None

    def _init_rs485(self):
        try:
            instrument = minimalmodbus.Instrument(config.get('SENSORS', {}).get('RS485_PORT', '/dev/ttyUSB0'),
                                                   config.get('SENSORS', {}).get('RS485_SLAVE_ID', 1))
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
            device_folders = glob.glob(base_dir + '28-*')
            if not device_folders:
                logger.error("No DS18B20 temperature sensor found. Check wiring and kernel modules.")
                return None
            device_folder = device_folders[0]
            device_file = device_folder + '/w1_slave'
            logger.info("DS18B20 temperature sensor initialized")
            return device_file
        except (IndexError, Exception) as e:
            logger.error(f"DS18B20 initialization failed: {e}")
            return None

    def _init_gsm(self):
        try:
            ser = serial.Serial(port=config.get('SENSORS', {}).get('GSM_PORT', "/dev/serial0"),
                              baudrate=config.get('SENSORS', {}).get('GSM_BAUDRATE', 9600), timeout=5)
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
            return GPIO.input(config.get('GPIO', {}).get('TURBIDITY_PIN', 17)) == 0
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
                            data[param] = self.calculate_ph(value, data.get('temperature', 25))
                        else:
                            data[param] = None
                    else:
                        data[param] = value

                self.state['sensor_errors']['rs485_error_count'] = 0
                self.state['sensor_errors']['last_successful_read'] = time.time()
                return data

            except Exception as e:
                self.state['sensor_errors']['rs485_error_count'] += 1
                logger.error(f"RS485 sensor read error #{self.state['sensor_errors']['rs485_error_count']}: {e}")

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

        if not any([avg_temp, avg_ph, avg_ec, avg_nitrogen, avg_phosphorus]):
            status['alerts'].append('⚠️ No valid sensor data available')
            status['score'] += 50
            status['overall'] = 'WARNING'
            return status

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
        GPIO.output(config.get('GPIO', {}).get('BLUE_LED_PIN', 27), blue)
        GPIO.output(config.get('GPIO', {}).get('YELLOW_LED_PIN', 22), yellow)
        GPIO.output(config.get('GPIO', {}).get('RED_LED_PIN', 5), red)

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
        with self.state_lock:
            current_time = time.time()

            if status['overall'] == 'CRITICAL':
                if not self.state['critical']['sustained']:
                    self.state['critical']['start_time'] = current_time
                    self.state['critical']['sustained'] = True
                    self.state['critical']['alert_sent'] = False
                    logger.info("Critical condition detected. Starting timer before SMS alert.")

                elif (not self.state['critical']['alert_sent'] and
                      current_time - self.state['critical']['start_time'] > config.get('CRITICAL_DURATION', 300)):
                    logger.info("Sustained critical condition confirmed. Sending SMS alert.")
                    self._send_sms_message(status)
                    self.state['sms']['last_sent_time'] = current_time
                    self.state['critical']['alert_sent'] = True

            else:
                if self.state['critical']['sustained']:
                    logger.info("Condition recovered. Resetting critical state.")
                    self.state['critical']['start_time'] = None
                    self.state['critical']['sustained'] = False
                    self.state['critical']['alert_sent'] = False

    def _send_sms_message(self, status):
        if not self.gsm:
            logger.error("GSM module not available for SMS")
            return

        message = f"🚨 POND ALERT ({status['overall']})\n"
        message += f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M')}\n\n"
        message += "Critical Issues:\n" + "\n".join(status['alerts'][:3])
        message += f"\nActions:\n" + "\n".join(list(status['recommendations'])[:2])

        with self.gsm_lock:
            for phone in config.get('PHONE_NUMBERS', []):
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
        while self.state['running']:
            try:
                with self.state_lock:
                    if self.state['pump']['should_run'] and not self.state['pump']['is_running']:
                        logger.info(f"Activating PUMP in {self.state['pump']['mode']} mode.")
                        GPIO.output(config.get('GPIO', {}).get('PUMP_PIN', 16), GPIO.LOW)
                        self.state['pump']['is_running'] = True
                        self.state['pump']['start_time'] = time.time()
                        self.state['pump']['should_run'] = False

                    if self.state['pump']['is_running']:
                        run_duration = config.get('PUMP_RUN_DURATION', {}).get(self.state['pump']['mode'], 300)
                        if time.time() - self.state['pump']['start_time'] > run_duration:
                            logger.info(f"{self.state['pump']['mode']} pump cycle complete. Turning PUMP OFF.")
                            GPIO.output(config.get('GPIO', {}).get('PUMP_PIN', 16), GPIO.HIGH)
                            self.state['pump']['is_running'] = False
                            self.state['pump']['mode'] = "OFF"

                self.thread_watchdog['pump'] = time.time()
                time.sleep(1)
            except Exception as e:
                logger.error(f"Error in pump_control_loop: {e}")
                time.sleep(5)

    def _update_lcd_content(self, status):
        with self.state_lock:
            if not self.state['indicators']['lcd_available'] or not self.lcd:
                return

        try:
            content = ""
            if status['overall'] in ['WARNING', 'CRITICAL']:
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

            self.state['indicators']['lcd_error_count'] = 0

        except Exception as e:
            self.state['indicators']['lcd_error_count'] += 1
            logger.error(f"LCD error #{self.state['indicators']['lcd_error_count']}: {e}")

            if self.state['indicators']['lcd_error_count'] >= 3:
                logger.warning("Multiple LCD errors, attempting to reinitialize")
                try:
                    if self.lcd:
                        self.lcd.close()
                    self.lcd = self._init_lcd()
                    self.state['indicators']['lcd_error_count'] = 0
                except Exception as init_error:
                    logger.error(f"Failed to reinitialize LCD: {init_error}")
                    with self.state_lock:
                        self.state['indicators']['lcd_available'] = False

    def display_loop(self):
        while self.state['running']:
            try:
                with self.state_lock:
                    if self.state.get('last_status_full'):
                        self._update_lcd_content(self.state['last_status_full'])
                    self.state['indicators']['lcd_screen'] += 1

                self.thread_watchdog['display'] = time.time()
                time.sleep(config.get('LCD_REFRESH_INTERVAL', 5))
            except Exception as e:
                logger.error(f"Error in display_loop: {e}")
                time.sleep(5)

    def validate_sensor_data(self, data):
        valid_ranges = {
            'temperature': (-40, 80),
            'ph': (0, 14),
            'ec': (0, 5000),
            'nitrogen': (0, 100),
            'phosphorus': (0, 20),
            'quality_score': (0, 150)
        }

        out_of_range = False

        for param, (min_val, max_val) in valid_ranges.items():
            value = data.get(param)
            if value is None:
                continue

            try:
                val_float = float(value)
                if not (min_val <= val_float <= max_val):
                    logger.debug(f"{param} out of range: {val_float} (expected {min_val}-{max_val})")

                    if param in ['phosphorus', 'nitrogen'] and val_float > max_val:
                        data[param] = max_val
                        logger.info(f"Capping {param} at {max_val}")
                        out_of_range = False
                    else:
                        out_of_range = True
            except (ValueError, TypeError) as e:
                logger.debug(f"{param} validation error: {value} - {e}")
                out_of_range = True

        quality_status = data.get('quality_status')
        if quality_status not in ['GOOD', 'WARNING', 'CRITICAL']:
            logger.debug(f"Invalid quality_status: {quality_status}")
            data['quality_status'] = 'GOOD'
            logger.debug("Defaulting quality_status to 'GOOD'")

        return not out_of_range

    def has_any_valid_data(self, data):
        return any(v is not None for k, v in data.items()
                   if k not in ['quality_score', 'quality_status'])

    def send_to_thingspeak(self, data, timestamp):
        if not config.get('THINGSPEAK', {}).get('API_KEY'):
            logger.warning("ThingSpeak API key not configured")
            return False

        if not self.validate_sensor_data(data):
            logger.debug("Data validation failed. Skipping send.")
            return False

        payload = {"api_key": config.get('THINGSPEAK', {}).get('API_KEY')}
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

        max_retries = config.get('THINGSPEAK', {}).get('MAX_RETRIES', 3)
        initial_delay = config.get('THINGSPEAK', {}).get('RETRY_DELAY', 30)
        max_delay = config.get('THINGSPEAK', {}).get('MAX_RETRY_DELAY', 300)

        for attempt in range(max_retries):
            if time.time() - self.state['thingspeak']['last_network_check'] > 30:
                if not check_network_connectivity():
                    logger.warning(f"Network is down. Attempting backup and potentially network restart. (Attempt {attempt+1}/{max_retries})")
                    self.save_thingspeak_backup(timestamp, data)
                    with self.state_lock:
                         self.state['thingspeak']['network_error_count'] += 1
                    
                    if self.state['thingspeak']['network_error_count'] % 3 == 0 and self.state['thingspeak']['network_error_count'] > 0:
                        restart_network_interface()
                        time.sleep(5)

                    if not check_network_connectivity():
                        logger.error("Failed to restore network connectivity. Stopping upload attempts for this cycle.")
                        break

            try:
                response = requests.get(config.get('THINGSPEAK', {}).get('URL'), params=payload, timeout=10)
                response.raise_for_status()
                logger.info(f"Data sent to ThingSpeak successfully. Response: {response.text.strip()}")
                
                with self.state_lock:
                    self.state['thingspeak']['connection_errors'] = 0
                    self.state['thingspeak']['network_error_count'] = 0
                return True

            except requests.exceptions.Timeout:
                logger.warning(f"Timeout error connecting to ThingSpeak. (Attempt {attempt+1}/{max_retries})")
                self.save_thingspeak_backup(timestamp, data)

            except requests.exceptions.RequestException as e:
                logger.error(f"Error connecting to ThingSpeak (Attempt {attempt+1}/{max_retries}): {e}")
                self.save_thingspeak_backup(timestamp, data)
                
            except Exception as e:
                logger.error(f"An unexpected error occurred during ThingSpeak upload: {e}")
                self.save_thingspeak_backup(timestamp, data)

            delay = min(max_delay, initial_delay * (2 ** attempt)) + time.uniform(0, 5)
            logger.info(f"Retrying in {delay:.2f} seconds...")
            time.sleep(delay)

        with self.state_lock:
            self.state['thingspeak']['connection_errors'] += 1
        logger.error(f"Failed to send data to ThingSpeak after {max_retries} attempts.")
        return False

    def save_thingspeak_backup(self, timestamp, data):
        backup_file = config.get('THINGSPEAK', {}).get('BACKUP_FILE')
        if not backup_file:
            logger.error("Backup file path not configured.")
            return

        if not ensure_directory_exists(backup_file):
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
        backup_file = config.get('THINGSPEAK', {}).get('BACKUP_FILE')
        if not backup_file or not os.path.exists(backup_file):
            return

        rows_to_keep = []
        try:
            with open(backup_file, "r", newline="") as f:
                reader = csv.reader(f)
                headers = next(reader, None)
                for row in reader:
                    if len(row) >= 9:
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
            success = self.send_to_thingspeak(data, row['timestamp'])
            if not success:
                still_failed.append(row)
            else:
                logger.info(f"Flushed backup: {row['timestamp']}")
            time.sleep(15)

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
        while self.state['running']:
            try:
                with self.state_lock:
                    if time.time() - self.state['thingspeak']['last_sent_time'] >= config.get('THINGSPEAK', {}).get('SEND_INTERVAL', 60):
                        data = {
                            'temperature': self.get_average(self.history['temp']),
                            'ph': self.get_average(self.history['ph']),
                            'ec': self.get_average(self.history['ec']),
                            'nitrogen': self.get_average(self.history['nitrogen']),
                            'phosphorus': self.get_average(self.history['phosphorus']),
                            'turbidity': sum(self.history['turbidity']) / len(self.history['turbidity']) if self.history['turbidity'] else 0,
                            'quality_score': self.state.get('last_status_full', {}).get('score', 0),
                            'quality_status': self.state.get('last_status_full', {}).get('overall', 'GOOD')
                        }

                        if self.has_any_valid_data(data):
                            try:
                                self.flush_thingspeak_backup()
                            except Exception as e:
                                logger.error(f"Critical error flushing backup: {e}")
                                ensure_backup_file_exists()

                            timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                            if self.send_to_thingspeak(data, timestamp):
                                self.state['thingspeak']['last_sent_time'] = time.time()
                        else:
                            logger.info("Waiting for valid sensor data before sending to ThingSpeak")

                self.thread_watchdog['thingspeak'] = time.time()
                time.sleep(5)
            except Exception as e:
                logger.error(f"Error in thingspeak_loop: {e}")
                time.sleep(10)

    def watchdog_loop(self):
        while self.state['running']:
            try:
                current_time = time.time()
                timeout = 60

                for thread_name, last_update in self.thread_watchdog.items():
                    if current_time - last_update > timeout:
                        logger.error(f"Thread {thread_name} appears to be stuck!")
                        self.thread_watchdog[thread_name] = current_time

                time.sleep(30)
            except Exception as e:
                logger.error(f"Error in watchdog_loop: {e}")
                time.sleep(30)

    def monitor_loop(self):
        first_cycle = True

        while self.state['running']:
            try:
                rs485_data = self.read_rs485_sensor()
                ds18b20_temp = self.read_ds18b20_temp()

                if not rs485_data:
                    if first_cycle:
                        print("\n" + "="*60)
                        print(f"  POND MONITORING REPORT - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
                        print("="*60)
                        print("\n❌ ERROR: Failed to read from RS485 sensor. Check wiring and power.")
                        print("Waiting for sensor data...")
                        first_cycle = False
                    time.sleep(config.get('TEMP_READ_INTERVAL', 15))
                    continue

                self.update_historical_data(rs485_data, ds18b20_temp)
                status = self.get_water_quality_status(rs485_data, ds18b20_temp)

                with self.state_lock:
                    self.state['last_status_full'] = status
                    self.state['indicators']['last_status'] = status['overall']

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
                print(f"Avg Phosphorus:    {self.get_average(self.history['phosphorus']):.1f} mg/kg" if self.get_average(self.history['phosphorus']) is not None else "Avg Phosphorus:    N/A")
                turbidity_ratio = sum(self.history['turbidity']) / len(self.history['turbidity']) if self.history['turbidity'] else 0
                print(f"Turbidity Ratio:   {turbidity_ratio:.0%}" if self.history['turbidity'] else "Turbidity Ratio:   N/A")

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

                self.handle_critical_state(status)
                self.update_indicators(status)

                self.thread_watchdog['monitor'] = time.time()
                time.sleep(config.get('TEMP_READ_INTERVAL', 15))
            except KeyboardInterrupt:
                self.state['running'] = False
                break
            except Exception as e:
                logger.error(f"Error in monitor_loop: {e}")
                time.sleep(5)

    def cleanup(self):
        logger.info("Starting cleanup...")
        self.state['running'] = False

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
                pass

        GPIO.output(config.get('GPIO', {}).get('PUMP_PIN', 16), GPIO.HIGH)
        logger.info("Pump turned OFF.")

        if self.gsm:
            self.gsm.close()
            logger.info("GSM module closed.")

        GPIO.cleanup()
        logger.info("System cleanup complete")

def main():
    logger.info("Smart Fish Pond Monitoring System v5.13 (Robust)")
    
    ensure_backup_file_exists()

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
        try:
            monitor.cleanup()
        except NameError:
            logger.error("Monitor object not created, cannot cleanup.")
        except Exception as cleanup_error:
            logger.error(f"Error during cleanup: {cleanup_error}")

if __name__ == "__main__":
    main()