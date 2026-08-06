/*
------------------------------------------------------
 Project : Robo Monkey - ESP32 Bring-up Test
 Author  : Gourav Jain

 Description:
 Verifies successful firmware upload and serial
 communication before integrating ST3215 serial bus
 servos.
------------------------------------------------------
*/

void setup() {
  Serial.begin(115200);
  delay(2000);

  Serial.println();
  Serial.println("=====================================");
  Serial.println(" ESP32 Board Initialization Success ");
  Serial.println("=====================================");
}

void loop() {
  Serial.println("Board Running...");
  delay(1000);
}
