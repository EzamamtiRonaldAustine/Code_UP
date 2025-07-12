#include <SPI.h>
#include <MFRC522.h>

#define SS_PIN 10
#define RST_PIN 9
#define RELAY_PIN 8
#define TRIG_PIN 7
#define ECHO_PIN 6
#define BUZZER_PIN 5

MFRC522 rfid(SS_PIN, RST_PIN);
byte allowedUID[4] = {0xDE, 0xAD, 0xBE, 0xEF}; // Replace with your card UID

bool doorUnlocked = false;
unsigned long unlockTime = 0;
const int unlockDuration = 5000; // milliseconds

void setup() {
  Serial.begin(9600);
  SPI.begin();
  rfid.PCD_Init();
  pinMode(RELAY_PIN, OUTPUT);
  pinMode(TRIG_PIN, OUTPUT);
  pinMode(ECHO_PIN, INPUT);
  pinMode(BUZZER_PIN, OUTPUT);
  digitalWrite(RELAY_PIN, LOW); // Initially locked
  Serial.println("System Ready.");
}

void loop() {
  checkRFID();
  checkUltrasonic();
  autoRelock();
}

void checkRFID() {
  if (!rfid.PICC_IsNewCardPresent() || !rfid.PICC_ReadCardSerial()) return;

  Serial.print("UID Tag: ");
  for (byte i = 0; i < rfid.uid.size; i++) {
    Serial.print(rfid.uid.uidByte[i], HEX);
    Serial.print(" ");
  }
  Serial.println();

  if (checkUID(rfid.uid.uidByte)) {
    unlockDoor();
  } else {
    Serial.println("Access Denied!");
  }

  rfid.PICC_HaltA();
}

bool checkUID(byte *uid) {
  for (int i = 0; i < 4; i++) {
    if (uid[i] != allowedUID[i]) return false;
  }
  return true;
}

void unlockDoor() {
  Serial.println("Access Granted! Unlocking door...");
  digitalWrite(RELAY_PIN, HIGH);
  doorUnlocked = true;
  unlockTime = millis();
}

void autoRelock() {
  if (doorUnlocked && millis() - unlockTime >= unlockDuration) {
    digitalWrite(RELAY_PIN, LOW);
    doorUnlocked = false;
    Serial.println("Door auto-locked.");
  }
}

void checkUltrasonic() {
  long duration;
  float distance;

  digitalWrite(TRIG_PIN, LOW);
  delayMicroseconds(2);
  digitalWrite(TRIG_PIN, HIGH);
  delayMicroseconds(10);
  digitalWrite(TRIG_PIN, LOW);

  duration = pulseIn(ECHO_PIN, HIGH);
  distance = duration * 0.034 / 2; // cm

  Serial.print("Distance: ");
  Serial.println(distance);

  if (distance < 35 && !doorUnlocked) {
    Serial.println("Intruder detected by ultrasonic! Triggering alarm.");
    tone(BUZZER_PIN, 3500); // play 3kHz tone
    delay(3000);            // for 3 seconds
    noTone(BUZZER_PIN);     // stop the tone
  }
}
