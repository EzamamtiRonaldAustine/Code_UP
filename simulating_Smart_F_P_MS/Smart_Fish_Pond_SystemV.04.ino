/*
  SMART FISH POND MANAGEMENT SYSTEM
  SIMULINO NANO - Proteus Simulation
  Author: Ezamamti Ronald A
  Version: 5.2 (CLEAN DISPLAY)
*/

#include <LiquidCrystal.h>

// ==================== PIN DEFINITIONS ====================
// Analog Sensors
#define TEMP_PIN        A0
#define PH_PIN          A1
#define TURB_PIN        A2
#define AMMONIA_PIN     A3
#define DO_PIN          A4

// Ultrasonic
#define TRIG_PIN        2
#define ECHO_PIN        3

// LCD
#define LCD_RS          4
#define LCD_EN          5
#define LCD_D4          6
#define LCD_D5          7
#define LCD_D6          8
#define LCD_D7          9

// Actuators
#define RELAY_AERATOR   10
#define RELAY_PUMP      11

// Indicators
#define GREEN_LED       12
#define ORANGE_LED      13
#define RED_LED         A5

// ==================== THRESHOLDS ====================
#define TEMP_MAX        32.0
#define TEMP_MIN        20.0
#define TEMP_WARNING    30.0

#define PH_MIN          6.5
#define PH_MAX          8.5
#define PH_WARNING_LOW  6.8
#define PH_WARNING_HIGH 8.2

#define TURB_MAX        50.0
#define TURB_WARNING    40.0

#define NH3_MAX         0.05
#define NH3_WARNING     0.03

#define DO_MIN          5.0
#define DO_WARNING      6.0

#define WATER_LEVEL_MIN 20.0

// ==================== GLOBAL VARIABLES ====================
LiquidCrystal lcd(LCD_RS, LCD_EN, LCD_D4, LCD_D5, LCD_D6, LCD_D7);

float temperature = 25.0;
float pH_value = 7.0;
float turbidity = 30.0;
float ammonia = 0.02;
float dissolvedOxygen = 7.0;
float waterLevel = 65.0;

bool alertTriggered = false;
bool warningTriggered = false;
bool aeratorActive = false;
bool pumpActive = false;

unsigned long lastSensorRead = 0;
const unsigned long SENSOR_READ_INTERVAL = 2000;

unsigned long lastDisplayUpdate = 0;
const unsigned long DISPLAY_UPDATE_INTERVAL = 1000;

unsigned long lastSerialLog = 0;
const unsigned long SERIAL_LOG_INTERVAL = 3000;

int displayMode = 0;
unsigned long lastDisplayChange = 0;

// ==================== SETUP ====================
void setup() {
  Serial.begin(9600);
  
  // Initialize pins
  pinMode(RELAY_AERATOR, OUTPUT);
  pinMode(RELAY_PUMP, OUTPUT);
  pinMode(GREEN_LED, OUTPUT);
  pinMode(ORANGE_LED, OUTPUT);
  pinMode(RED_LED, OUTPUT);
  pinMode(TRIG_PIN, OUTPUT);
  pinMode(ECHO_PIN, INPUT);
  
  // Initialize outputs - ALL OFF
  digitalWrite(RELAY_AERATOR, LOW);
  digitalWrite(RELAY_PUMP, LOW);
  digitalWrite(GREEN_LED, LOW);
  digitalWrite(ORANGE_LED, LOW);
  digitalWrite(RED_LED, LOW);
  
  // Initialize LCD
  lcd.begin(16, 2);
  lcd.clear();
  lcd.print("SMART FISH POND");
  lcd.setCursor(0, 1);
  lcd.print("SIMULINO NANO");
  
  // Wait for Serial to initialize in Proteus
  delay(2000);
  
  // System ready indication
  digitalWrite(GREEN_LED, HIGH);
  
  lcd.clear();
  lcd.print("SYSTEM READY");
  lcd.setCursor(0, 1);
  lcd.print("TERMINAL ACTIVE");
  
  Serial.println("========================================");
  Serial.println("   SMART FISH POND - SIMULINO NANO");
  Serial.println("   Virtual Terminal: ACTIVE");
  Serial.println("   System: OPERATIONAL");
  Serial.println("========================================");
  Serial.println();
  
  delay(1500);
  lcd.clear();
  
  lastSensorRead = millis();
  lastDisplayUpdate = millis();
  lastSerialLog = millis();
  lastDisplayChange = millis();
}

