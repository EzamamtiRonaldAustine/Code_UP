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
float pH_value = 0.0;
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
  Serial.println("========================================");
  Serial.println(" SMART FISH POND MANAGEMENT SYSTEM");
  Serial.println(" Arduino MEGA2560 - System Ready");
  Serial.println("========================================");
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
  pH_value = (phRaw * 14.0) / 1023.0;
  
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
    Serial.println("ALERT: Temperature TOO HIGH!");
  } else if (temperature < TEMP_MIN) {
    alertTriggered = true;
    Serial.println("ALERT: Temperature TOO LOW!");
  }
  
  // pH Check
  if (pH_value < PH_MIN) {
    alertTriggered = true;
    Serial.println("ALERT: pH TOO LOW (Acidic)!");
  } else if (pH_value > PH_MAX) {
    alertTriggered = true;
    Serial.println("ALERT: pH TOO HIGH (Alkaline)!");
  }
  
  // Turbidity Check
  if (turbidity > TURB_MAX) {
    alertTriggered = true;
    Serial.println("ALERT: High Turbidity Detected!");
  }
  
  // Ammonia Check
  if (ammonia > NH3_MAX) {
    alertTriggered = true;
    Serial.println("ALERT: Ammonia Level CRITICAL!");
  }
  
  // Dissolved Oxygen Check
  if (dissolvedOxygen < DO_MIN) {
    alertTriggered = true;
    Serial.println("ALERT: Dissolved Oxygen TOO LOW!");
  }
  
  // Water Level Check
  if (waterLevel < WATER_LEVEL_MIN) {
    alertTriggered = true;
    Serial.println("ALERT: Water Level CRITICALLY LOW!");
  }
  
  // ===== WARNING CONDITIONS (Approaching thresholds) =====
  
  if (!alertTriggered) {
    if (temperature > TEMP_WARNING && temperature <= TEMP_MAX) {
      warningTriggered = true;
    }
    if (pH_value < PH_WARNING_LOW && pH_value >= PH_MIN) {
      warningTriggered = true;
    }
    if (pH_value > PH_WARNING_HIGH && pH_value <= PH_MAX) {
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
      if (!aeratorActive) {
        digitalWrite(RELAY_AERATOR, HIGH);
        aeratorActive = true;
        Serial.println("ACTION: Aerator ACTIVATED (Low DO)");
      }
    } else {
      if (aeratorActive) {
        digitalWrite(RELAY_AERATOR, LOW);
        aeratorActive = false;
      }
    }
    
    // Activate pump if temp high, ammonia high, or turbidity high
    if (temperature > TEMP_MAX || ammonia > NH3_MAX || turbidity > TURB_MAX) {
      if (!pumpActive) {
        digitalWrite(RELAY_PUMP, HIGH);
        pumpActive = true;
        Serial.println("ACTION: Water Pump ACTIVATED");
      }
    } else {
      if (pumpActive) {
        digitalWrite(RELAY_PUMP, LOW);
        pumpActive = false;
      }
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
  lcd.print(pH_value, 1);
  
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
  Serial.println("========================================");
  Serial.println("    WATER QUALITY DATA SNAPSHOT");
  Serial.println("========================================");
  Serial.print("Temperature:      ");
  Serial.print(temperature, 2);
  Serial.println(" C");
  
  Serial.print("pH Level:         ");
  Serial.println(pH_value, 2);
  
  Serial.print("Turbidity:        ");
  Serial.print(turbidity, 2);
  Serial.println(" NTU");
  
  Serial.print("Ammonia (NH3):    ");
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
    Serial.println("ALERT");
  } else if (warningTriggered) {
    Serial.println("WARNING");
  } else {
    Serial.println("NORMAL");
  }
  
  Serial.print("Aerator:          ");
  Serial.println(aeratorActive ? "ON" : "OFF");
  
  Serial.print("Water Pump:       ");
  Serial.println(pumpActive ? "ON" : "OFF");
  
  Serial.println("========================================");
  Serial.println();
}

// ==================== GSM FUNCTIONS ====================

