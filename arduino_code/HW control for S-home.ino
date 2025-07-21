// Updated Combined Smart Home System with ToneAC Optimized Buzzer & Continuous Doorbell

#include <SPI.h>
#include <MFRC522.h>
#include <DHT.h>
#include <IRremote.hpp>
#include <toneAC.h>

// ---------- Pin Definitions ----------
#define RST_PIN         5
#define SS_PIN          4
#define RELAY_PIN       8
#define TRIG_PIN        7
#define ECHO_PIN        6
#define DHT_PIN         2
#define FAN_PIN         A0
#define RED_PIN         A1
#define GREEN_PIN       A2
#define BLUE_PIN        A3
#define IR_PIN          A4
#define BUTTON_PIN      A5
// ToneAC uses fixed pins 9 & 10

// ---------- RFID Setup ----------
MFRC522 rfid(SS_PIN, RST_PIN);
byte authorized1[] = {0x93, 0x18, 0xE1, 0x0F};
byte authorized2[] = {0x33, 0xBD, 0x19, 0x0E};
bool doorUnlocked = false;
unsigned long unlockTime = 0;
const int unlockDuration = 5000;

// ---------- DHT Setup ----------
#define DHTTYPE DHT11
DHT dht(DHT_PIN, DHTTYPE);
bool fanAuto = true;
int fanSpeed = 255;
float tempThreshold = 30.0;
unsigned long lastFanCheck = 0;
unsigned long lastDataSend = 0;
const unsigned long fanCheckInterval = 3000;
const unsigned long sendInterval = 5000;

// ---------- RGB & IR ----------
bool whiteMode = false;

// ---------- Frequencies ----------
const int INTRUDER_FREQ = 2000;
const int DOORBELL_FREQ = 1500;
const int BUZZER_ON_FREQ = 2500;

// ---------- Buzzer State ----------
bool doorbellActive = false;
unsigned long intruderToneEnd = 0;

void setup() {
  Serial.begin(9600);
  SPI.begin();
  rfid.PCD_Init();
  dht.begin();

  pinMode(RELAY_PIN, OUTPUT); digitalWrite(RELAY_PIN, LOW);
  pinMode(TRIG_PIN, OUTPUT); pinMode(ECHO_PIN, INPUT);
  pinMode(FAN_PIN, OUTPUT);
  pinMode(RED_PIN, OUTPUT);
  pinMode(GREEN_PIN, OUTPUT);
  pinMode(BLUE_PIN, OUTPUT);
  pinMode(BUTTON_PIN, INPUT_PULLUP);

  IrReceiver.begin(IR_PIN, ENABLE_LED_FEEDBACK);
  analogWrite(FAN_PIN, 0);
  setColor(LOW, LOW, LOW);

  Serial.println("System Initialized");
}

void loop() {
  handleSerialCommands();
  autoRelock();
  checkRFID();
  checkUltrasonic();
  checkDHTFan();
  handleIRRemote();
  checkButton();
  manageBuzzer();
  sendSensorData();
}

void handleSerialCommands() {
  if (Serial.available()) {
    String cmd = Serial.readStringUntil('\n');
    cmd.trim();

    if (cmd == "LOCK_DOOR") {
      digitalWrite(RELAY_PIN, LOW);
      doorUnlocked = false;
      Serial.println("ACK:LOCK_DOOR");
    } else if (cmd == "UNLOCK_DOOR") {
      digitalWrite(RELAY_PIN, HIGH);
      doorUnlocked = true;
      unlockTime = millis();
      Serial.println("ACK:UNLOCK_DOOR");
    } else if (cmd == "FAN_ON") {
      fanAuto = false;
      analogWrite(FAN_PIN, fanSpeed);
      Serial.println("ACK:FAN_ON");
    } else if (cmd == "FAN_OFF") {
      fanAuto = false;
      analogWrite(FAN_PIN, 0);
      Serial.println("ACK:FAN_OFF");
    } else if (cmd == "FAN_AUTO") {
      fanAuto = true;
      Serial.println("ACK:FAN_AUTO");
    } else if (cmd.startsWith("FAN_SPEED_")) {
      int value = cmd.substring(10).toInt();
      fanSpeed = constrain(value, 0, 255);
      if (!fanAuto) analogWrite(FAN_PIN, fanSpeed);
      Serial.print("ACK:FAN_SPEED_");
      Serial.println(fanSpeed);
    } else if (cmd == "BUZZER_ON") {
      toneAC(BUZZER_ON_FREQ);
      Serial.println("ACK:BUZZER_ON");
    } else if (cmd == "BUZZER_OFF") {
      noToneAC();
      Serial.println("ACK:BUZZER_OFF");
    } else if (cmd == "RGB_RED") {
      setColor(HIGH, LOW, LOW);
      Serial.println("ACK:RGB_RED");
    } else if (cmd == "RGB_GREEN") {
      setColor(LOW, HIGH, LOW);
      Serial.println("ACK:RGB_GREEN");
    } else if (cmd == "RGB_BLUE") {
      setColor(LOW, LOW, HIGH);
      Serial.println("ACK:RGB_BLUE");
    } else if (cmd == "RGB_WHITE") {
      setColor(HIGH, HIGH, HIGH);
      Serial.println("ACK:RGB_WHITE");
    } else if (cmd == "RGB_OFF") {
      setColor(LOW, LOW, LOW);
      Serial.println("ACK:RGB_OFF");
    }
  }
}

