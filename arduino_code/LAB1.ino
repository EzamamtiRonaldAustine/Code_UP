void setup() {
  pinMode(6, OUTPUT); // LED pin set as output
}

void loop() {
  digitalWrite(3, HIGH); // turn LED on
  delay(1000);           // wait for 1 second
  digitalWrite(3, LOW);  // turn LED off
  delay(1000);           // wait for 1 second
}
