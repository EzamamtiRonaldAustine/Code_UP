#include <DHT.h>

#define DHTPIN 2          // Pin where the DHT11 is connected
#define DHTTYPE DHT11     // Define the type of sensor

DHT dht(DHTPIN, DHTTYPE); // Create a DHT object

void setup() {
  Serial.begin(9600);
  dht.begin(); // Initialize the DHT sensor
}

void loop() {
  delay(2000); // Wait a few seconds between measurements

  // Read humidity and temperature
  float humidity = dht.readHumidity();
  float temperature = dht.readTemperature();

  // Check if any reads failed and exit early (to try again).
  if (isnan(humidity) || isnan(temperature)) {
    Serial.println("Failed to read from DHT sensor!");
    return;
  }

  // Print the results to the Serial Monitor
  Serial.print("Humidity (%): ");
  Serial.println(humidity, 2);
  Serial.print("Temperature (C): ");
  Serial.println(temperature, 2);
}
