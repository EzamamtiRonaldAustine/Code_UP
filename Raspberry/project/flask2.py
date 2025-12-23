import os
import glob
import time
import serial
import random
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
import re
from flask import Flask, render_template_string, jsonify

# ============================================================================
# LOGGING CONFIGURATION
# ============================================================================

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# ============================================================================
# CONFIGURATION CONSTANTS
# ============================================================================

QUALITY_STATUS_CODES = {
    "GOOD": 0,
    "WARNING": 1,
    "CRITICAL": 2
}

DEFAULT_CONFIG = {
    "TEMP_READ_INTERVAL": 15,
    "LCD_REFRESH_INTERVAL": 5,
    "PUMP_RUN_DURATION": {
        "SHORT": 60,
        "NORMAL": 120,
        "LONG": 180
    },
    "SMS_COOLDOWN": 120,
    "CRITICAL_DURATION": 120,
    "HISTORY_SIZE": 5,
    "THINGSPEAK": {
        "URL": "https://api.thingspeak.com/update",
        "API_KEY": "",
        "SEND_INTERVAL": 60,
        "BACKUP_FILE": "pond_thingspeak_backup.csv",
        "MAX_RETRIES": 3,
        "RETRY_DELAY": 5,
        "MAX_RETRY_DELAY": 60
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
    "PHONE_NUMBERS": ["", ""]
}

def check_network_connectivity():
    try:
        socket.gethostbyname('8.8.8.8')
        return True
    except socket.gaierror:
        logger.warning("Network connectivity check failed")
        return False
    except Exception as e:
        logger.error(f"Error during network check: {e}")
        return False

def restart_network_interface():
    try:
        logger.info("Attempting to restart network interface...")
        subprocess.run(["sudo", "ip", "link", "set", "wlan0", "down"], 
                      stderr=subprocess.PIPE, stdout=subprocess.PIPE, timeout=10)
        time.sleep(2)
        subprocess.run(["sudo", "ip", "link", "set", "wlan0", "up"], 
                      stderr=subprocess.PIPE, stdout=subprocess.PIPE, timeout=10)
        time.sleep(5)
        try:
            subprocess.run(["sudo", "systemctl", "restart", "NetworkManager"], 
                          timeout=10, check=False)
        except:
            subprocess.run(["sudo", "systemctl", "restart", "networking"], 
                          timeout=10, check=False)
        time.sleep(15)
        if check_network_connectivity():
            logger.info("✅ Network connectivity restored")
            return True
        else:
            logger.warning("Network connectivity still down")
            return False
    except Exception as e:
        logger.error(f"Failed to restart network interface: {e}")
        return False

def load_config():
    return DEFAULT_CONFIG

config = load_config()

# ============================================================================
# MAIN MONITORING CLASS
# ============================================================================

class SmartFishPondMonitor:
    def __init__(self):
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

        self.state_lock = threading.Lock()
        self.gsm_lock = threading.Lock()

        self.thread_watchdog = {
            'monitor': time.time(),
            'display': time.time(),
            'pump': time.time(),
            'thingspeak': time.time()
        }

        self.history = {
            'temp': deque(maxlen=config.get('HISTORY_SIZE', 5)),
            'ph': deque(maxlen=config.get('HISTORY_SIZE', 5)),
            'ec': deque(maxlen=config.get('HISTORY_SIZE', 5)),
            'nitrogen': deque(maxlen=config.get('HISTORY_SIZE', 5)),
            'phosphorus': deque(maxlen=config.get('HISTORY_SIZE', 5)),
            'turbidity': deque(maxlen=config.get('HISTORY_SIZE', 5))
        }

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
            logger.info("✅ GPIO initialized successfully")
        except Exception as e:
            logger.error(f"GPIO initialization failed: {e}")
            raise

        self.lcd = self._init_lcd()
        self.rs485_instrument = self._init_rs485()
        self.device_file = self._init_ds18b20()
        self.gsm = self._init_gsm()
        self.test_thingspeak_connection()

        self.monitor_thread = threading.Thread(target=self.monitor_loop, name="Monitor", daemon=True)
        self.display_thread = threading.Thread(target=self.display_loop, name="Display", daemon=True)
        self.pump_thread = threading.Thread(target=self.pump_control_loop, name="Pump", daemon=True)
        self.thingspeak_thread = threading.Thread(target=self.thingspeak_loop, name="ThingSpeak", daemon=True)
        self.watchdog_thread = threading.Thread(target=self.watchdog_loop, name="Watchdog", daemon=True)

        for t in [self.monitor_thread, self.display_thread, self.pump_thread,
                 self.thingspeak_thread, self.watchdog_thread]:
            t.start()

    def test_thingspeak_connection(self):
        test_payload = {
            "api_key": config.get('THINGSPEAK', {}).get('API_KEY'),
            "field1": 25.0
        }
        try:
            response = requests.get(
                config.get('THINGSPEAK', {}).get('URL'),
                params=test_payload,
                timeout=10
            )
            if response.status_code == 200:
                result = response.text.strip()
                if result.isdigit() and int(result) > 0:
                    logger.info(f"✅ ThingSpeak connection test PASSED")
                    return True
        except Exception as e:
            logger.error(f"❌ Connection test failed: {e}")
        return False

    def _init_lcd(self):
        max_retries = 3
        for attempt in range(max_retries):
            try:
                lcd = CharLCD('PCF8574', 0x27)
                lcd.clear()
                lcd.write_string("Initializing...")
                logger.info("✅ LCD initialized")
                return lcd
            except Exception as e:
                logger.error(f"LCD initialization failed: {e}")
                if attempt < max_retries - 1:
                    time.sleep(2)
        self.state['indicators']['lcd_available'] = False
        logger.warning("LCD unavailable")
        return None

    def _init_rs485(self):
        try:
            instrument = minimalmodbus.Instrument(
                config.get('SENSORS', {}).get('RS485_PORT', '/dev/ttyUSB0'),
                config.get('SENSORS', {}).get('RS485_SLAVE_ID', 1)
            )
            instrument.serial.baudrate = 9600
            instrument.serial.bytesize = 8
            instrument.serial.parity = minimalmodbus.serial.PARITY_NONE
            instrument.serial.stopbits = 1
            instrument.serial.timeout = 1
            logger.info("✅ RS485 sensor initialized")
            return instrument
        except Exception as e:
            logger.error(f"❌ RS485 initialization failed: {e}")
            return None

    def _init_ds18b20(self):
        try:
            os.system('modprobe w1-gpio')
            os.system('modprobe w1-therm')
            base_dir = '/sys/bus/w1/devices/'
            device_folders = glob.glob(base_dir + '28-*')
            if not device_folders:
                logger.error("No DS18B20 temperature sensor found")
                return None
            device_folder = device_folders[0]
            device_file = device_folder + '/w1_slave'
            logger.info("✅ DS18B20 temperature sensor initialized")
            return device_file
        except Exception as e:
            logger.error(f"❌ DS18B20 initialization failed: {e}")
            return None

    def _init_gsm(self):
        try:
            ser = serial.Serial(port=config.get('SENSORS', {}).get('GSM_PORT', "/dev/serial0"),
                              baudrate=config.get('SENSORS', {}).get('GSM_BAUDRATE', 9600), timeout=5)
            self.send_at_command(ser, "AT", 1)
            self.send_at_command(ser, "ATE0", 1)
            self.send_at_command(ser, "AT+CMGF=1", 1)
            logger.info("✅ GSM module initialized")
            return ser
        except Exception as e:
            logger.error(f"❌ GSM initialization failed: {e}")
            return None

    def send_at_command(self, ser, command, delay=1):
        try:
            ser.write((command + "\r\n").encode())
            time.sleep(delay)
            return ser.read_all().decode(errors="ignore").strip()
        except Exception as e:
            logger.error(f"Error sending AT command: {e}")
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
            logger.debug(f"Error reading DS18B20: {e}")
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
            logger.error(f"RS485 sensor read error: {e}")
            if self.state['sensor_errors']['rs485_error_count'] >= 5:
                logger.warning("Multiple RS485 errors, attempting to reinitialize")
                self.rs485_instrument = self._init_rs485()
                self.state['sensor_errors']['rs485_error_count'] = 0
            return {}

    def _read_register_with_retry(self, register, retries=2):
        for attempt in range(retries):
            try:
                value = self.rs485_instrument.read_register(register, 1, functioncode=3)
                return value
            except Exception as e:
                logger.debug(f"RS485 read attempt {attempt + 1} failed: {e}")
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
        elif avg_ph < 5.5:
            status['score'] += 50
            status['alerts'].append(f"🚨 CRITICAL: pH {avg_ph:.1f} is dangerously acidic")
            status['recommendations'].add('URGENT: Add agricultural lime (CaCO₃) immediately')
        elif avg_ph < 6.0:
            status['score'] += 25
            status['alerts'].append(f"⚠️ WARNING: pH {avg_ph:.1f} is acidic")
            status['recommendations'].add('Consider adding agricultural lime gradually')
        elif avg_ph < 6.5:
            status['score'] += 10
            status['alerts'].append(f"ℹ️ pH {avg_ph:.1f} is slightly low but acceptable")
        elif avg_ph > 9.5:
            status['score'] += 50
            status['alerts'].append(f"🚨 CRITICAL: pH {avg_ph:.1f} is dangerously alkaline")
            status['recommendations'].add('URGENT: Perform large water change')
        elif avg_ph > 9.0:
            status['score'] += 25
            status['alerts'].append(f"⚠️ WARNING: pH {avg_ph:.1f} is too alkaline")
            status['recommendations'].add('Perform partial water change')
        elif avg_ph > 8.5:
            status['score'] += 10
            status['alerts'].append(f"ℹ️ pH {avg_ph:.1f} is slightly high but acceptable")

        if avg_temp is not None:
            if avg_temp < 12:
                status['score'] += 40
                status['alerts'].append(f"🚨 CRITICAL: Temperature {avg_temp:.1f}°C is too cold")
                status['recommendations'].add('Add pond heater immediately')
            elif avg_temp < 18:
                status['score'] += 15
                status['alerts'].append(f"⚠️ Temperature {avg_temp:.1f}°C is cool")
            elif avg_temp > 35:
                status['score'] += 40
                status['alerts'].append(f"🚨 CRITICAL: Temperature {avg_temp:.1f}°C is too hot")
                status['recommendations'].add('Add shade and emergency aeration')
            elif avg_temp > 30:
                status['score'] += 15
                status['alerts'].append(f"⚠️ Temperature {avg_temp:.1f}°C is warm")
                status['recommendations'].add('Monitor closely and increase aeration')

        if avg_ec is not None and avg_ec > 2000:
            status['score'] += 30
            status['alerts'].append(f"⚠️ EC {avg_ec:.0f} μS/cm is high")
            status['recommendations'].add('Consider diluting with fresh water')

        if turbidity_ratio > 0.8:
            status['score'] += 20
            status['alerts'].append(f"⚠️ Water is consistently turbid")
            status['recommendations'].add('Check filter and consider water change')

        if avg_nitrogen is not None:
            if avg_nitrogen > 200:
                status['score'] += 35
                status['alerts'].append(f"🚨 CRITICAL: Nitrogen extremely high: {avg_nitrogen:.1f} mg/kg")
                status['recommendations'].add('URGENT: Stop feeding and perform large water change')
            elif avg_nitrogen > 150:
                status['score'] += 20
                status['alerts'].append(f"⚠️ WARNING: Nitrogen high: {avg_nitrogen:.1f} mg/kg")
                status['recommendations'].add('Reduce feeding and increase water changes')
            elif avg_nitrogen > 100:
                status['score'] += 5
                status['alerts'].append(f"ℹ️ Nitrogen elevated: {avg_nitrogen:.1f} mg/kg (monitor)")

        if avg_phosphorus is not None:
            if avg_phosphorus > 200:
                status['score'] += 35
                status['alerts'].append(f"🚨 CRITICAL: Phosphorus extremely high: {avg_phosphorus:.1f} mg/kg")
                status['recommendations'].add('URGENT: Stop feeding and perform large water change')
            elif avg_phosphorus > 150:
                status['score'] += 20
                status['alerts'].append(f"⚠️ WARNING: Phosphorus high: {avg_phosphorus:.1f} mg/kg")
                status['recommendations'].add('Reduce feeding and increase water changes')
            elif avg_phosphorus > 100:
                status['score'] += 5
                status['alerts'].append(f"ℹ️ Phosphorus elevated: {avg_phosphorus:.1f} mg/kg (monitor)")

        if status['score'] >= 80:
            status['overall'] = 'CRITICAL'
        elif status['score'] >= 40:
            status['overall'] = 'WARNING'
        else:
            status['overall'] = 'GOOD'

        return status

    def set_leds(self, blue, yellow, red):
        try:
            GPIO.output(config.get('GPIO', {}).get('BLUE_LED_PIN', 27), blue)
            GPIO.output(config.get('GPIO', {}).get('YELLOW_LED_PIN', 22), yellow)
            GPIO.output(config.get('GPIO', {}).get('RED_LED_PIN', 5), red)
        except Exception as e:
            logger.debug(f"LED control error: {e}")

    def update_indicators(self, status):
        self.set_leds(0, 0, 0)
        try:
            self.pwm_buzzer.ChangeDutyCycle(0)
        except:
            pass

        if status['overall'] == 'GOOD':
            self.set_leds(1, 0, 0)
            with self.state_lock:
                self.state['pump']['should_run'] = False
                self.state['pump']['mode'] = "OFF"
        elif status['overall'] == 'WARNING':
            self.set_leds(0, 1, 0)
            try:
                threading.Timer(0.2, lambda: self.pwm_buzzer.ChangeDutyCycle(50)).start()
                threading.Timer(0.4, lambda: self.pwm_buzzer.ChangeDutyCycle(0)).start()
            except:
                pass
            with self.state_lock:
                self.state['pump']['should_run'] = False
        elif status['overall'] == 'CRITICAL':
            self.set_leds(0, 0, 1)
            try:
                threading.Timer(1.0, lambda: self.pwm_buzzer.ChangeDutyCycle(50)).start()
                threading.Timer(1.2, lambda: self.pwm_buzzer.ChangeDutyCycle(0)).start()
            except:
                pass

            with self.state_lock:
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
        current_time = time.time()

        if status['overall'] == 'CRITICAL':
            with self.state_lock:
                if not self.state['critical']['sustained']:
                    self.state['critical']['start_time'] = current_time
                    self.state['critical']['sustained'] = True
                    self.state['critical']['alert_sent'] = False
                    logger.info("⚠️ Critical condition detected. Starting 5-minute timer before SMS alert.")

                elif (not self.state['critical']['alert_sent'] and
                      current_time - self.state['critical']['start_time'] > config.get('CRITICAL_DURATION', 300)):
                    logger.info("🚨 Sustained critical condition confirmed. Sending SMS alert.")
                    self._send_sms_message(status)
                    self.state['sms']['last_sent_time'] = current_time
                    self.state['critical']['alert_sent'] = True

        else:
            with self.state_lock:
                if self.state['critical']['sustained']:
                    logger.info("✅ Condition recovered. Resetting critical state.")
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
        if status['recommendations']:
            message += f"\n\nActions:\n" + "\n".join(list(status['recommendations'])[:2])

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
                        logger.info(f"✅ SMS sent to {phone}")
                    else:
                        logger.error(f"❌ SMS failed to {phone}: {final_response.strip()}")
                except Exception as e:
                    logger.error(f"Error sending SMS to {phone}: {e}")

    def pump_control_loop(self):
        while self.state['running']:
            try:
                with self.state_lock:
                    should_activate = self.state['pump']['should_run'] and not self.state['pump']['is_running']
                    is_running = self.state['pump']['is_running']
                    pump_mode = self.state['pump']['mode']
                    start_time = self.state['pump']['start_time']
                
                if should_activate:
                    logger.info(f"▶️ Activating PUMP in {pump_mode} mode.")
                    GPIO.output(config.get('GPIO', {}).get('PUMP_PIN', 16), GPIO.LOW)
                    with self.state_lock:
                        self.state['pump']['is_running'] = True
                        self.state['pump']['start_time'] = time.time()
                        self.state['pump']['should_run'] = False

                if is_running:
                    run_duration = config.get('PUMP_RUN_DURATION', {}).get(pump_mode, 300)
                    if time.time() - start_time > run_duration:
                        logger.info(f"⏹️ {pump_mode} pump cycle complete. Turning PUMP OFF.")
                        GPIO.output(config.get('GPIO', {}).get('PUMP_PIN', 16), GPIO.HIGH)
                        with self.state_lock:
                            self.state['pump']['is_running'] = False
                            self.state['pump']['mode'] = "OFF"

                self.thread_watchdog['pump'] = time.time()
                time.sleep(1)
            except Exception as e:
                logger.error(f"Error in pump_control_loop: {e}")
                self.thread_watchdog['pump'] = time.time()
                time.sleep(5)

    def _update_lcd_content(self, status):
        if not self.state['indicators']['lcd_available'] or not self.lcd:
            return

        try:
            line1 = ""
            line2 = ""

            if status['overall'] in ['WARNING', 'CRITICAL']:
                if status['overall'] == 'WARNING':
                    line1 = "!   WARNING   !"
                else:
                    line1 = "!! CRITICAL  !!"

                if status['alerts']:
                    alert = status['alerts'][0]
                    alert_clean = ''.join(c for c in alert if ord(c) < 128)
                    alert_clean = alert_clean.replace('CRITICAL:', '').replace('DANGER:', '').replace('WARNING:', '').replace('ℹ️', '').strip()

                    if 'pH' in alert_clean:
                        ph_match = re.search(r'pH[:\s]+([\d.]+)', alert_clean)
                        if ph_match:
                            ph_val = float(ph_match.group(1))
                            if 'acidic' in alert_clean.lower() or 'dangerously acidic' in alert_clean.lower():
                                line2 = f"pH:{ph_val:4.1f} ACIDIC "
                            elif 'alkaline' in alert_clean.lower() or 'dangerously alkaline' in alert_clean.lower():
                                line2 = f"pH:{ph_val:4.1f} ALKALIN"
                            elif 'slightly low' in alert_clean.lower():
                                line2 = f"pH:{ph_val:4.1f} LOW    "
                            elif 'slightly high' in alert_clean.lower():
                                line2 = f"pH:{ph_val:4.1f} HIGH   "
                            else:
                                line2 = f"pH:{ph_val:4.1f} Problem"
                        else:
                            line2 = "pH sensor issue "
                    elif 'Temperature' in alert_clean:
                        temp_match = re.search(r'([\d.]+).?C', alert_clean)
                        if temp_match:
                            temp_val = float(temp_match.group(1))
                            if 'cold' in alert_clean.lower():
                                line2 = f"T:{temp_val:4.1f}C  COLD  "
                            elif 'cool' in alert_clean.lower():
                                line2 = f"T:{temp_val:4.1f}C  COOL  "
                            elif 'hot' in alert_clean.lower():
                                line2 = f"T:{temp_val:4.1f}C   HOT  "
                            elif 'warm' in alert_clean.lower():
                                line2 = f"T:{temp_val:4.1f}C  WARM  "
                            else:
                                line2 = f"T:{temp_val:4.1f}C   BAD "
                        else:
                            line2 = "Temp issue      "
                    elif 'Nitrogen' in alert_clean:
                        n_match = re.search(r'([\d.]+)\s*mg/kg', alert_clean)
                        if n_match:
                            n_val = float(n_match.group(1))
                            if 'extremely high' in alert_clean.lower() or 'critical' in alert_clean.lower():
                                line2 = f"N:{n_val:6.1f} CRIT  "
                            elif 'high' in alert_clean.lower() or 'warning' in alert_clean.lower():
                                line2 = f"N:{n_val:6.1f} HIGH  "
                            elif 'elevated' in alert_clean.lower():
                                line2 = f"N:{n_val:6.1f} ELEV  "
                            else:
                                line2 = f"N:{n_val:6.1f} HIGH  "
                        else:
                            line2 = "Nitrogen too HI "
                    elif 'Phosphorus' in alert_clean:
                        p_match = re.search(r'([\d.]+)\s*mg/kg', alert_clean)
                        if p_match:
                            p_val = float(p_match.group(1))
                            if 'extremely high' in alert_clean.lower() or 'critical' in alert_clean.lower():
                                line2 = f"P:{p_val:6.1f} CRIT  "
                            elif 'high' in alert_clean.lower() or 'warning' in alert_clean.lower():
                                line2 = f"P:{p_val:6.1f} HIGH  "
                            elif 'elevated' in alert_clean.lower():
                                line2 = f"P:{p_val:6.1f} ELEV  "
                            else:
                                line2 = f"P:{p_val:6.1f} HIGH  "
                        else:
                            line2 = "Phosphorus HIGH "
                    elif 'EC' in alert_clean:
                        ec_match = re.search(r'EC\s+([\d.]+)', alert_clean)
                        if ec_match:
                            ec_val = float(ec_match.group(1))
                            line2 = f"EC:{ec_val:5.0f} HIGH   "
                        else:
                            line2 = "EC too high     "
                    elif 'turbid' in alert_clean.lower():
                        line2 = "WATER TURBID    "
                    elif 'sensor' in alert_clean.lower() and 'pH' in alert_clean:
                        line2 = "pH sensor fault "
                    elif 'sensor' in alert_clean.lower():
                        line2 = "Sensor fault    "
                    elif 'No valid' in alert_clean:
                        line2 = "No sensor data  "
                    else:
                        line2 = alert_clean[:16].ljust(16)
                else:
                    line2 = "Check system    "

            else:
                screen = self.state['indicators']['lcd_screen'] % 4

                if screen == 0:
                    temp = self.get_average(self.history['temp'])
                    ph = self.get_average(self.history['ph'])
                    if temp is not None and ph is not None:
                        line1 = f"T:{temp:4.1f}C  pH:{ph:4.1f} "
                        temp_trend = status['trends'].get('temperature', 'STABLE')
                        ph_trend = status['trends'].get('ph', 'STABLE')
                        if temp_trend == "STABLE" and ph_trend == "STABLE":
                            line2 = "TREND: STABLE   "
                        elif temp_trend == "INCREASING" and ph_trend == "INCREASING":
                            line2 = "TREND: UP   UP  "
                        elif temp_trend == "DECREASING" and ph_trend == "DECREASING":
                            line2 = "TREND: DOWN DOWN"
                        elif temp_trend == "INCREASING" and ph_trend == "DECREASING":
                            line2 = "TREND: UP   DOWN"
                        elif temp_trend == "DECREASING" and ph_trend == "INCREASING":
                            line2 = "TREND: DOWN UP  "
                        elif temp_trend == "INCREASING":
                            line2 = "TREND: UP   --  "
                        elif temp_trend == "DECREASING":
                            line2 = "TREND: DOWN --  "
                        elif ph_trend == "INCREASING":
                            line2 = "TREND: --   UP  "
                        elif ph_trend == "DECREASING":
                            line2 = "TREND: --   DOWN"
                        else:
                            line2 = "TREND: STABLE   "
                    else:
                        line1 = "Temperature & pH"
                        line2 = "No data         "

                elif screen == 1:
                    ec = self.get_average(self.history['ec'])
                    turbidity_ratio = sum(self.history['turbidity']) / len(self.history['turbidity']) if self.history['turbidity'] else 0
                    if ec is not None:
                        turbidity_status = "TURBID" if turbidity_ratio > 0.5 else "CLEAR "
                        line1 = f"EC:{ec:5.0f} uS/cm  "
                        line2 = f"WATER: {turbidity_status:6} "
                    else:
                        line1 = "EC & Turbidity  "
                        line2 = "No data         "

                elif screen == 2:
                    n = self.get_average(self.history['nitrogen'])
                    p = self.get_average(self.history['phosphorus'])
                    if n is not None and p is not None:
                        line1 = f"N:{n:6.1f} mg/kg  "
                        line2 = f"P:{p:6.1f} mg/kg  "
                    else:
                        line1 = "Nitrogen & Phos."
                        line2 = "No data         "

                else:
                    status_text = status['overall']
                    score = status['score']
                    line1 = f"Status: {status_text:7} "
                    line2 = f"Score: {score:3}/100   "

            line1 = line1[:16].ljust(16)
            line2 = line2[:16].ljust(16)
            content = line1 + line2

            if content != self.state['indicators']['last_lcd_content']:
                try:
                    self.lcd.clear()
                    time.sleep(0.01)
                    self.lcd.cursor_pos = (0, 0)
                    self.lcd.write_string(line1)
                    time.sleep(0.01)
                    self.lcd.cursor_pos = (1, 0)
                    self.lcd.write_string(line2)
                    self.state['indicators']['last_lcd_content'] = content
                except Exception as lcd_err:
                    logger.error(f"LCD write error: {lcd_err}")
                    raise

            self.state['indicators']['lcd_error_count'] = 0

        except Exception as e:
            self.state['indicators']['lcd_error_count'] += 1
            logger.error(f"LCD error: {e}")
            if self.state['indicators']['lcd_error_count'] >= 5:
                logger.warning("Multiple LCD errors, marking as unavailable")
                self.state['indicators']['lcd_available'] = False

    def display_loop(self):
        while self.state['running']:
            try:
                last_status = self.state.get('last_status_full')
                if last_status:
                    self._update_lcd_content(last_status)
                
                self.state['indicators']['lcd_screen'] += 1
                self.thread_watchdog['display'] = time.time()
                time.sleep(config.get('LCD_REFRESH_INTERVAL', 5))
            except Exception as e:
                logger.error(f"Error in display_loop: {e}")
                self.thread_watchdog['display'] = time.time()
                time.sleep(5)

    def validate_sensor_data(self, data):
        valid_ranges = {
            'temperature': (-40, 80),
            'ph': (0, 14),
            'ec': (0, 5000),
            'nitrogen': (0, 200),
            'phosphorus': (0, 200),
            'quality_score': (0, 150)
        }

        out_of_range = False
        for param, (min_val, max_val) in valid_ranges.items():
            value = data.get(param)
            if value is not None:
                try:
                    val_float = float(value)
                    if not (min_val <= val_float <= max_val):
                        logger.warning(f"{param} out of range: {val_float}")
                        out_of_range = True
                except (ValueError, TypeError) as e:
                    logger.warning(f"{param} validation error: {value} - {e}")
                    out_of_range = True

        quality_status = data.get('quality_status')
        if quality_status and quality_status not in ['GOOD', 'WARNING', 'CRITICAL']:
            logger.debug(f"Invalid quality_status: {quality_status}")
            data['quality_status'] = 'GOOD'

        return not out_of_range

    def has_any_valid_data(self, data):
        return any(v is not None for k, v in data.items()
                   if k not in ['quality_score', 'quality_status'])

    def send_to_thingspeak(self, data, timestamp):
        if not config.get('THINGSPEAK', {}).get('API_KEY'):
            logger.warning("ThingSpeak API key not configured")
            return False

        if not self.validate_sensor_data(data):
            logger.debug("Data validation failed")
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
            status_text = str(data['quality_status']).upper()
            status_code = QUALITY_STATUS_CODES.get(status_text, -1)
            payload['field8'] = status_code

        max_retries = config.get('THINGSPEAK', {}).get('MAX_RETRIES', 3)
        initial_delay = config.get('THINGSPEAK', {}).get('RETRY_DELAY', 5)
        max_delay = config.get('THINGSPEAK', {}).get('MAX_RETRY_DELAY', 60)

        for attempt in range(max_retries):
            if time.time() - self.state['thingspeak']['last_network_check'] > 30:
                self.state['thingspeak']['last_network_check'] = time.time()
                
                if not check_network_connectivity():
                    logger.warning("⚠️ Network is down. Saving to backup.")
                    self.save_thingspeak_backup(timestamp, data)
                    self.state['thingspeak']['network_error_count'] += 1
                    if self.state['thingspeak']['network_error_count'] % 3 == 0:
                        restart_network_interface()
                        time.sleep(5)
                    if not check_network_connectivity():
                        logger.error("❌ Failed to restore network connectivity.")
                        break

            try:
                response = requests.get(
                    config.get('THINGSPEAK', {}).get('URL'), 
                    params=payload, 
                    timeout=10
                )
                
                if response.status_code == 200:
                    result = response.text.strip()
                    if result.isdigit() and int(result) > 0:
                        logger.info(f"✅ ThingSpeak upload (Entry: {result})")
                        self.state['thingspeak']['connection_errors'] = 0
                        self.state['thingspeak']['network_error_count'] = 0
                        return True
                    else:
                        logger.warning(f"⚠️ ThingSpeak returned '{result}'")
                        self.save_thingspeak_backup(timestamp, data)
                        return False
                else:
                    logger.error(f"❌ HTTP Error: {response.status_code}")
                    self.save_thingspeak_backup(timestamp, data)

            except requests.exceptions.Timeout:
                logger.warning(f"⏱️ Timeout (Attempt {attempt+1}/{max_retries})")
                self.save_thingspeak_backup(timestamp, data)

            except requests.exceptions.ConnectionError as e:
                logger.error(f"🌐 Network error (Attempt {attempt+1}/{max_retries}): {str(e)[:80]}")
                self.save_thingspeak_backup(timestamp, data)

            except requests.exceptions.RequestException as e:
                logger.error(f"❌ Request failed (Attempt {attempt+1}/{max_retries}): {str(e)[:80]}")
                self.save_thingspeak_backup(timestamp, data)
                
            except Exception as e:
                logger.error(f"❌ Unexpected error: {e}")
                self.save_thingspeak_backup(timestamp, data)

            if attempt < max_retries - 1:
                delay = min(max_delay, initial_delay * (2 ** attempt)) + random.uniform(0, 2)
                logger.info(f"⏳ Retrying in {delay:.1f} seconds...")
                time.sleep(delay)

        self.state['thingspeak']['connection_errors'] += 1
        logger.error(f"❌ Failed to send to ThingSpeak after {max_retries} attempts.")
        return False

    def save_thingspeak_backup(self, timestamp, data):
        backup_file = config.get('THINGSPEAK', {}).get('BACKUP_FILE')
        if not backup_file:
            logger.error("Backup file path not configured.")
            return

        ensure_directory_exists(backup_file)
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
            logger.debug(f"💾 Backup saved")
        except Exception as e:
            logger.error(f"Error saving backup: {e}")

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
                            def safe_convert(value, is_numeric=True):
                                if not value or value.strip() == '':
                                    return None
                                if is_numeric:
                                    try:
                                        return float(value)
                                    except ValueError:
                                        return None
                                return value

                            row_dict = {
                                'timestamp': row[0],
                                'temperature': safe_convert(row[1]),
                                'ph': safe_convert(row[2]),
                                'ec': safe_convert(row[3]),
                                'nitrogen': safe_convert(row[4]),
                                'phosphorus': safe_convert(row[5]),
                                'turbidity': safe_convert(row[6]),
                                'quality_score': safe_convert(row[7]),
                                'quality_status': safe_convert(row[8], is_numeric=False)
                            }
                            rows_to_keep.append(row_dict)
                        except (ValueError, IndexError) as e:
                            logger.warning(f"Skipping invalid backup row: {e}")
                            continue
        except Exception as e:
            logger.error(f"Error reading backup file: {e}")
            return

        if not rows_to_keep:
            try:
                os.remove(backup_file)
                logger.info("🗑️ Empty backup file removed")
            except OSError:
                pass
            return

        logger.info(f"📤 Flushing {len(rows_to_keep)} backup entries...")
        still_failed = []

        for row in rows_to_keep:
            data = {k: v for k, v in row.items()
                    if k != 'timestamp' and v is not None}

            if self.has_any_valid_data(data):
                success = self.send_to_thingspeak(data, row['timestamp'])
                if not success:
                    still_failed.append(row)
                else:
                    logger.info(f"✅ Flushed backup: {row['timestamp']}")
                time.sleep(16)
            else:
                logger.warning(f"Skipping backup entry with no valid data: {row['timestamp']}")

        if still_failed:
            try:
                with open(backup_file, "w", newline="") as f:
                    writer = csv.writer(f)
                    writer.writerow(["timestamp", "temperature", "ph", "ec", "nitrogen",
                                  "phosphorus", "turbidity", "quality_score", "quality_status"])
                    for row in still_failed:
                        writer.writerow([
                            row['timestamp'],
                            row.get('temperature', ''),
                            row.get('ph', ''),
                            row.get('ec', ''),
                            row.get('nitrogen', ''),
                            row.get('phosphorus', ''),
                            row.get('turbidity', ''),
                            row.get('quality_score', ''),
                            row.get('quality_status', '')
                        ])
                logger.info(f"💾 {len(still_failed)} entries remain in backup")
            except Exception as e:
                logger.error(f"Error writing backup file: {e}")
        else:
            try:
                os.remove(backup_file)
                logger.info("✅ All backup data sent to ThingSpeak")
            except OSError:
                pass

    def thingspeak_loop(self):
        while self.state['running']:
            try:
                current_time = time.time()
                send_interval = config.get('THINGSPEAK', {}).get('SEND_INTERVAL', 60)
                
                if current_time - self.state['thingspeak']['last_sent_time'] >= send_interval:
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
                            logger.error(f"Error flushing backup: {e}")

                        timestamp = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                        if self.send_to_thingspeak(data, timestamp):
                            self.state['thingspeak']['last_sent_time'] = current_time
                    else:
                        logger.debug("Waiting for valid sensor data...")

                self.thread_watchdog['thingspeak'] = time.time()
                time.sleep(5)
                
            except Exception as e:
                logger.error(f"Error in thingspeak_loop: {e}")
                self.thread_watchdog['thingspeak'] = time.time()
                time.sleep(10)

    def watchdog_loop(self):
        while self.state['running']:
            try:
                current_time = time.time()
                timeout = 120

                for thread_name, last_update in self.thread_watchdog.items():
                    if current_time - last_update > timeout:
                        logger.error(f"⚠️ Thread '{thread_name}' appears to be stuck!")

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

                first_cycle = False
                self.update_historical_data(rs485_data, ds18b20_temp)
                status = self.get_water_quality_status(rs485_data, ds18b20_temp)

                self.state['last_status_full'] = status
                self.state['indicators']['last_status'] = status['overall']

                print("\n" + "="*60)
                print(f"  POND MONITORING REPORT - {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")
                print("="*60)

                print("\n--- SENSOR READINGS ---")
                print(f"DS18B20 Temp:      {ds18b20_temp:.1f}°C" if ds18b20_temp is not None else "DS18B20 Temp:      N/A")
                print(f"RS485 Temp:        {rs485_data.get('temperature'):.1f}°C" if rs485_data.get('temperature') is not None else "RS485 Temp:        N/A")
                print(f"Combined Temp:     {self.get_average(self.history['temp']):.1f}°C" if self.get_average(self.history['temp']) is not None else "Combined Temp:     N/A")

                turbidity = self.read_turbidity()
                print(f"Turbidity:         {'TURBID' if turbidity else 'CLEAR'}" if turbidity is not None else "Turbidity:         N/A")

                print("\n--- RS485 PROBE DATA (UNITS: mg/kg, μS/cm) ---")
                print(f"pH:                {rs485_data.get('ph'):.1f}" if rs485_data.get('ph') is not None else "pH:                N/A")
                print(f"EC:                {rs485_data.get('ec'):.0f} μS/cm" if rs485_data.get('ec') is not None else "EC:                N/A")
                print(f"Nitrogen (N):      {rs485_data.get('nitrogen'):.1f} mg/kg" if rs485_data.get('nitrogen') is not None else "Nitrogen (N):      N/A")
                print(f"Phosphorus (P):    {rs485_data.get('phosphorus'):.1f} mg/kg" if rs485_data.get('phosphorus') is not None else "Phosphorus (P):    N/A")
                print(f"Potassium (K):     {rs485_data.get('potassium'):.0f} mg/kg" if rs485_data.get('potassium') is not None else "Potassium (K):     N/A")

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
                self.thread_watchdog['monitor'] = time.time()
                time.sleep(5)

    def cleanup(self):
        logger.info("Starting cleanup...")
        self.state['running'] = False

        for t in [self.monitor_thread, self.display_thread, self.pump_thread,
                 self.thingspeak_thread, self.watchdog_thread]:
            if t.is_alive():
                try:
                    t.join(timeout=3)
                except:
                    pass

        self.set_leds(0, 0, 0)
        if self.pwm_buzzer:
            try:
                self.pwm_buzzer.stop()
            except:
                pass
        
        if self.lcd:
            try:
                self.lcd.clear()
                self.lcd.write_string("System stopped")
            except:
                pass

        GPIO.output(config.get('GPIO', {}).get('PUMP_PIN', 16), GPIO.HIGH)
        logger.info("Pump turned OFF.")

        if self.gsm:
            try:
                self.gsm.close()
                logger.info("GSM module closed.")
            except:
                pass

        GPIO.cleanup()
        logger.info("✅ System cleanup complete")

# ============================================================================
# FLASK WEB INTERFACE
# ============================================================================

app = Flask(__name__)

# Global variables for web interface
monitoring_data = {
    'last_update': None,
    'sensor_readings': {},
    'status': {},
    'historical_data': {},
    'trends': {},
    'alerts': [],
    'recommendations': [],
    'system_status': 'Initializing...'
}

monitor = None
monitoring_running = False

@app.route('/')
def index():
    return render_template_string('''
<!DOCTYPE html>
<html lang="en">
<head>
    <meta charset="UTF-8">
    <meta name="viewport" content="width=device-width, initial-scale=1.0">
    <title>Smart Fish Pond Monitor</title>
    <link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.0.0/css/all.min.css">
    <style>
        :root {
            --primary: #2563eb;
            --success: #10b981;
            --warning: #f59e0b;
            --danger: #ef4444;
            --dark: #1f2937;
            --light: #f3f4f6;
            --white: #ffffff;
        }

        * {
            margin: 0;
            padding: 0;
            box-sizing: border-box;
            font-family: 'Segoe UI', Tahoma, Geneva, Verdana, sans-serif;
        }

        body {
            background: linear-gradient(135deg, #667eea 0%, #764ba2 100%);
            min-height: 100vh;
            padding: 20px;
            color: var(--dark);
        }

        .container {
            max-width: 1400px;
            margin: 0 auto;
            background: var(--white);
            border-radius: 20px;
            box-shadow: 0 20px 60px rgba(0, 0, 0, 0.3);
            overflow: hidden;
        }

        header {
            background: linear-gradient(135deg, var(--primary) 0%, #1d4ed8 100%);
            color: var(--white);
            padding: 30px;
            text-align: center;
            position: relative;
        }

        h1 {
            font-size: 2.5rem;
            margin-bottom: 10px;
        }

        .subtitle {
            font-size: 1.1rem;
            opacity: 0.9;
        }

        .status-badge {
            display: inline-block;
            padding: 8px 16px;
            border-radius: 20px;
            font-weight: bold;
            margin-top: 15px;
        }

        .status-good { background: var(--success); color: var(--white); }
        .status-warning { background: var(--warning); color: var(--white); }
        .status-critical { background: var(--danger); color: var(--white); }
        .status-unknown { background: var(--dark); color: var(--white); }

        .dashboard {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 20px;
            padding: 30px;
        }

        .card {
            background: var(--white);
            border-radius: 15px;
            padding: 25px;
            box-shadow: 0 10px 30px rgba(0, 0, 0, 0.1);
            transition: transform 0.3s ease, box-shadow 0.3s ease;
        }

        .card:hover {
            transform: translateY(-5px);
            box-shadow: 0 15px 40px rgba(0, 0, 0, 0.15);
        }

        .card-header {
            display: flex;
            align-items: center;
            margin-bottom: 20px;
            padding-bottom: 15px;
            border-bottom: 2px solid var(--light);
        }

        .card-header i {
            font-size: 1.5rem;
            margin-right: 12px;
            color: var(--primary);
        }

        .card-title {
            font-size: 1.3rem;
            font-weight: 600;
            color: var(--dark);
        }

        .sensor-value {
            font-size: 2.5rem;
            font-weight: bold;
            margin: 15px 0;
            color: var(--primary);
        }

        .sensor-unit {
            font-size: 1rem;
            color: #6b7280;
            margin-left: 5px;
        }

        .sensor-status {
            display: inline-block;
            padding: 5px 12px;
            border-radius: 20px;
            font-size: 0.9rem;
            font-weight: 500;
        }

        .status-normal { background: #dcfce7; color: #166534; }
        .status-warning { background: #fef3c7; color: #92400e; }
        .status-critical { background: #fee2e2; color: #b91c1c; }

        .trend-indicator {
            display: inline-flex;
            align-items: center;
            margin-left: 10px;
            font-size: 0.9rem;
        }

        .trend-up { color: var(--danger); }
        .trend-down { color: var(--success); }
        .trend-stable { color: var(--warning); }

        .alerts-section {
            margin-top: 30px;
        }

        .alert-item {
            background: var(--light);
            border-left: 4px solid var(--danger);
            padding: 15px;
            margin-bottom: 10px;
            border-radius: 8px;
            display: flex;
            align-items: center;
        }

        .alert-item i {
            color: var(--danger);
            margin-right: 10px;
            font-size: 1.2rem;
        }

        .recommendations-section {
            margin-top: 20px;
        }

        .recommendation-item {
            background: #f0f9ff;
            border-left: 4px solid var(--primary);
            padding: 15px;
            margin-bottom: 10px;
            border-radius: 8px;
            display: flex;
            align-items: center;
        }

        .recommendation-item i {
            color: var(--primary);
            margin-right: 10px;
            font-size: 1.2rem;
        }

        .system-info {
            background: var(--light);
            padding: 15px;
            border-radius: 10px;
            margin-top: 20px;
            display: flex;
            justify-content: space-between;
            align-items: center;
        }

        .system-info-item {
            display: flex;
            align-items: center;
        }

        .system-info-item i {
            margin-right: 8px;
            color: var(--primary);
        }

        .last-update {
            font-size: 0.9rem;
            color: #6b7280;
            margin-top: 10px;
            text-align: center;
        }

        @media (max-width: 768px) {
            .dashboard {
                grid-template-columns: 1fr;
            }
            
            h1 {
                font-size: 2rem;
            }
            
            .sensor-value {
                font-size: 2rem;
            }
        }

        .loading {
            text-align: center;
            padding: 50px;
            color: #6b7280;
        }

        .loading i {
            font-size: 3rem;
            margin-bottom: 20px;
            color: var(--primary);
            animation: spin 2s linear infinite;
        }

        @keyframes spin {
            0% { transform: rotate(0deg); }
            100% { transform: rotate(360deg); }
        }
    </style>
</head>
<body>
    <div class="container">
        <header>
            <h1><i class="fas fa-fish"></i> Smart Fish Pond Monitor</h1>
            <p class="subtitle">Real-time Aquaculture Water Quality Monitoring System</p>
            <div id="status-badge" class="status-badge status-unknown">Initializing...</div>
        </header>

        <div id="dashboard" class="dashboard">
            <div id="loading" class="loading">
                <i class="fas fa-spinner"></i>
                <p>Loading monitoring data...</p>
            </div>
        </div>

        <div class="alerts-section" id="alerts-section">
            <!-- Alerts will be populated here -->
        </div>

        <div class="recommendations-section" id="recommendations-section">
            <!-- Recommendations will be populated here -->
        </div>

        <div class="system-info">
            <div class="system-info-item">
                <i class="fas fa-clock"></i>
                <span>Last Update: <span id="last-update">--:--:--</span></span>
            </div>
            <div class="system-info-item">
                <i class="fas fa-tachometer-alt"></i>
                <span>System Status: <span id="system-status">Initializing</span></span>
            </div>
            <div class="system-info-item">
                <i class="fas fa-database"></i>
                <span>Data Points: <span id="data-points">0</span></span>
            </div>
        </div>

        <div class="last-update">
            <i class="fas fa-info-circle"></i>
            Data refreshes every 5 seconds. Press Ctrl+C in terminal to stop monitoring.
        </div>
    </div>

    <script>
        // Global variables
        let monitoringData = null;
        let intervalId = null;

        // Function to update the dashboard
        function updateDashboard() {
            fetch('/api/data')
                .then(response => response.json())
                .then(data => {
                    monitoringData = data;
                    renderDashboard(data);
                })
                .catch(error => {
                    console.error('Error fetching data:', error);
                    document.getElementById('dashboard').innerHTML = `
                        <div class="card">
                            <div class="card-header">
                                <i class="fas fa-exclamation-triangle"></i>
                                <h2 class="card-title">Connection Error</h2>
                            </div>
                            <p>Failed to connect to monitoring system. Please check the terminal.</p>
                        </div>
                    `;
                });
        }

        // Function to render the dashboard
        function renderDashboard(data) {
            if (!data || !data.status) {
                return;
            }

            const status = data.status;
            const readings = data.sensor_readings;
            const trends = status.trends || {};
            const alerts = status.alerts || [];
            const recommendations = status.recommendations || [];

            // Update status badge
            const statusBadge = document.getElementById('status-badge');
            statusBadge.className = `status-badge status-${status.overall.toLowerCase()}`;
            statusBadge.textContent = status.overall.toUpperCase();

            // Create dashboard cards
            let dashboardHTML = '';

            // Temperature card
            dashboardHTML += createSensorCard(
                'Temperature',
                'fas fa-thermometer-half',
                readings.temperature,
                '°C',
                status.overall,
                trends.temperature
            );

            // pH card
            dashboardHTML += createSensorCard(
                'pH Level',
                'fas fa-flask',
                readings.ph,
                '',
                status.overall,
                trends.ph
            );

            // EC card
            dashboardHTML += createSensorCard(
                'Electrical Conductivity',
                'fas fa-bolt',
                readings.ec,
                ' μS/cm',
                status.overall,
                null
            );

            // Nitrogen card
            dashboardHTML += createSensorCard(
                'Nitrogen',
                'fas fa-atom',
                readings.nitrogen,
                ' mg/kg',
                status.overall,
                trends.nitrogen
            );

            // Phosphorus card
            dashboardHTML += createSensorCard(
                'Phosphorus',
                'fas fa-microscope',
                readings.phosphorus,
                ' mg/kg',
                status.overall,
                trends.phosphorus
            );

            // Turbidity card
            dashboardHTML += createSensorCard(
                'Turbidity',
                'fas fa-water',
                readings.turbidity,
                ' %',
                status.overall,
                null
            );

            document.getElementById('dashboard').innerHTML = dashboardHTML;

            // Update alerts
            const alertsSection = document.getElementById('alerts-section');
            if (alerts.length > 0) {
                let alertsHTML = '<h3><i class="fas fa-exclamation-circle"></i> Active Alerts</h3>';
                alerts.forEach(alert => {
                    alertsHTML += `
                        <div class="alert-item">
                            <i class="fas fa-exclamation-triangle"></i>
                            <span>${alert}</span>
                        </div>
                    `;
                });
                alertsSection.innerHTML = alertsHTML;
            } else {
                alertsSection.innerHTML = '<h3><i class="fas fa-check-circle"></i> No Active Alerts</h3>';
            }

            // Update recommendations
            const recommendationsSection = document.getElementById('recommendations-section');
            if (recommendations.length > 0) {
                let recommendationsHTML = '<h3><i class="fas fa-lightbulb"></i> Recommendations</h3>';
                recommendations.forEach(rec => {
                    recommendationsHTML += `
                        <div class="recommendation-item">
                            <i class="fas fa-hand-point-right"></i>
                            <span>${rec}</span>
                        </div>
                    `;
                });
                recommendationsSection.innerHTML = recommendationsHTML;
            } else {
                recommendationsSection.innerHTML = '<h3><i class="fas fa-thumbs-up"></i> No Recommendations</h3>';
            }

            // Update system info
            document.getElementById('last-update').textContent = data.last_update || '--:--:--';
            document.getElementById('system-status').textContent = data.system_status || 'Unknown';
            document.getElementById('data-points').textContent = 
                (data.historical_data?.temp_history?.length || 0) + ' points';
        }

        // Function to create sensor card HTML
        function createSensorCard(title, icon, value, unit, overallStatus, trend) {
            if (value === null || value === undefined) {
                value = '--';
            }

            let trendHTML = '';
            if (trend) {
                const trendIcon = trend === 'INCREASING' ? 'fa-arrow-up' : 
                                trend === 'DECREASING' ? 'fa-arrow-down' : 'fa-minus';
                const trendColor = trend === 'INCREASING' ? 'trend-up' : 
                                 trend === 'DECREASING' ? 'trend-down' : 'trend-stable';
                trendHTML = `<span class="trend-indicator ${trendColor}">
                    <i class="fas ${trendIcon}"></i> ${trend}
                </span>`;
            }

            const statusClass = overallStatus === 'GOOD' ? 'status-normal' : 
                             overallStatus === 'WARNING' ? 'status-warning' : 
                             overallStatus === 'CRITICAL' ? 'status-critical' : 'status-normal';

            return `
                <div class="card">
                    <div class="card-header">
                        <i class="fas ${icon}"></i>
                        <h2 class="card-title">${title}</h2>
                    </div>
                    <div class="sensor-value">
                        ${value}
                        <span class="sensor-unit">${unit}</span>
                    </div>
                    <div class="sensor-status ${statusClass}">
                        ${overallStatus}
                    </div>
                    ${trendHTML}
                </div>
            `;
        }

        // Initialize the dashboard
        document.addEventListener('DOMContentLoaded', function() {
            updateDashboard();
            intervalId = setInterval(updateDashboard, 5000);
        });

        // Cleanup on page unload
        window.addEventListener('beforeunload', function() {
            if (intervalId) {
                clearInterval(intervalId);
            }
        });
    </script>
</body>
</html>