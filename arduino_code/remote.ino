#include <DHT.h>
#include <IRremote.hpp>

#define DHTPIN 2
#define DHTTYPE DHT11
#define FAN_PIN 4
#define IR_PIN 3

DHT dht(DHTPIN, DHTTYPE);

bool fanAuto = true;
int fanSpeed = 255;
float tempThreshold = 24.0;

void setup() {
  Serial.begin(9600);
  dht.begin();
  delay(100);
  IrReceiver.begin(IR_PIN, ENABLE_LED_FEEDBACK);
  pinMode(FAN_PIN, OUTPUT);
  analogWrite(FAN_PIN, 0);
  Serial.println("Temperature & IR Fan Control Ready.");
}

void loop() {
  handleIR();

  float temp = dht.readTemperature();
  if (isnan(temp)) {
    Serial.println("Failed to read DHT!");
  } else {
    Serial.print("Temp: ");
    Serial.println(temp);

    if (fanAuto) {
      if (temp >= tempThreshold) {
        analogWrite(FAN_PIN, fanSpeed);
        Serial.println("Fan ON (Auto)");
      } else {
        analogWrite(FAN_PIN, 0);
        Serial.println("Fan OFF (Auto)");
      }
    }
  }

  delay(2000);
}

void handleIR() {
  if (IrReceiver.decode()) {
    uint32_t code = IrReceiver.decodedIRData.decodedRawData;
    Serial.print("IR Code: 0x");
    Serial.println(code, HEX);

  switch (code) {
    case 0xBA45FF00:  // Power (Auto/Manual toggle)
      fanAuto = !fanAuto;
      Serial.println(fanAuto ? "Auto Mode Enabled" : "Auto Mode Disabled");
      break;
  
    case 0xB946FF00:  // VOL+
      fanSpeed = min(255, fanSpeed + 50);
      Serial.print("Fan Speed Increased: ");
      Serial.println(fanSpeed);
      break;
  
    case 0xEA15FF00:  // VOL-
      fanSpeed = max(0, fanSpeed - 50);
      Serial.print("Fan Speed Decreased: ");
      Serial.println(fanSpeed);
      break;
  
    case 0xE916FF00:  // "0" button – Restart Arduino
      Serial.println("Restarting Arduino...");
      delay(100);
      asm volatile ("  jmp 0");
      break;
  
    case 0xE718FF00:  // "2" – Fan OFF (Manual)
      analogWrite(FAN_PIN, 0);
      Serial.println("Fan OFF (Manual)");
      break;
  
    case 0xF30CFF00:  // "1" – Fan ON (Manual)
      analogWrite(FAN_PIN, fanSpeed);
      Serial.println("Fan ON (Manual)");
      break;
  
    default:
      Serial.println("Unknown Command");
      break;
  }


    IrReceiver.resume();
  }
}
