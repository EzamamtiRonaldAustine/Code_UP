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

# --- Configuration ---
TEMP_READ_INTERVAL = 15  # seconds between readings
LCD_REFRESH_INTERVAL = 5  # seconds between LCD screen changes
PUMP_RUN_DURATION = {
    "SHORT": 120,   # 2 minutes
    "NORMAL": 300,  # 5 minutes
    "LONG": 600     # 10 minutes
}
SMS_COOLDOWN = 300  # seconds (5 minutes) - RENAMED FOR CLARITY
CRITICAL_DURATION = 300 # seconds (5 minutes) - NEW SUSTAINED CRITICAL CHECK
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

# --- GSM Configuration ---
GSM_PORT = "/dev/serial0"
GSM_BAUDRATE = 9600
PHONE_NUMBERS = ["+256764152908", "+256770701680"]  # Your phone numbers

class SmartFishPondMonitor:
    def __init__(self):
        # --- Initialize System State ---
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
                'last_lcd_content': ""
            },
            'sms': {
                'last_sent_time': 0
            },
            # NEW: State for tracking sustained critical condition
            'critical': {
                'start_time': None, # Tracks when the critical period started
                'sustained': False # Flag to check if condition has been met for the duration
            }
        }

        # --- Initialize Historical Data ---
        self.history = {
            'temp': deque(maxlen=HISTORY_SIZE),
            'ph': deque(maxlen=HISTORY_SIZE),
            'ec': deque(maxlen=HISTORY_SIZE),
            'nitrogen': deque(maxlen=HISTORY_SIZE),
            'phosphorus': deque(maxlen=HISTORY_SIZE),
            'turbidity': deque(maxlen=HISTORY_SIZE)
        }

        # --- Initialize GPIO ---
        GPIO.setmode(GPIO.BCM)
        GPIO.setup(TURBIDITY_PIN, GPIO.IN, pull_up_down=GPIO.PUD_UP)
        GPIO.setup(BLUE_LED_PIN, GPIO.OUT)
        GPIO.setup(YELLOW_LED_PIN, GPIO.OUT)
        GPIO.setup(RED_LED_PIN, GPIO.OUT)
        GPIO.setup(BUZZER_PIN, GPIO.OUT)
        GPIO.setup(PUMP_PIN, GPIO.OUT)

        # Initialize Buzzer with PWM
        self.pwm_buzzer = GPIO.PWM(BUZZER_PIN, 1000)
        self.pwm_buzzer.start(0)

        # Initialize all indicators to OFF
        self.set_leds(0, 0, 0)
        GPIO.output(PUMP_PIN, GPIO.HIGH)  # Ensure pump is OFF

        # --- Initialize Peripherals ---
        self.lcd = self._init_lcd()
        self.rs485_instrument = self._init_rs485()
        self.device_file = self._init_ds18b20()
        self.gsm = self._init_gsm()

        # --- Start Threads ---
        self.monitor_thread = threading.Thread(target=self.monitor_loop)
        self.display_thread = threading.Thread(target=self.display_loop)
        self.pump_thread = threading.Thread(target=self.pump_control_loop)

        self.monitor_thread.daemon = True
        self.display_thread.daemon = True
        self.pump_thread.daemon = True

        self.monitor_thread.start()
        self.display_thread.start()
        self.pump_thread.start()

    def _init_lcd(self):
        try:
            lcd = CharLCD('PCF8574', 0x27)
            lcd.clear()
            lcd.write_string("Initializing...")
            print("✅ LCD initialized")
            return lcd
        except Exception as e:
            print(f"❌ LCD initialization failed: {e}")
            return None

    def _init_rs485(self):
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

    def _init_ds18b20(self):
        try:
            os.system('modprobe w1-gpio')
            os.system('modprobe w1-therm')
            base_dir = '/sys/bus/w1/devices/'
            device_folder = glob.glob(base_dir + '28-*')[0]
            device_file = device_folder + '/w1_slave'
            print("✅ DS18B20 temperature sensor initialized")
            return device_file
        except (IndexError, Exception) as e:
            print(f"❌ DS18B20 initialization failed: {e}. Check 1-Wire is enabled in raspi-config.")
            return None

    def _init_gsm(self):
        try:
            ser = serial.Serial(port=GSM_PORT, baudrate=GSM_BAUDRATE, timeout=5)
            self.send_at_command(ser, "AT", 1)
            self.send_at_command(ser, "ATE0", 1)
            self.send_at_command(ser, "AT+CMGF=1", 1)
            print("✅ GSM module initialized")
            return ser
        except Exception as e:
            print(f"❌ GSM initialization failed: {e}")
            return None

    def send_at_command(self, ser, command, delay=1):
        try:
            ser.write((command + "\r\n").encode())
            time.sleep(delay)
            return ser.read_all().decode(errors="ignore").strip()
        except Exception as e:
            print(f"Error sending AT command '{command}': {e}")
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
                    if -10 < temp_c < 60:  # Sanity check
                        return temp_c
        except Exception as e:
            print(f"Error reading DS18B20: {e}")
        return None

    def read_turbidity(self):
        try:
            return GPIO.input(TURBIDITY_PIN) == 0
        except:
            return None

    def read_rs485_sensor(self):
        if not self.rs485_instrument:
            return {}
        data = {}
        registers = {
            'temperature': 19, 'ph': 13, 'ec': 7,
            'nitrogen': 4, 'phosphorus': 5, 'potassium': 6
        }
        # Read temperature first for pH calculation
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
        return data

    def _read_register_with_retry(self, register, retries=2):
        for attempt in range(retries):
            try:
                value = self.rs485_instrument.read_register(register, 1, functioncode=3)
                return value
            except Exception as e:
                print(f"RS485 read attempt {attempt + 1} failed for reg {register}: {e}")
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
            'overall': 'GOOD', 'score': 0, 'alerts': [], 'recommendations': set(), 'trends': {}
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
        
        # (Scoring logic remains the same)
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
        
        if sum(self.history['turbidity']) / len(self.history['turbidity']) > 0.7:
            status['score'] += 25
            status['alerts'].append(f"⚠️ Water is consistently turbid")
            status['recommendations'].add('Check filter and perform water change')
        
        if avg_nitrogen is not None and avg_nitrogen > 5:
            status['score'] += 30
            status['alerts'].append(f"🚨 Nitrogen extremely high: {avg_nitrogen:.1f} mg/kg")
            status['recommendations'].add('Reduce feeding and perform water change')
        
        if avg_phosphorus is not None and avg_phosphorus > 1:
            status['score'] += 30
            status['alerts'].append(f"🚨 Phosphorus extremely high: {avg_phosphorus:.1f} mg/kg")
            status['recommendations'].add('Reduce feeding and perform water change')
        
        if status['score'] >= 70:
            status['overall'] = 'CRITICAL'
        elif status['score'] >= 40:
            status['overall'] = 'WARNING'
        
        return status

    def set_leds(self, blue, yellow, red):
        GPIO.output(BLUE_LED_PIN, blue)
        GPIO.output(YELLOW_LED_PIN, yellow)
        GPIO.output(RED_LED_PIN, red)

    def update_indicators(self, status):
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

    def send_sms_alert(self, status):
        # --- NEW LOGIC: Check for sustained critical condition ---
        if status['overall'] != 'CRITICAL' or not self.gsm:
            return

        # If this is the first time entering critical state, start the timer
        if not self.state['critical']['sustained']:
            print("  -> INFO: Critical condition detected. Starting 5-minute timer before sending SMS.")
            self.state['critical']['start_time'] = time.time()
            self.state['critical']['sustained'] = True
            return # Do not send SMS yet

        # Check if the critical condition has persisted for the required duration
        if self.state['critical']['sustained'] and \
           (time.time() - self.state['critical']['start_time'] > CRITICAL_DURATION):
            print("  -> ACTION: Sustained critical condition confirmed. Sending SMS alert.")
            self._send_sms_message(status)
            self.state['sms']['last_sent_time'] = time.time()
            # Reset the sustained flag so we don't spam SMS
            self.state['critical']['sustained'] = False

    def _send_sms_message(self, status):
        message = f"🚨 POND ALERT ({status['overall']})\n"
        message += f"Time: {datetime.now().strftime('%Y-%m-%d %H:%M')}\n\n"
        message += "Critical Issues:\n" + "\n".join(status['alerts'][:3])
        message += f"\nActions:\n" + "\n".join(list(status['recommendations'])[:2])

        for phone in PHONE_NUMBERS:
            try:
                self.gsm.write(f'AT+CMGS="{phone}"\r\n'.encode())
                time.sleep(1)
                self.gsm.write(message.encode())
                time.sleep(0.5)
                self.gsm.write(b'\x1A')
                time.sleep(5) # Wait for network confirmation
                final_response = self.gsm.read_all().decode(errors="ignore")
                if "+CMGS:" in final_response:
                    print(f"✅ SMS sent to {phone}")
                else:
                    print(f"❌ SMS failed to {phone}: {final_response.strip()}")
            except Exception as e:
                print(f"Error sending SMS to {phone}: {e}")

    def pump_control_loop(self):
        while self.state['running']:
            if self.state['pump']['should_run'] and not self.state['pump']['is_running']:
                print(f"  -> ACTION: Activating PUMP in {self.state['pump']['mode']} mode.")
                GPIO.output(PUMP_PIN, GPIO.LOW)
                self.state['pump']['is_running'] = True
                self.state['pump']['start_time'] = time.time()
                self.state['pump']['should_run'] = False
            
            if self.state['pump']['is_running']:
                run_duration = PUMP_RUN_DURATION.get(self.state['pump']['mode'], 300)
                if time.time() - self.state['pump']['start_time'] > run_duration:
                    print(f"  -> ACTION: {self.state['pump']['mode']} pump cycle complete. Turning PUMP OFF.")
                    GPIO.output(PUMP_PIN, GPIO.HIGH)
                    self.state['pump']['is_running'] = False
                    self.state['pump']['mode'] = "OFF"
            
            time.sleep(1)

    def _update_lcd_content(self, status):
        if not self.lcd:
            return
        
        content = ""
        if status['overall'] in ['WARNING', 'CRITICAL']:
            content = f"Status: {status['overall']}\n{status['alerts'][0][:16]}"
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

    def display_loop(self):
        while self.state['running']:
            try:
                if self.state.get('last_status_full'):
                    self._update_lcd_content(self.state['last_status_full'])
                time.sleep(LCD_REFRESH_INTERVAL)
            except Exception as e:
                print(f"Error in display_loop: {e}")
                time.sleep(5)

    def monitor_loop(self):
        while self.state['running']:
            try:
                rs485_data = self.read_rs485_sensor()
                ds18b20_temp = self.read_ds18b20_temp()
                
                if not rs485_data:
                    print("\n❌ ERROR: Failed to read from RS485 sensor.")
                    time.sleep(TEMP_READ_INTERVAL)
                    continue

                status = self.get_water_quality_status(rs485_data, ds18b20_temp)
                
                # --- NEW LOGIC: Handle sustained critical state ---
                if status['overall'] == 'CRITICAL':
                    if not self.state['critical']['sustained']:
                        # Start the timer on first entry into critical state
                        if self.state['critical']['start_time'] is None:
                            self.state['critical']['start_time'] = time.time()
                            self.state['critical']['sustained'] = True
                            print("  -> INFO: Critical condition detected. Starting 5-minute timer before sending SMS.")
                    else:
                        # If already sustained, check if it's time to send SMS
                        self.send_sms_alert(status)
                else:
                    # If status is no longer critical, reset the critical state
                    if self.state['critical']['sustained']:
                        print("  -> INFO: Condition recovered. Resetting critical timer.")
                        self.state['critical']['start_time'] = None
                        self.state['critical']['sustained'] = False

                self.update_indicators(status)
                self.state['indicators']['last_status'] = status['overall']
                self.state['last_status_full'] = status # Store the full status for the display loop

                time.sleep(TEMP_READ_INTERVAL)
            except KeyboardInterrupt:
                self.state['running'] = False
            except Exception as e:
                print(f"Error in monitor_loop: {e}")
                time.sleep(5)

    def cleanup(self):
        self.state['running'] = False
        self.set_leds(0, 0, 0)
        if self.pwm_buzzer:
            self.pwm_buzzer.stop()
        if self.lcd:
            self.lcd.clear()
            self.lcd.write_string("System stopped")
        
        GPIO.output(PUMP_PIN, GPIO.HIGH)
        print("Pump turned OFF.")
        
        if self.gsm:
            self.gsm.close()
            print("GSM module closed.")
        
        GPIO.cleanup()
        print("\n✅ System cleanup complete")

def main():
    print("Smart Fish Pond Monitoring System v3.2 (Sustained Critical SMS)")
    try:
        monitor = SmartFishPondMonitor()
        print("✅ System initialized. Monitoring started. Press Ctrl+C to stop.")
        while monitor.state['running']:
            time.sleep(1)
    except KeyboardInterrupt:
        print("\nStopping system...")
        monitor.cleanup()

if __name__ == "__main__":
    main()