void initGSM() {
  Serial.println("Initializing SIM900D GSM Module...");
  
  Serial1.println("AT");
  delay(1000);
  
  Serial1.println("AT+CMGF=1"); // Set SMS text mode
  delay(1000);
  
  Serial.println("GSM Module Initialized");
}

void sendGSMAlert() {
  Serial.println("========================================");
  Serial.println("  SENDING GSM ALERT SMS...");
  Serial.println("========================================");
  
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
  Serial1.print(pH_value, 1);
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
  
  Serial.println("GSM Alert SMS Sent Successfully");
  Serial.println();
}
// ```

// **Key Change:** Renamed `pH` variable to `pH_value` to avoid conflicts with some compilers.

// ---

// ### **STEP 3: Compile the Code**
// ```
// 1. Copy the complete code above into Arduino IDE
// 2. Click "Verify" (✓ checkmark button)
// 3. Wait for compilation to complete
// 4. Check for "Done compiling" message at bottom
// 5. Note: Should show 0 errors, 0 warnings
// ```

// ---

// ### **STEP 4: Export HEX File**
// ```
// 1. After successful compilation
// 2. Sketch → Export Compiled Binary
// 3. A message will appear: "Done compiling and creating .hex"
// 4. Navigate to your sketch folder (usually in Documents/Arduino/)
// 5. You'll find TWO .hex files:
//    - YourSketchName.ino.standard.hex (use this one)
//    - YourSketchName.ino.with_bootloader.standard.hex
// 6. Copy the first .hex file to a known location
// ```

// ---

// ### **STEP 5: Update Proteus Connections for MEGA2560**

// Since you switched to Arduino MEGA2560, **update your connections**:

// #### **🔄 REVISED CONNECTION CHANGES:**

// | **Component** | **Old ESP32 Pin** | **New MEGA2560 Pin** |
// |---------------|-------------------|----------------------|
// | LM35 (Temp) | GPIO36 (VP) | **A0** |
// | pH Meter | GPIO39 (VN) | **A1** |
// | Turbidity POT | GPIO34 | **A2** |
// | Ammonia POT | GPIO35 | **A3** |
// | DO POT | GPIO32 | **A4** |
// | Ultrasonic TRIG | GPIO5 | **Digital Pin 22** |
// | Ultrasonic ECHO | GPIO18 | **Digital Pin 23** |
// | LCD RS | GPIO13 | **Digital Pin 24** |
// | LCD EN | GPIO12 | **Digital Pin 25** |
// | LCD D4 | GPIO14 | **Digital Pin 26** |
// | LCD D5 | GPIO27 | **Digital Pin 27** |
// | LCD D6 | GPIO26 | **Digital Pin 28** |
// | LCD D7 | GPIO25 | **Digital Pin 29** |
// | Relay Aerator | GPIO23 | **Digital Pin 30** |
// | Relay Pump | GPIO19 | **Digital Pin 31** |
// | Green LED | GPIO2 | **Digital Pin 32** |
// | Orange LED | GPIO15 | **Digital Pin 33** |
// | Red LED | GPIO33 | **Digital Pin 34** |
// | Buzzer | GPIO21 | **Digital Pin 35** |
// | GSM TX | GPIO17 (TX2) | **TX1 (Pin 18)** |
// | GSM RX | GPIO16 (RX2) | **RX1 (Pin 19)** |
// | Virtual Terminal TX | GPIO1 (TX0) | **TX0 (Pin 1)** |
// | Virtual Terminal RX | GPIO3 (RX0) | **RX0 (Pin 0)** |

// #### **Power Connections:**
// ```
// Arduino MEGA2560:
//   VIN pin → 5V Rail (from LM1117T-5.0)
//   GND pin → Common Ground
//   5V pin → Leave unconnected (internal regulator output)
// ```

// ---

// ### **STEP 6: Load HEX into Proteus MEGA2560**
// ```
// 1. In Proteus, double-click the ARDUINO MEGA2560 component
// 2. In the Edit Component window:
//    - Program File: Click folder icon → Browse to your .hex file
//    - Clock Frequency: 16MHz (default for MEGA2560)
// 3. Click OK
// 4. The component should now show a small "P" icon indicating program loaded
// ```

