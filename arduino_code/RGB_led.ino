#include <IRremote.hpp>

#define IR_RECEIVE_PIN 2       // IR sensor pin
#define RED_PIN 3              // RGB LED Red
#define GREEN_PIN 5            // RGB LED Green
#define BLUE_PIN 6             // RGB LED Blue
#define BUZZER_PIN 7           // Buzzer
#define DOORBELL_BUTTON_PIN 8  // Doorbell push button

bool whiteMode = false;

void setup() {
  Serial.begin(9600);

  // Initialize IR receiver
  IrReceiver.begin(IR_RECEIVE_PIN, ENABLE_LED_FEEDBACK);

  pinMode(RED_PIN, OUTPUT);
  pinMode(GREEN_PIN, OUTPUT);
  pinMode(BLUE_PIN, OUTPUT);
  pinMode(BUZZER_PIN, OUTPUT);
  pinMode(DOORBELL_BUTTON_PIN, INPUT_PULLUP);

  setColor(LOW, LOW, LOW);  // Turn off LED
  Serial.println("System Ready: IR + Doorbell");
}

void loop() {
  handleIRRemote();
  handleDoorbell();
}

void handleIRRemote() {
  if (IrReceiver.decode()) {
    uint32_t code = IrReceiver.decodedIRData.decodedRawData;
    Serial.print("IR Code: 0x");
    Serial.println(code, HEX);

    switch (code) {
      case 0xF708FF00: // Button 4 - Red
        setColor(HIGH, LOW, LOW);
        whiteMode = false;
        Serial.println("Red ON");
        break;

      case 0xE31CFF00: // Button 5 - Green
        setColor(LOW, HIGH, LOW);
        whiteMode = false;
        Serial.println("Green ON");
        break;

      case 0xA55AFF00: // Button 6 - Blue
        setColor(LOW, LOW, HIGH);
        whiteMode = false;
        Serial.println("Blue ON");
        break;

      case 0xA15EFF00: // Button 3 - Toggle White
        whiteMode = !whiteMode;
        if (whiteMode) {
          setColor(HIGH, HIGH, HIGH);
          Serial.println("White ON");
        } else {
          setColor(LOW, LOW, LOW);
          Serial.println("White OFF");
        }
        break;

      default:
        Serial.println("Unknown button");
        break;
    }

    IrReceiver.resume(); // Ready for next signal
  }
}

void setColor(bool red, bool green, bool blue) {
  digitalWrite(RED_PIN, red);
  digitalWrite(GREEN_PIN, green);
  digitalWrite(BLUE_PIN, blue);
}

void handleDoorbell() {
  if (digitalRead(DOORBELL_BUTTON_PIN) == LOW) {
    Serial.println("Button Pressed - Buzzing");
    tone(BUZZER_PIN, 1500);
    delay(1000);
    noTone(BUZZER_PIN);
  }
}