// ==================== MAIN LOOP ====================
void loop() {
  unsigned long currentMillis = millis();
  
  // Read sensors and process data
  if (currentMillis - lastSensorRead >= SENSOR_READ_INTERVAL) {
    readAllSensors();
    checkWaterQuality();
    controlActuators();
    lastSensorRead = currentMillis;
  }
  
  // Update LCD display
  if (currentMillis - lastDisplayUpdate >= DISPLAY_UPDATE_INTERVAL) {
    updateLCDDisplay();
    lastDisplayUpdate = currentMillis;
  }
  
  // Log data to Serial (less frequent to reduce clutter)
  if (currentMillis - lastSerialLog >= SERIAL_LOG_INTERVAL) {
    logDataToSerial();
    lastSerialLog = currentMillis;
  }
}

// ==================== SENSOR READING ====================
void readAllSensors() {
  // Read analog sensors with realistic simulation ranges
  int tempRaw = analogRead(TEMP_PIN);
  temperature = 18.0 + (tempRaw / 1023.0) * 22.0;  // 18-40°C
  
  int phRaw = analogRead(PH_PIN);
  pH_value = 5.5 + (phRaw / 1023.0) * 4.5;        // 5.5-10.0
  
  int turbRaw = analogRead(TURB_PIN);
  turbidity = (turbRaw / 1023.0) * 100.0;         // 0-100 NTU
  
  int ammoniaRaw = analogRead(AMMONIA_PIN);
  ammonia = (ammoniaRaw / 1023.0) * 0.15;         // 0-0.15 ppm
  
  int doRaw = analogRead(DO_PIN);
  dissolvedOxygen = 3.0 + (doRaw / 1023.0) * 12.0; // 3-15 mg/L
  
  waterLevel = getWaterLevel();
}

float getWaterLevel() {
  // Simulate ultrasonic water level sensor
  digitalWrite(TRIG_PIN, LOW);
  delayMicroseconds(2);
  digitalWrite(TRIG_PIN, HIGH);
  delayMicroseconds(10);
  digitalWrite(TRIG_PIN, LOW);
  
  long duration = pulseIn(ECHO_PIN, HIGH, 30000);
  
  if (duration == 0) {
    // No echo - return simulated level based on potentiometer
    return 20.0 + (analogRead(A4) / 1023.0) * 80.0;
  }
  
  float distance = (duration * 0.0343) / 2.0;
  float level = 100.0 - distance;
  
  // Constrain to realistic values
  if (level < 0) level = 0;
  if (level > 100) level = 100;
  
  return level;
}

// ==================== WATER QUALITY CHECK ====================
void checkWaterQuality() {
  alertTriggered = false;
  warningTriggered = false;
  
  // Check for CRITICAL alerts
  if (temperature > TEMP_MAX || temperature < TEMP_MIN) {
    alertTriggered = true;
  }
  else if (pH_value < PH_MIN || pH_value > PH_MAX) {
    alertTriggered = true;
  }
  else if (turbidity > TURB_MAX) {
    alertTriggered = true;
  }
  else if (ammonia > NH3_MAX) {
    alertTriggered = true;
  }
  else if (dissolvedOxygen < DO_MIN) {
    alertTriggered = true;
  }
  else if (waterLevel < WATER_LEVEL_MIN) {
    alertTriggered = true;
  }
  
  // Check for WARNINGS (only if no critical alert)
  if (!alertTriggered) {
    if (temperature > TEMP_WARNING) warningTriggered = true;
    if (pH_value < PH_WARNING_LOW || pH_value > PH_WARNING_HIGH) warningTriggered = true;
    if (turbidity > TURB_WARNING) warningTriggered = true;
    if (ammonia > NH3_WARNING) warningTriggered = true;
    if (dissolvedOxygen < DO_WARNING) warningTriggered = true;
  }
}

