/*
  ╔════════════════════════════════════════════════════════╗
  ║  SMART FISH POND MANAGEMENT SYSTEM                     ║
  ║  Arduino MEGA2560 Firmware - Proteus Simulation        ║
  ║  Author: Ezamamti Ronald A                             ║
  ║  Version: 2.0 (Arduino MEGA2560)                       ║
  ╚════════════════════════════════════════════════════════╝
*/

#include <LiquidCrystal.h>

// ==================== PIN DEFINITIONS ====================
// Analog Sensors (ADC Inputs)
#define TEMP_PIN        A0  // LM35 Temperature Sensor
#define PH_PIN          A1  // pH Meter Sensor
#define TURB_PIN        A2  // Turbidity Sensor (POT simulation)
#define AMMONIA_PIN     A3  // Ammonia Sensor (POT simulation)
#define DO_PIN          A4  // Dissolved Oxygen Sensor (POT simulation)

// Ultrasonic Water Level Sensor
#define TRIG_PIN        22  // Trigger pin
#define ECHO_PIN        23  // Echo pin

// LCD Display (4-bit mode)
#define LCD_RS          24
#define LCD_EN          25
#define LCD_D4          26
#define LCD_D5          27
#define LCD_D6          28
#define LCD_D7          29

// Actuators (Digital Outputs)
#define RELAY_AERATOR   30  // Relay controlling aerator motor
#define RELAY_PUMP      31  // Relay controlling water pump

// Indicators (Digital Outputs)
#define GREEN_LED       32  // Normal status indicator
#define ORANGE_LED      33  // Warning status indicator
#define RED_LED         34  // Alert status indicator
#define BUZZER          35  // Audio alarm

// ==================== THRESHOLDS ====================
// Temperature (°C)
#define TEMP_MAX        32.0
#define TEMP_MIN        20.0
#define TEMP_WARNING    30.0

// pH
#define PH_MIN          6.5
#define PH_MAX          8.5
#define PH_WARNING_LOW  6.8
#define PH_WARNING_HIGH 8.2

// Turbidity (NTU)
#define TURB_MAX        50.0
#define TURB_WARNING    40.0

// Ammonia (ppm)
#define NH3_MAX         0.05
#define NH3_WARNING     0.03

// Dissolved Oxygen (mg/L)
#define DO_MIN          5.0
#define DO_WARNING      6.0

// Water Level (cm)
#define WATER_LEVEL_MIN 10.0

// ==================== GLOBAL VARIABLES ====================
LiquidCrystal lcd(LCD_RS, LCD_EN, LCD_D4, LCD_D5, LCD_D6, LCD_D7);

// Sensor readings
float temperature = 0.0;
float pH = 0.0;
float turbidity = 0.0;
float ammonia = 0.0;
float dissolvedOxygen = 0.0;
float waterLevel = 0.0;

// System status flags
bool alertTriggered = false;
bool warningTriggered = false;
bool aeratorActive = false;
bool pumpActive = false;

// GSM alert timing
unsigned long lastGSMAlert = 0;
const unsigned long GSM_ALERT_INTERVAL = 300000; // 5 minutes

// Update intervals
unsigned long lastSensorRead = 0;
const unsigned long SENSOR_READ_INTERVAL = 2000; // 2 seconds

unsigned long lastDisplayUpdate = 0;
const unsigned long DISPLAY_UPDATE_INTERVAL = 1000; // 1 second

// ==================== SETUP ====================
void setup() {
  // Initialize Serial Communications
  Serial.begin(9600);   // Virtual Terminal (debugging) - Serial0
  Serial1.begin(9600);  // GSM Module (SIM900D) - Serial1
  
  // Initialize LCD (16 columns x 2 rows)
  lcd.begin(16, 2);
  lcd.clear();
  
  // Display startup message
  lcd.setCursor(0, 0);
  lcd.print("  FISH  POND");
  lcd.setCursor(0, 1);
  lcd.print("INITIALIZING...");
  
  // Configure Pin Modes - Actuators
  pinMode(RELAY_AERATOR, OUTPUT);
  pinMode(RELAY_PUMP, OUTPUT);
  pinMode(GREEN_LED, OUTPUT);
  pinMode(ORANGE_LED, OUTPUT);
  pinMode(RED_LED, OUTPUT);
  pinMode(BUZZER, OUTPUT);
  
  // Configure Pin Modes - Sensors
  pinMode(TRIG_PIN, OUTPUT);
  pinMode(ECHO_PIN, INPUT);
  
  // Set Initial States (All OFF)
  digitalWrite(RELAY_AERATOR, LOW);
  digitalWrite(RELAY_PUMP, LOW);
  digitalWrite(GREEN_LED, HIGH);  // Start with normal status
  digitalWrite(ORANGE_LED, LOW);
  digitalWrite(RED_LED, LOW);
  digitalWrite(BUZZER, LOW);
  
  delay(2000);
  
  // Initialize GSM Module
  initGSM();
  
  // Clear LCD and show ready message
  lcd.clear();
  lcd.setCursor(0, 0);
  lcd.print("SYSTEM  READY");
  delay(1500);
  lcd.clear();
  
  // Print startup message to Serial
  Serial.println("╔════════════════════════════════════════╗");
  Serial.println("║ SMART FISH POND MANAGEMENT SYSTEM      ║");
  Serial.println("║ Arduino MEGA2560 - System Ready        ║");
  Serial.println("╚════════════════════════════════════════╝");
  Serial.println();
  
  lastSensorRead = millis();
  lastDisplayUpdate = millis();
}

