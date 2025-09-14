// Pin assignments
const int led3 = 3;  // Always blinking LED
const int led6 = 6;  // LED controlled by switch
const int sw   = 7;  // Switch pin

// Timing variables for LED3 blinking
unsigned long previousMillis3 = 0;
const long interval3 = 1000; // 1 second blink
bool led3State = LOW;

// Timing variables for LED6 (switch-controlled blink)
unsigned long previousMillis6 = 0;
const long interval6 = 300; // 300 ms blink
bool led6State = LOW;

void setup() {
  pinMode(led3, OUTPUT);
  pinMode(led6, OUTPUT);
  pinMode(sw, INPUT);
}

void loop() {
  unsigned long currentMillis = millis();

  // --- LED3: Blinks constantly ---
  if (currentMillis - previousMillis3 >= interval3) {
    previousMillis3 = currentMillis;
    led3State = !led3State; // toggle state
    digitalWrite(led3, led3State);
  }

  // --- LED6: Blinks only when switch is pressed ---
  if (digitalRead(sw) == HIGH) {
    if (currentMillis - previousMillis6 >= interval6) {
      previousMillis6 = currentMillis;
      led6State = !led6State; // toggle state
      digitalWrite(led6, led6State);
    }
  } else {
    // If switch is off, keep LED6 off
    led6State = LOW;
    digitalWrite(led6, led6State);
  }
}
