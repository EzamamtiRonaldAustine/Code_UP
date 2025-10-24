/*
  ╔════════════════════════════════════════════════════════╗
  ║  SMART FISH POND MANAGEMENT SYSTEM                     ║
  ║  Arduino UNO Firmware - Proteus Simulation             ║
  ║  Author: Ezamamti Ronald A                             ║
  ║  Version: 3.0 (Arduino UNO)                            ║
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
#define TRIG_PIN        2   // Trigger pin
#define ECHO_PIN        3   // Echo pin

// LCD Display (4-bit mode)
#define LCD_RS          4
#define LCD_EN          5
#define LCD_D4          6
#define LCD_D5          7
#define LCD_D6          8
#define LCD_D7          9

// Actuators (Digital Outputs)
#define RELAY_AERATOR   10  // Relay controlling aerator motor
#define RELAY_PUMP      11  // Relay controlling water pump

// Indicators (Digital Outputs)
#define GREEN_LED       12  // Normal status indicator
#define ORANGE_LED      13  // Warning status indicator
#define RED_LED         A5  // Alert status indicator (use as digital)

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

// Virtual Serial alert timing
unsigned long lastSerialAlert = 0;
const unsigned long SERIAL_ALERT_INTERVAL = 300000; // 5 minutes

// Update intervals
unsigned long lastSensorRead = 0;
const unsigned long SENSOR_READ_INTERVAL = 2000; // 2 seconds

unsigned long lastDisplayUpdate = 0;
const unsigned long DISPLAY_UPDATE_INTERVAL = 1000; // 1 second

// ==================== SETUP ====================
void setup() {
  // Initialize Serial Communications
  Serial.begin(9600);   // Virtual Terminal (debugging)
  
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
  
  // Configure Pin Modes - Sensors
  pinMode(TRIG_PIN, OUTPUT);
  pinMode(ECHO_PIN, INPUT);
  
  // Set Initial States (All OFF)
  digitalWrite(RELAY_AERATOR, LOW);
  digitalWrite(RELAY_PUMP, LOW);
  digitalWrite(GREEN_LED, HIGH);  // Start with normal status
  digitalWrite(ORANGE_LED, LOW);
  digitalWrite(RED_LED, LOW);
  
  delay(2000);
  
  // Clear LCD and show ready message
  lcd.clear();
  lcd.setCursor(0, 0);
  lcd.print("SYSTEM  READY");
  delay(1500);
  lcd.clear();
  
  // Print startup message to Serial
  Serial.println("========================================");
  Serial.println(" SMART FISH POND MANAGEMENT SYSTEM");
  Serial.println(" Arduino UNO - System Ready");
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
    
    // Send virtual alert if needed (throttled)
    if (alertTriggered && (currentMillis - lastSerialAlert >= SERIAL_ALERT_INTERVAL)) {
      sendVirtualAlert();
      lastSerialAlert = currentMillis;
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
    digitalWrite(ORANGE_LED, LOW);
    
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
    digitalWrite(RELAY_AERATOR, LOW);
    digitalWrite(RELAY_PUMP, LOW);
    aeratorActive = false;
    pumpActive = false;
    
  } else {
    // ===== NORMAL STATE =====
    
    digitalWrite(RED_LED, LOW);
    digitalWrite(GREEN_LED, HIGH);
    digitalWrite(ORANGE_LED, LOW);
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

// ==================== VIRTUAL ALERT FUNCTIONS ====================

void sendVirtualAlert() {
  Serial.println("========================================");
  Serial.println("  VIRTUAL ALERT - SIMULATED SMS");
  Serial.println("========================================");
  
  Serial.println("FISH POND ALERT!");
  Serial.println();
  Serial.println("Critical conditions detected:");
  Serial.print("Temp: "); Serial.print(temperature, 1); Serial.println(" C");
  Serial.print("pH: "); Serial.println(pH_value, 1);
  Serial.print("DO: "); Serial.print(dissolvedOxygen, 1); Serial.println(" mg/L");
  Serial.print("NH3: "); Serial.print(ammonia, 2); Serial.println(" ppm");
  Serial.print("Water Level: "); Serial.print(waterLevel, 1); Serial.println(" cm");
  Serial.println();
  Serial.println("CHECK POND IMMEDIATELY!");
  Serial.println("*** Virtual Alert Sent Successfully ***");
  Serial.println();
}