// ==================== ACTUATOR CONTROL ====================
void controlActuators() {
  if (alertTriggered) {
    // ALERT MODE - Red LED, activate necessary equipment
    digitalWrite(RED_LED, HIGH);
    digitalWrite(GREEN_LED, LOW);
    digitalWrite(ORANGE_LED, LOW);
    
    // Aerator control - activate if oxygen low
    if (dissolvedOxygen < DO_MIN) {
      digitalWrite(RELAY_AERATOR, HIGH);
      aeratorActive = true;
    } else {
      digitalWrite(RELAY_AERATOR, LOW);
      aeratorActive = false;
    }
    
    // Water pump control - activate for water quality issues
    if (temperature > TEMP_MAX || ammonia > NH3_MAX || turbidity > TURB_MAX) {
      digitalWrite(RELAY_PUMP, HIGH);
      pumpActive = true;
    } else {
      digitalWrite(RELAY_PUMP, LOW);
      pumpActive = false;
    }
    
  } else if (warningTriggered) {
    // WARNING MODE - Orange LED, monitor closely
    digitalWrite(RED_LED, LOW);
    digitalWrite(GREEN_LED, LOW);
    digitalWrite(ORANGE_LED, HIGH);
    digitalWrite(RELAY_AERATOR, LOW);
    digitalWrite(RELAY_PUMP, LOW);
    aeratorActive = false;
    pumpActive = false;
    
  } else {
    // NORMAL MODE - Green LED, all systems normal
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
  // Handle display mode switching for normal operation
  if (!alertTriggered && !warningTriggered) {
    if (millis() - lastDisplayChange >= 4000) { // Change every 4 seconds
      displayMode = (displayMode + 1) % 2;
      lastDisplayChange = millis();
    }
  }
  
  lcd.clear();
  
  if (alertTriggered) {
    // ALERT SCREEN - Clean text only
    lcd.setCursor(0, 0);
    lcd.print("ALERT! CHECK SYS");
    lcd.setCursor(0, 1);
    lcd.print("T:");
    lcd.print(temperature, 1);
    lcd.print("C DO:");
    lcd.print(dissolvedOxygen, 1);
    
  } else if (warningTriggered) {
    // WARNING SCREEN - Clean text only
    lcd.setCursor(0, 0);
    lcd.print("WARNING MONITOR");
    lcd.setCursor(0, 1);
    lcd.print("pH:");
    lcd.print(pH_value, 1);
    lcd.print(" NH3:");
    lcd.print(ammonia, 3);
    
  } else {
    // NORMAL SCREENS - Alternate between two displays
    if (displayMode == 0) {
      lcd.setCursor(0, 0);
      lcd.print("T:");
      lcd.print(temperature, 1);
      lcd.print("C pH:");
      lcd.print(pH_value, 1);
      lcd.setCursor(0, 1);
      lcd.print("DO:");
      lcd.print(dissolvedOxygen, 1);
      lcd.print(" L:");
      lcd.print(waterLevel, 0);
      lcd.print("%");
    } else {
      lcd.setCursor(0, 0);
      lcd.print("TURB:");
      lcd.print(turbidity, 1);
      lcd.print(" NTU");
      lcd.setCursor(0, 1);
      lcd.print("NH3:");
      lcd.print(ammonia, 3);
      lcd.print(" ppm");
    }
  }
}

// ==================== SERIAL LOGGING ====================
void logDataToSerial() {
  Serial.println("============ POND DATA ============");
  Serial.print("Temperature:    "); Serial.print(temperature, 1); Serial.println(" C");
  Serial.print("pH Level:       "); Serial.println(pH_value, 1);
  Serial.print("Turbidity:      "); Serial.print(turbidity, 1); Serial.println(" NTU");
  Serial.print("Ammonia:        "); Serial.print(ammonia, 3); Serial.println(" ppm");
  Serial.print("Dissolved O2:   "); Serial.print(dissolvedOxygen, 1); Serial.println(" mg/L");
  Serial.print("Water Level:    "); Serial.print(waterLevel, 1); Serial.println(" %");
  Serial.print("System Status:  ");
  
  if (alertTriggered) {
    Serial.println("ALERT");
    Serial.print("Aerator:        "); Serial.println(aeratorActive ? "ON" : "OFF");
    Serial.print("Water Pump:     "); Serial.println(pumpActive ? "ON" : "OFF");
  } else if (warningTriggered) {
    Serial.println("WARNING");
  } else {
    Serial.println("NORMAL");
  }
  Serial.println("===================================");
  Serial.println();
}