// ==================== MAIN LOOP ====================
void loop() {
  unsigned long currentMillis = millis();
  
  // Read sensors at defined interval
  if (currentMillis - lastSensorRead >= SENSOR_READ_INTERVAL) {
    readAllSensors();
    checkWaterQuality();
    controlActuators();
    logDataToSerial();
    
    // Send GSM alert if needed (throttled)
    if (alertTriggered && (currentMillis - lastGSMAlert >= GSM_ALERT_INTERVAL)) {
      sendGSMAlert();
      lastGSMAlert = currentMillis;
    }
    
    lastSensorRead = currentMillis;
  }
  
  // Update LCD display at defined interval
  if (currentMillis - lastDisplayUpdate >= DISPLAY_UPDATE_INTERVAL) {
    updateLCDDisplay();
    lastDisplayUpdate = currentMillis;
  }
}

// ==================== SENSOR READING FUNCTIONS ====================

void readAllSensors() {
  // Read Temperature (LM35: 10mV/°C, Arduino ADC: 0-1023 for 0-5V)
  int tempRaw = analogRead(TEMP_PIN);
  temperature = (tempRaw * 5.0 / 1023.0) * 100.0;
  
  // Read pH (0-14 pH mapped to 0-5V)
  int phRaw = analogRead(PH_PIN);
  pH = (phRaw * 14.0) / 1023.0;
  
  // Read Turbidity (0-100 NTU mapped to 0-5V)
  int turbRaw = analogRead(TURB_PIN);
  turbidity = (turbRaw * 100.0) / 1023.0;
  
  // Read Ammonia (0-1 ppm mapped to 0-5V)
  int ammoniaRaw = analogRead(AMMONIA_PIN);
  ammonia = (ammoniaRaw * 1.0) / 1023.0;
  
  // Read Dissolved Oxygen (0-20 mg/L mapped to 0-5V)
  int doRaw = analogRead(DO_PIN);
  dissolvedOxygen = (doRaw * 20.0) / 1023.0;
  
  // Read Water Level (Ultrasonic sensor)
  waterLevel = getWaterLevel();
}

float getWaterLevel() {
  // Send ultrasonic pulse
  digitalWrite(TRIG_PIN, LOW);
  delayMicroseconds(2);
  digitalWrite(TRIG_PIN, HIGH);
  delayMicroseconds(10);
  digitalWrite(TRIG_PIN, LOW);
  
  // Measure echo duration (timeout 30ms)
  long duration = pulseIn(ECHO_PIN, HIGH, 30000);
  
  // Calculate distance in cm (speed of sound = 343 m/s)
  float distance = (duration * 0.0343) / 2.0;
  
  // Convert to water level (sensor mounted 100cm above pond bottom)
  float level = 100.0 - distance;
  
  // Constrain to valid range
  if (level < 0) level = 0;
  if (level > 100) level = 100;
  
  return level;
}

// ==================== WATER QUALITY ANALYSIS ====================

