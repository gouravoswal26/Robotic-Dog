/*
 * ------------------------------------------------------------
 * Project : Robotic Dog
 * File    : MPU6500_Test.ino
 * Author  : Gourav Jain
 * Board   : ESP32
 * Sensor  : MPU6500
 * ------------------------------------------------------------
 * Purpose:
 * Reads raw Accelerometer, Gyroscope, and Temperature
 * data from the MPU6500 using I2C communication.
 *
 * Development Stage:
 * Hardware Bring-up
 * ------------------------------------------------------------
 */

#include <Wire.h>

#define MPU6500_ADDRESS 0x68

// ESP32 I2C Pins
#define SDA_PIN 21
#define SCL_PIN 22

int16_t AccX, AccY, AccZ;
int16_t GyroX, GyroY, GyroZ;
int16_t Temperature;

void setup()
{
    Serial.begin(115200);

    Wire.begin(SDA_PIN, SCL_PIN);

    Serial.println("--------------------------------------");
    Serial.println(" Robotic Dog - MPU6500 Hardware Test");
    Serial.println("--------------------------------------");

    initializeMPU6500();
}

void loop()
{
    readMPU6500();

    Serial.println("============== MPU6500 ==============");

    Serial.print("Accel X : ");
    Serial.println(AccX);

    Serial.print("Accel Y : ");
    Serial.println(AccY);

    Serial.print("Accel Z : ");
    Serial.println(AccZ);

    Serial.println();

    Serial.print("Gyro X  : ");
    Serial.println(GyroX);

    Serial.print("Gyro Y  : ");
    Serial.println(GyroY);

    Serial.print("Gyro Z  : ");
    Serial.println(GyroZ);

    Serial.println();

    float tempC = (Temperature / 333.87) + 21.0;

    Serial.print("Temperature : ");
    Serial.print(tempC);
    Serial.println(" °C");

    Serial.println("--------------------------------------");

    delay(500);
}

void initializeMPU6500()
{
    Wire.beginTransmission(MPU6500_ADDRESS);
    Wire.write(0x6B);       // Power Management Register
    Wire.write(0x00);       // Wake up MPU6500
    Wire.endTransmission();

    Serial.println("MPU6500 Initialized Successfully");
}

void readMPU6500()
{
    Wire.beginTransmission(MPU6500_ADDRESS);
    Wire.write(0x3B);       // Starting register
    Wire.endTransmission(false);

    Wire.requestFrom(MPU6500_ADDRESS, 14);

    AccX = (Wire.read() << 8) | Wire.read();
    AccY = (Wire.read() << 8) | Wire.read();
    AccZ = (Wire.read() << 8) | Wire.read();

    Temperature = (Wire.read() << 8) | Wire.read();

    GyroX = (Wire.read() << 8) | Wire.read();
    GyroY = (Wire.read() << 8) | Wire.read();
    GyroZ = (Wire.read() << 8) | Wire.read();
}
