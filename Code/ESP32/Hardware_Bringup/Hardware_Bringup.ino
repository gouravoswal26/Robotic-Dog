#include <Wire.h>

// ESP32 I2C Pins
#define SDA_PIN 21
#define SCL_PIN 22

void setup() {
  Serial.begin(115200);
  Wire.begin(SDA_PIN, SCL_PIN);

  Serial.println("\nESP32 I2C Scanner");
}

void loop() {
  byte error, address;
  int deviceCount = 0;

  Serial.println("Scanning...");

  for (address = 1; address < 127; address++) {
    Wire.beginTransmission(address);
    error = Wire.endTransmission();

    if (error == 0) {
      Serial.print("Device found at 0x");
      if (address < 16)
        Serial.print("0");
      Serial.println(address, HEX);
      deviceCount++;
    }
  }

  if (deviceCount == 0) {
    Serial.println("No I2C devices found.");
  } else {
    Serial.print("Total devices found: ");
    Serial.println(deviceCount);
  }

  Serial.println("-------------------------");
  delay(3000);