void checkWaterQuality() {
  alertTriggered = false;
  warningTriggered = false;
  
  // ===== CRITICAL CONDITIONS (ALERT) =====
  
  // Temperature Check
  if (temperature > TEMP_MAX) {
    alertTriggered = true;
    Serial.println("⚠️  ALERT: Temperature TOO HIGH!");
  } else if (temperature < TEMP_MIN) {
    alertTriggered = true;
    Serial.println("⚠️  ALERT: Temperature TOO LOW!");
  }
  
  // pH Check
  if (pH < PH_MIN) {
    alertTriggered = true;
    Serial.println("⚠️  ALERT: pH TOO LOW (Acidic)!");
  } else if (pH > PH_MAX) {
    alertTriggered = true;
    Serial.println("⚠️  ALERT: pH TOO HIGH (Alkaline)!");
  }
  
  // Turbidity Check
  if (turbidity > TURB_MAX) {
    alertTriggered = true;
    Serial.println("⚠️  ALERT: High Turbidity Detected!");
  }
  
  // Ammonia Check
  if (ammonia > NH3_MAX) {
    alertTriggered = true;
    Serial.println("⚠️  ALERT: Ammonia Level CRITICAL!");
  }
  
  // Dissolved Oxygen Check
  if (dissolvedOxygen < DO_MIN) {
    alertTriggered = true;
    Serial.println("⚠️  ALERT: Dissolved Oxygen TOO LOW!");
  }
  
  // Water Level Check
  if (waterLevel < WATER_LEVEL_MIN) {
    alertTriggered = true;
    Serial.println("⚠️  ALERT: Water Level CRITICALLY LOW!");
  }
  
  // ===== WARNING CONDITIONS (Approaching thresholds) =====
  
  if (!alertTriggered) {
    if (temperature > TEMP_WARNING && temperature <= TEMP_MAX) {
      warningTriggered = true;
    }
    if (pH < PH_WARNING_LOW && pH >= PH_MIN) {
      warningTriggered = true;
    }
    if (pH > PH_WARNING_HIGH && pH <= PH_MAX) {
      warningTriggered = true;
    }
    if (turbidity > TURB_WARNING && turbidity <= TURB_MAX) {
      warningTriggered = true;
    }
    if (ammonia > NH3_WARNING && ammonia <= NH3_MAX) {
      warningTriggered = true;
    }
    if (dissolvedOxygen < DO_WARNING && dissolvedOxygen >= DO_MIN) {
      warningTriggered = true;
    }
  }
}

// ==================== ACTUATOR CONTROL ====================

void controlActuators() {
  if (alertTriggered) {
    // ===== ALERT STATE =====
    
    // Turn on alert indicators
    digitalWrite(RED_LED, HIGH);
    digitalWrite(GREEN_LED, LOW);
    digitalWrite(ORANGE_LED, HIGH);
    digitalWrite(BUZZER, HIGH);
    
    // Activate aerator if DO is low
    if (dissolvedOxygen < DO_MIN) {
      digitalWrite(RELAY_AERATOR, HIGH);
      aeratorActive = true;
      if (!aeratorActive) { // Log only on state change
        Serial.println("✓ ACTION: Aerator ACTIVATED (Low DO)");
      }
    } else {
      digitalWrite(RELAY_AERATOR, LOW);
      aeratorActive = false;
    }
    
    // Activate pump if temp high, ammonia high, or turbidity high
    if (temperature > TEMP_MAX || ammonia > NH3_MAX || turbidity > TURB_MAX) {
      digitalWrite(RELAY_PUMP, HIGH);
      pumpActive = true;
      if (!pumpActive) { // Log only on state change
        Serial.println("✓ ACTION: Water Pump ACTIVATED (Temp/Ammonia/Turbidity)");
      }
    } else {
      digitalWrite(RELAY_PUMP, LOW);
      pumpActive = false;
    }
    
  } else if (warningTriggered) {
    // ===== WARNING STATE =====
    
    digitalWrite(RED_LED, LOW);
    digitalWrite(GREEN_LED, LOW);
    digitalWrite(ORANGE_LED, HIGH);
    digitalWrite(BUZZER, LOW);
    digitalWrite(RELAY_AERATOR, LOW);
    digitalWrite(RELAY_PUMP, LOW);
    aeratorActive = false;
    pumpActive = false;
    
  } else {
    // ===== NORMAL STATE =====
    
    digitalWrite(RED_LED, LOW);
    digitalWrite(GREEN_LED, HIGH);
    digitalWrite(ORANGE_LED, LOW);
    digitalWrite(BUZZER, LOW);
    digitalWrite(RELAY_AERATOR, LOW);
    digitalWrite(RELAY_PUMP, LOW);
    aeratorActive = false;
    pumpActive = false;
  }
}

// ==================== LCD DISPLAY ====================

