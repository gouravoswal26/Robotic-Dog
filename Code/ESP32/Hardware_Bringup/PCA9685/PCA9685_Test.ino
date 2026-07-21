/*
 * ------------------------------------------------------------
 * Project : Robotic Dog
 * File    : PCA9685_Test.ino
 * Author  : Gourav Jain
 * Board   : ESP32
 * Driver  : PCA9685 16-Channel PWM Servo Driver
 * ------------------------------------------------------------
 * Purpose:
 * Verify communication with the PCA9685 and test all
 * connected servo channels.
 *
 * Development Stage:
 * Hardware Bring-up
 * ------------------------------------------------------------
 */

#include <Wire.h>
#include <Adafruit_PWMServoDriver.h>

#define SDA_PIN 21
#define SCL_PIN 22

// Servo pulse lengths
#define SERVO_MIN 110
#define SERVO_CENTER 307
#define SERVO_MAX 510

Adafruit_PWMServoDriver pwm = Adafruit_PWMServoDriver(0x40);

void setup()
{
    Serial.begin(115200);

    Wire.begin(SDA_PIN, SCL_PIN);

    Serial.println("--------------------------------------");
    Serial.println(" Robotic Dog - PCA9685 Hardware Test");
    Serial.println("--------------------------------------");

    pwm.begin();
    pwm.setPWMFreq(50);

    delay(500);

    Serial.println("PCA9685 Initialized Successfully");

    centerAllServos();

    Serial.println("All Servos Centered");
}

void loop()
{
    Serial.println("Testing Servo Channels...");

    for (uint8_t channel = 0; channel < 12; channel++)
    {
        Serial.print("Servo ");
        Serial.print(channel);
        Serial.println(" -> MIN");

        pwm.setPWM(channel, 0, SERVO_MIN);
        delay(400);

        Serial.print("Servo ");
        Serial.print(channel);
        Serial.println(" -> CENTER");

        pwm.setPWM(channel, 0, SERVO_CENTER);
        delay(400);

        Serial.print("Servo ");
        Serial.print(channel);
        Serial.println(" -> MAX");

        pwm.setPWM(channel, 0, SERVO_MAX);
        delay(400);

        pwm.setPWM(channel, 0, SERVO_CENTER);
        delay(300);
    }

    Serial.println("--------------------------------------");
    Serial.println("All Servo Channels Tested");
    Serial.println("--------------------------------------");

    delay(2000);
}

void centerAllServos()
{
    for (uint8_t i = 0; i < 12; i++)
    {
        pwm.setPWM(i, 0, SERVO_CENTER);
    }
}
