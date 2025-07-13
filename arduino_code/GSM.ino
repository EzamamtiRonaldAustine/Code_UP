#include <SoftwareSerial.h>

SoftwareSerial gsm(2, 3); // RX, TX

void setup() {
  Serial.begin(9600);
  gsm.begin(9600);
  
  Serial.println("Initializing SIM900A...");
  delay(2000);

  sendATCommand("AT");
  sendATCommand("AT+CMGF=1"); // SMS text mode
  sendATCommand("AT+CSCS=\"GSM\""); // Use GSM charset

  Serial.println("Sending SMS...");
  gsm.println("AT+CMGS=\"+256763583059\"");  // Replace with your real number
  delay(1000);
  gsm.print("Test SMS from SIM900A");
  delay(500);
  gsm.write(26);  // CTRL+Z to send
  delay(5000);    // Wait for confirmation
}

void loop() {
  while (gsm.available()) {
    Serial.write(gsm.read());
  }
}

void sendATCommand(String command) {
  gsm.println(command);
  delay(1000);
  while (gsm.available()) {
    Serial.write(gsm.read());
  }
}