void updateLCDDisplay() {
  lcd.clear();
  
  // Line 1: Temperature and pH
  lcd.setCursor(0, 0);
  lcd.print("T:");
  lcd.print(temperature, 1);
  lcd.print("C pH:");
  lcd.print(pH, 1);
  
  // Line 2: Status or Key Parameters
  lcd.setCursor(0, 1);
  
  if (alertTriggered) {
    lcd.print("ALERT! CHECK SYS");
  } else if (warningTriggered) {
    lcd.print("WARNING:MONITOR ");
  } else {
    lcd.print("DO:");
    lcd.print(dissolvedOxygen, 1);
    lcd.print(" L:");
    lcd.print(waterLevel, 0);
    lcd.print("cm");
  }
}

// ==================== SERIAL LOGGING ====================

void logDataToSerial() {
  Serial.println("════════════════════════════════════════");
  Serial.println("    WATER QUALITY DATA SNAPSHOT");
  Serial.println("════════════════════════════════════════");
  Serial.print("Temperature:      ");
  Serial.print(temperature, 2);
  Serial.println(" °C");
  
  Serial.print("pH Level:         ");
  Serial.println(pH, 2);
  
  Serial.print("Turbidity:        ");
  Serial.print(turbidity, 2);
  Serial.println(" NTU");
  
  Serial.print("Ammonia (NH₃):    ");
  Serial.print(ammonia, 3);
  Serial.println(" ppm");
  
  Serial.print("Dissolved Oxygen: ");
  Serial.print(dissolvedOxygen, 2);
  Serial.println(" mg/L");
  
  Serial.print("Water Level:      ");
  Serial.print(waterLevel, 2);
  Serial.println(" cm");
  
  Serial.println("----------------------------------------");
  Serial.print("System Status:    ");
  
  if (alertTriggered) {
    Serial.println("🔴 ALERT");
  } else if (warningTriggered) {
    Serial.println("🟠 WARNING");
  } else {
    Serial.println("🟢 NORMAL");
  }
  
  Serial.print("Aerator:          ");
  Serial.println(aeratorActive ? "ON" : "OFF");
  
  Serial.print("Water Pump:       ");
  Serial.println(pumpActive ? "ON" : "OFF");
  
  Serial.println("════════════════════════════════════════\n");
}

// ==================== GSM FUNCTIONS ====================

void initGSM() {
  Serial.println("Initializing SIM900D GSM Module...");
  
  Serial1.println("AT");
  delay(1000);
  
  Serial1.println("AT+CMGF=1"); // Set SMS text mode
  delay(1000);
  
  Serial.println("✓ GSM Module Initialized");
}

void sendGSMAlert() {
  Serial.println("╔════════════════════════════════════════╗");
  Serial.println("║  SENDING GSM ALERT SMS...              ║");
  Serial.println("╚════════════════════════════════════════╝");
  
  // Replace with actual phone number
  Serial1.println("AT+CMGS=\"+256700000000\"");
  delay(1000);
  
  // Compose SMS message
  Serial1.print("FISH POND ALERT!\n\n");
  Serial1.print("Critical conditions detected:\n");
  Serial1.print("Temp: ");
  Serial1.print(temperature, 1);
  Serial1.print(" C\n");
  Serial1.print("pH: ");
  Serial1.print(pH, 1);
  Serial1.print("\n");
  Serial1.print("DO: ");
  Serial1.print(dissolvedOxygen, 1);
  Serial1.print(" mg/L\n");
  Serial1.print("NH3: ");
  Serial1.print(ammonia, 2);
  Serial1.print(" ppm\n");
  Serial1.print("Water Level: ");
  Serial1.print(waterLevel, 1);
  Serial1.print(" cm\n\n");
  Serial1.print("CHECK POND IMMEDIATELY!");
  
  Serial1.write(26); // Ctrl+Z to send SMS
  delay(5000);
  
  Serial.println("✓ GSM Alert SMS Sent Successfully");
  Serial.println();
}
// ```

// ---

// # 🚀 **SIMULATION PROCEDURES**

// ## **STEP 1: Prepare Arduino Code**

// ### **1.1 Install ESP32 Board in Arduino IDE**
// ```
// 1. Open Arduino IDE
// 2. File → Preferences
// 3. Additional Board Manager URLs:
//    https://dl.espressif.com/dl/package_esp32_index.json
// 4. Tools → Board → Boards Manager
// 5. Search "ESP32" → Install "ESP32 by Espressif Systems"
// ```

