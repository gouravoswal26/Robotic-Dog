/*
 * ------------------------------------------------------------
 * Project : Robotic Dog
 * File    : FSR_Test.ino
 * Author  : Gourav Jain
 * Board   : ESP32
 * Purpose : Test Force Sensitive Resistor (FSR) Sensors
 * ------------------------------------------------------------
 * This program reads the analog values from four FSR sensors
 * placed on the robot's feet and displays their readings on
 * the Serial Monitor.
 *
 * Development Stage:
 * Hardware Bring-up
 * ------------------------------------------------------------
 */

#define FSR_FRONT_LEFT   34
#define FSR_FRONT_RIGHT  35
#define FSR_REAR_LEFT    32
#define FSR_REAR_RIGHT   33

const int CONTACT_THRESHOLD = 500;

void setup()
{
    Serial.begin(115200);

    pinMode(FSR_FRONT_LEFT, INPUT);
    pinMode(FSR_FRONT_RIGHT, INPUT);
    pinMode(FSR_REAR_LEFT, INPUT);
    pinMode(FSR_REAR_RIGHT, INPUT);

    Serial.println("------------------------------------");
    Serial.println(" Robotic Dog - FSR Sensor Test");
    Serial.println("------------------------------------");
}

void loop()
{
    int frontLeft  = analogRead(FSR_FRONT_LEFT);
    int frontRight = analogRead(FSR_FRONT_RIGHT);
    int rearLeft   = analogRead(FSR_REAR_LEFT);
    int rearRight  = analogRead(FSR_REAR_RIGHT);

    Serial.println("----------- FSR Readings -----------");

    Serial.print("Front Left  : ");
    Serial.print(frontLeft);
    Serial.print("\t");
    Serial.println(frontLeft > CONTACT_THRESHOLD ? "Contact" : "No Contact");

    Serial.print("Front Right : ");
    Serial.print(frontRight);
    Serial.print("\t");
    Serial.println(frontRight > CONTACT_THRESHOLD ? "Contact" : "No Contact");

    Serial.print("Rear Left   : ");
    Serial.print(rearLeft);
    Serial.print("\t");
    Serial.println(rearLeft > CONTACT_THRESHOLD ? "Contact" : "No Contact");

    Serial.print("Rear Right  : ");
    Serial.print(rearRight);
    Serial.print("\t");
    Serial.println(rearRight > CONTACT_THRESHOLD ? "Contact" : "No Contact");

    Serial.println();

    delay(500);
}
