/*
 * ------------------------------------------------------------
 * Project : Robotic Dog
 * File    : Ultrasonic_Test.ino
 * Author  : Gourav Jain
 * Board   : ESP32
 * Sensor  : HC-SR04 Ultrasonic Sensor (x2)
 * ------------------------------------------------------------
 * Purpose:
 * Verify distance measurements from two ultrasonic sensors.
 *
 * Development Stage:
 * Hardware Bring-up
 * ------------------------------------------------------------
 */

#define TRIG_FRONT 18
#define ECHO_FRONT 19

#define TRIG_REAR  23
#define ECHO_REAR   5

float measureDistance(uint8_t trigPin, uint8_t echoPin);

void setup()
{
    Serial.begin(115200);

    pinMode(TRIG_FRONT, OUTPUT);
    pinMode(ECHO_FRONT, INPUT);

    pinMode(TRIG_REAR, OUTPUT);
    pinMode(ECHO_REAR, INPUT);

    Serial.println("--------------------------------------");
    Serial.println(" Robotic Dog - Ultrasonic Test");
    Serial.println("--------------------------------------");
}

void loop()
{
    float frontDistance = measureDistance(TRIG_FRONT, ECHO_FRONT);
    float rearDistance  = measureDistance(TRIG_REAR, ECHO_REAR);

    Serial.print("Front Sensor : ");
    Serial.print(frontDistance);
    Serial.println(" cm");

    Serial.print("Rear Sensor  : ");
    Serial.print(rearDistance);
    Serial.println(" cm");

    if(frontDistance < 20)
        Serial.println("Obstacle detected at Front");

    if(rearDistance < 20)
        Serial.println("Obstacle detected at Rear");

    Serial.println("--------------------------------------");

    delay(500);
}

float measureDistance(uint8_t trigPin, uint8_t echoPin)
{
    digitalWrite(trigPin, LOW);
    delayMicroseconds(2);

    digitalWrite(trigPin, HIGH);
    delayMicroseconds(10);

    digitalWrite(trigPin, LOW);

    long duration = pulseIn(echoPin, HIGH, 30000);

    if(duration == 0)
        return -1;

    return duration * 0.0343 / 2.0;
}