// ### **1.2 Configure Arduino IDE**
// ```
// Tools → Board → ESP32 Arduino → ESP32 Dev Module
// Tools → Upload Speed → 115200
// Tools → Flash Frequency → 80MHz
// Tools → Flash Mode → QIO
// Tools → Flash Size → 4MB
// Tools → Partition Scheme → Default 4MB with spiffs
// Tools → Core Debug Level → None
// Tools → Port → (Select your COM port if uploading to real hardware)
// ```

// ### **1.3 Compile and Export HEX**
// ```
// 1. Copy the complete code above into Arduino IDE
// 2. Click "Verify" (✓ button) to compile
// 3. Sketch → Export Compiled Binary
// 4. Navigate to sketch folder
// 5. Find file: YourSketchName.ino.esp32.bin
// 6. Keep this file ready for Proteus
// ```

// ---

// ## **STEP 2: Configure Proteus Project**

// ### **2.1 Load Firmware into ESP32**
// ```
// 1. Double-click ESP32-WROOM component in Proteus
// 2. In Properties window:
//    - Program File: Browse to your .bin file
//    - Clock Frequency: 240MHz
//    - Crystal Frequency: 40MHz
// 3. Click OK
// ```

// ### **2.2: Configure Virtual Terminal**
// ```
// 1. Double-click COMPIM (Virtual Terminal)
// 2. Set parameters:
//    - Physical Port: (None)
//    - Baud Rate: 9600
//    - Data Bits: 8
//    - Parity: None
//    - Stop Bits: 1
// 3. Click OK
// ```

// ### **2.3: Configure LCD Contrast**
// ```
// 1. Double-click POT-HG #4 (LCD Contrast)
// 2. Set Position: 25%
// 3. Click OK
// ```

// ### **2.4: Configure Sensor Potentiometers**
// ```
// For DO Sensor POT:
// - Double-click POT-HG #1
// - Set Position: 50% (simulates 10 mg/L - normal)
// - Increment: 10%

// For Turbidity POT:
// - Double-click POT-HG #2
// - Set Position: 30% (simulates 30 NTU - normal)

// For Ammonia POT:
// - Double-click POT-HG #3
// - Set Position: 20% (simulates 0.02 ppm - safe)
// ```

// ### **2.5: Configure LM35 Temperature**
// ```
// 1. Double-click LM35 component
// 2. Set Ambient Temperature: 25°C (normal)
// 3. Click OK
// ```

// ### **2.6: Configure pH Sensor**
// ```
// 1. Double-click PH METER component
// 2. Set pH Value: 7.0 (neutral - normal)
// 3. Click OK
// ```

// ### **2.7: Configure Ultrasonic Sensor**
// ```
// 1. Double-click ULTRASONIC V2.0
// 2. Set Distance: 50cm (simulates 50cm water level - normal)
// 3. Click OK
// ```

// ---

// ## **STEP 3: Run Simulation**

// ### **3.1: Initial System Check**
// ```
// 1. Click ▶️ PLAY button (bottom left)
// 2. Expected behavior in first 5 seconds:
//    ✓ Power LEDs illuminate
//    ✓ LCD shows "FISH POND" then "INITIALIZING..."
//    ✓ LCD shows "SYSTEM READY" then clears
//    ✓ Green LED turns ON
//    ✓ Virtual Terminal displays startup banner
// ```

// ### **3.2: Observe Normal Operation**
// ```
// What you should see:
// ✓ LCD Line 1: "T:25.0C pH:7.0"
// ✓ LCD Line 2: "DO:10.0 L:50cm"
// ✓ Green LED: ON
// ✓ Orange LED: OFF
// ✓ Red LED: OFF
// ✓ Buzzer: Silent
// ✓ Both relays: OFF (motors not running)
// ✓ Virtual Terminal: Updates every 2 seconds with water quality data
// ✓ Virtual Terminal: Shows "System Status: 🟢 NORMAL"
// ```

// ---

// ## **STEP 4: Test Alert Scenarios**

// ### **4.1: Test Low Dissolved Oxygen Alert**
// ```
// PROCEDURE:
// 1. Double-click DO POT (POT-HG #1)
// 2. Change Position to: 20% (simulates 4 mg/L - below threshold)
// 3. Click OK
// 4. Wait 2-3 seconds

// EXPECTED RESULTS:
// ✓ LCD Line 2: "ALERT! CHECK SYS"
// ✓ Red LED: ON
// ✓ Orange LED: ON
// ✓ Green LED: OFF
// ✓ Buzzer: ON (beeping)
// ✓ RELAY_AERATOR: Activates → Motor #1 spins
// ✓ Virtual Terminal: "⚠️  ALERT: Dissolved Oxygen TOO LOW!"
// ✓ Virtual Terminal: "✓ ACTION: Aerator ACTIVATED (Low DO)"
// ✓ GSM Module: Sends SMS alert (visible in Serial2 debug if monitored)
// ```

