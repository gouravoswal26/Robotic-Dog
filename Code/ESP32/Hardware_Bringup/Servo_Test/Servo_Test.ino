/*
 * ------------------------------------------------------------
 * Project : Robotic Dog
 * File    : Servo_Test.ino
 * Author  : Gourav Jain
 * Board   : ESP32
 * Driver  : PCA9685
 * ------------------------------------------------------------
 * Purpose:
 * Test all 12 servo motors individually to verify
 * wiring, direction, and neutral position.
 *
 * Development Stage:
 * Hardware Bring-up
 * ------------------------------------------------------------
 */

#include <Wire.h>
#include <Adafruit_PWMServoDriver.h>

#define SDA_PIN 21
#define SCL_PIN 22

#define SERVO_MIN     110
#define SERVO_CENTER  307
#define SERVO_MAX     510

#define TOTAL_SERVOS 12

Adafruit_PWMServoDriver pwm = Adafruit_PWMServoDriver(0x40);

void moveServo(uint8_t channel, uint16_t pulse);
void centerAllServos();

void setup()
{
    Serial.begin(115200);

    Wire.begin(SDA_PIN, SCL_PIN);

    pwm.begin();
    pwm.setPWMFreq(50);

    delay(500);

    Serial.println("========================================");
    Serial.println(" Robotic Dog - Servo Test");
    Serial.println("========================================");

    centerAllServos();

    Serial.println("All servos moved to neutral position.");
    delay(2000);
}

void loop()
{
    for(uint8_t servo = 0; servo < TOTAL_SERVOS; servo++)
    {
        Serial.print("Testing Servo ");
        Serial.println(servo);

        moveServo(servo, SERVO_MIN);
        delay(500);

        moveServo(servo, SERVO_CENTER);
        delay(500);

        moveServo(servo, SERVO_MAX);
        delay(500);

        moveServo(servo, SERVO_CENTER);
        delay(700);

        Serial.print("Servo ");
        Serial.print(servo);
        Serial.println(" OK");

        Serial.println("----------------------------------------");
    }

    Serial.println("Servo test completed.");
    Serial.println("Repeating in 3 seconds...\n");

    delay(3000);
}

void moveServo(uint8_t channel, uint16_t pulse)
{
    pwm.setPWM(channel, 0, pulse);
}

void centerAllServos()
{
    for(uint8_t i = 0; i < TOTAL_SERVOS; i++)
    {
        pwm.setPWM(i, 0, SERVO_CENTER);
    }
}
