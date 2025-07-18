#include <SPI.h>
#include <MFRC522.h>

#define SS_PIN 10
#define RST_PIN 9

MFRC522 rfid(SS_PIN, RST_PIN);

void setup() {
  Serial.begin(9600);
  while (!Serial); // Wait for Serial to initialize (for Leonardo or similar)
  
  SPI.begin();      // Init SPI bus
  rfid.PCD_Init();  // Init MFRC522
  
  byte firmware = rfid.PCD_ReadRegister(MFRC522::VersionReg);
  Serial.print("Firmware Version: 0x");
  Serial.println(firmware, HEX);
  
  if (firmware == 0x00 || firmware == 0xFF) {
    Serial.println("ERROR: RFID reader not detected. Check wiring and power (3.3V only).");
    while (true); // Stop execution
  }

  Serial.println("Scan a card to get UID...");
}

void loop() {
  // Wait for a new card
  if (!rfid.PICC_IsNewCardPresent()) return;
  if (!rfid.PICC_ReadCardSerial()) return;

  // Print UID
  Serial.print("Card UID: ");
  for (byte i = 0; i < rfid.uid.size; i++) {
    if (rfid.uid.uidByte[i] < 0x10) Serial.print("0"); // Leading zero
    Serial.print(rfid.uid.uidByte[i], HEX);
    Serial.print(i < rfid.uid.size - 1 ? " " : "");
  }
  Serial.println();

  // Halt PICC and stop encryption
  rfid.PICC_HaltA();
  rfid.PCD_StopCrypto1();
}