// ### **4.2: Test High Temperature Alert**
// ```
// PROCEDURE:
// 1. Double-click LM35 component
// 2. Set Ambient Temperature: 35°C
// 3. Click OK
// 4. Wait 2-3 seconds

// EXPECTED RESULTS:
// ✓ LCD Line 1: "T:35.0C pH:7.0"
// ✓ LCD Line 2: "ALERT! CHECK SYS"
// ✓ Red LED: ON
// ✓ Buzzer: ON
// ✓ RELAY_PUMP: Activates → Motor #2 (Water Pump) spins
// ✓ Virtual Terminal: "⚠️  ALERT: Temperature TOO HIGH!"
// ✓ Virtual Terminal: "✓ ACTION: Water Pump ACTIVATED"
// ```

// ### **4.3: Test pH Out of Range**
// ```
// PROCEDURE:
// 1. Double-click PH METER component
// 2. Set pH Value: 5.5 (acidic - below threshold)
// 3. Click OK

// EXPECTED RESULTS:
// ✓ LCD shows: "pH:5.5"
// ✓ Alert indicators active
// ✓ Virtual Terminal: "⚠️  ALERT: pH TOO LOW (Acidic)!"
// ```

// ### **4.4: Test High Ammonia**
// ```
// PROCEDURE:
// 1. Double-click Ammonia POT (POT-HG #3)
// 2. Set Position: 80% (simulates 0.08 ppm - critical)
// 3. Click OK

// EXPECTED RESULTS:
// ✓ Red LED: ON
// ✓ RELAY_PUMP: ON (water exchange needed)
// ✓ Virtual Terminal: "⚠️  ALERT: Ammonia Level CRITICAL!"
// ✓ Virtual Terminal: "✓ ACTION: Water Pump ACTIVATED"
// ```

// ### **4.5: Test High Turbidity**
// ```
// PROCEDURE:
// 1. Double-click Turbidity POT (POT-HG #2)
// 2. Set Position: 70% (simulates 70 NTU - high)
// 3. Click OK

// EXPECTED RESULTS:
// ✓ Alert triggered
// ✓ Water pump activates
// ✓ Virtual Terminal: "⚠️  ALERT: High Turbidity Detected!"
// ```

// ### **4.6: Test Low Water Level**
// ```
// PROCEDURE:
// 1. Double-click ULTRASONIC V2.0
// 2. Set Distance: 95cm (water level = 100-95 = 5cm - critical)
// 3. Click OK

// EXPECTED RESULTS:
// ✓ LCD: "L:5cm"
// ✓ Alert system active
// ✓ Virtual Terminal: "⚠️  ALERT: Water Level CRITICALLY LOW!"
// ```

// ### **4.7: Test Warning State**
// ```
// PROCEDURE:
// 1. Reset all sensors to normal (DO at 50%, Temp 25°C, etc.)
// 2. Double-click LM35
// 3. Set Temperature: 30.5°C (warning level, not alert)
// 4. Click OK

// EXPECTED RESULTS:
// ✓ Orange LED: ON
// ✓ Green LED: OFF
// ✓ Red LED: OFF
// ✓ Buzzer: OFF (no alarm)
// ✓ Relays: OFF (no action yet)
// ✓ LCD Line 2: "WARNING:MONITOR"
// ✓ Virtual Terminal: "System Status: 🟠 WARNING"
// ```

// ### **4.8: Test Multiple Simultaneous Alerts**
// ```
// PROCEDURE:
// 1. Set Temperature: 35°C (high)
// 2. Set DO POT: 20% (low - 4 mg/L)
// 3. Set Ammonia POT: 70% (high - 0.07 ppm)

// EXPECTED RESULTS:
// ✓ Both RELAY_AERATOR and RELAY_PUMP: ON
// ✓ Both motors running simultaneously
// ✓ Red LED + Orange LED + Buzzer: All ON
// ✓ Virtual Terminal shows multiple alerts:
//    "⚠️  ALERT: Temperature TOO HIGH!"
//    "⚠️  ALERT: Dissolved Oxygen TOO LOW!"
//    "⚠️  ALERT: Ammonia Level CRITICAL!"
//    "✓ ACTION: Aerator ACTIVATED"
//    "✓ ACTION: Water Pump ACTIVATED"