void sendSensorData() {
  if (millis() - lastDataSend < sendInterval) return;
  lastDataSend = millis();

  float temp = dht.readTemperature();
  float hum = dht.readHumidity();
  int dist = readDistance();

  if (!isnan(temp) && !isnan(hum)) {
    Serial.print("DATA:TEMP:"); Serial.print(temp);
    Serial.print(";HUM:"); Serial.print(hum);
    Serial.print(";DIST:"); Serial.print(dist);
    Serial.print(";FAN:"); Serial.print(fanSpeed);
    Serial.println(";");
  }
}

int readDistance() {
  digitalWrite(TRIG_PIN, LOW); delayMicroseconds(2);
  digitalWrite(TRIG_PIN, HIGH); delayMicroseconds(10);
  digitalWrite(TRIG_PIN, LOW);
  long duration = pulseIn(ECHO_PIN, HIGH);
  return duration * 0.034 / 2;
}

void checkRFID() {
  if (!rfid.PICC_IsNewCardPresent() || !rfid.PICC_ReadCardSerial()) return;
  if (isAuthorized(rfid.uid.uidByte)) unlockDoor();
  rfid.PICC_HaltA();
  rfid.PCD_StopCrypto1();
}

bool isAuthorized(byte *uid) {
  bool match1 = true, match2 = true;
  for (byte i = 0; i < 4; i++) {
    if (uid[i] != authorized1[i]) match1 = false;
    if (uid[i] != authorized2[i]) match2 = false;
  }
  return match1 || match2;
}

void unlockDoor() {
  digitalWrite(RELAY_PIN, HIGH);
  doorUnlocked = true;
  unlockTime = millis();
  Serial.println("DOOR:UNLOCKED");
}

void autoRelock() {
  if (doorUnlocked && millis() - unlockTime >= unlockDuration) {
    digitalWrite(RELAY_PIN, LOW);
    doorUnlocked = false;
    Serial.println("DOOR:LOCKED");
  }
}

void checkUltrasonic() {
  if (doorUnlocked) return;
  int distance = readDistance();
  if (distance > 0 && distance < 20 && millis() > intruderToneEnd) {
    Serial.println("Intruder detected!");
    toneAC(INTRUDER_FREQ);
    intruderToneEnd = millis() + 1500;
  }
}

void manageBuzzer() {
  if (millis() > intruderToneEnd && !doorbellActive) noToneAC();
}

void checkDHTFan() {
  if (millis() - lastFanCheck < fanCheckInterval) return;
  lastFanCheck = millis();
  float temp = dht.readTemperature();
  if (isnan(temp)) return;
  if (fanAuto) analogWrite(FAN_PIN, temp >= tempThreshold ? fanSpeed : 0);
}

void handleIRRemote() {
  if (IrReceiver.decode()) {
    uint32_t code = IrReceiver.decodedIRData.decodedRawData;
    switch (code) {
      case 0xBA45FF00: fanAuto = !fanAuto; break;
      case 0xB946FF00: fanSpeed = min(255, fanSpeed + 50); break;
      case 0xEA15FF00: fanSpeed = max(0, fanSpeed - 50); break;
      case 0xF30CFF00: analogWrite(FAN_PIN, fanSpeed); break;
      case 0xE718FF00: analogWrite(FAN_PIN, 0); break;
      case 0xF708FF00: setColor(HIGH, LOW, LOW); break;
      case 0xE31CFF00: setColor(LOW, HIGH, LOW); break;
      case 0xA55AFF00: setColor(LOW, LOW, HIGH); break;
      case 0xA15EFF00: whiteMode = !whiteMode; setColor(whiteMode, whiteMode, whiteMode); break;
    }
    IrReceiver.resume();
  }
}

void setColor(bool red, bool green, bool blue) {
  digitalWrite(RED_PIN, red);
  digitalWrite(GREEN_PIN, green);
  digitalWrite(BLUE_PIN, blue);
}

void checkButton() {
  if (digitalRead(BUTTON_PIN) == LOW) {
    if (!doorbellActive) {
      Serial.println("DOORBELL:PRESSED");
      toneAC(DOORBELL_FREQ);
      doorbellActive = true;
    }
  } else if (doorbellActive) {
    noToneAC();
    doorbellActive = false;
  }
}