// ---

// ### **STEP 7: Configure Virtual Terminal**
// ```
// 1. Double-click COMPIM (Virtual Terminal)
// 2. Ensure these settings:
//    - Physical Port: (None)
//    - Baud Rate: 9600
//    - Data Bits: 8
//    - Parity: None
//    - Stop Bits: 1
//    - Flow Control: None
// 3. Click OK
// ```

// ---

// ### **STEP 8: Run Simulation**
// ```
// 1. Click the PLAY button ▶️ (bottom left of Proteus)
// 2. Simulation should start without errors
// 3. Watch for:
//    ✓ LCD displays "FISH POND" then "INITIALIZING..."
//    ✓ After 2 seconds: "SYSTEM READY"
//    ✓ Green LED turns ON
//    ✓ Virtual Terminal shows startup banner
// ```

// ---

// ## **🔍 IF ERRORS STILL OCCUR:**

// ### **Error: "Program property is not defined"**

// **Cause:** HEX file not loaded or wrong file selected

// **Fix:**
// ```
// 1. Verify .hex file exists in sketch folder
// 2. Double-click Arduino MEGA2560 in Proteus
// 3. Click Program File → Browse again
// 4. Select the .standard.hex file (NOT .with_bootloader)
// 5. Click OK
// 6. Try simulation again
// ```

// ### **Error: "AVR: Cannot open program file"**

// **Cause:** File path contains special characters or spaces

// **Fix:**
// ```
// 1. Move .hex file to simple path: C:\Proteus\fishpond.hex
// 2. In Proteus, load from this simple path
// 3. Avoid paths with spaces or special characters
// ```

// ### **Error: "Simulation failed to start"**

// **Cause:** Component mismatch or power issues

// **Fix:**
// ```
// 1. Check Arduino MEGA2560 is powered:
//    - VIN → 5V Rail
//    - GND → Common Ground
// 2. Verify all regulators (LM1117) have correct pin connections
// 3. Check no floating wires
// 4. Ensure common GND for all components
// ```

// ---

// ## **✅ VERIFICATION CHECKLIST**

// Before running simulation, verify:
// ```
// ARDUINO IDE
// □ Board: Arduino Mega or Mega 2560 selected
// □ Processor: ATmega2560 selected
// □ Code compiled successfully (0 errors)
// □ .hex file exported to known location

// PROTEUS - ARDUINO COMPONENT
// □ Arduino MEGA2560 (not UNO, not ESP32)
// □ Program File loaded (.standard.hex)
// □ VIN connected to 5V rail
// □ GND connected to common ground

// PROTEUS - CONNECTIONS
// □ All analog sensors → A0-A4
// □ Ultrasonic → Pins 22, 23
// □ LCD → Pins 24-29
// □ Relays → Pins 30, 31
// □ LEDs → Pins 32-34
// □ Buzzer → Pin 35
// □ GSM → TX1/RX1 (Pins 18/19)
// □ Virtual Terminal → TX0/RX0 (Pins 0/1)

// PROTEUS - POWER
// □ DC source 9V configured
// □ LiPo Battery 7.4V configured
// □ LM1117T-5.0 connected correctly
// □ LM1117T-3.3 connected correctly
// □ Capacitors in place
// □ All grounds common

// PROTEUS - SENSORS
// □ LM35 configured (25°C)
// □ pH Meter configured (7.0)
// □ Ultrasonic configured (50cm)
// □ POTs configured (50% DO, 30% Turb, 20% NH3)
// □ LCD contrast POT (25%)
// ```

// ---

// ## **🚀 EXPECTED RESULTS AFTER FIX**

// Once you load the .hex file correctly:
// ```
// ✓ Simulation starts without errors
// ✓ LCD shows initialization sequence
// ✓ Green LED turns ON
// ✓ Virtual Terminal displays:
//   "========================================"
//   " SMART FISH POND MANAGEMENT SYSTEM"
//   " Arduino MEGA2560 - System Ready"
//   "========================================"
// ✓ After 2 seconds, water quality data appears
// ✓ System is ready for testing