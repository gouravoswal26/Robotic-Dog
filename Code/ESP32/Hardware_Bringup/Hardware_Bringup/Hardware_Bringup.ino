/*
 * ------------------------------------------------------------
 * Project : Robotic Dog
 * File    : Hardware_Bringup.ino
 * Author  : Gourav Jain
 * Board   : ESP32
 * ------------------------------------------------------------
 * Purpose:
 * Verify initialization of all major hardware components
 * before developing locomotion and autonomous behaviors.
 *
 * Hardware Checked:
 * - I2C Bus
 * - MPU6500 IMU
 * - SSD1306 OLED
 * - PCA9685 Servo Driver
 *
 * Development Stage:
 * Hardware Bring-up
 * ------------------------------------------------------------
 */

#include <Wire.h>
#include <Adafruit_GFX.h>
#include <Adafruit_SSD1306.h>
#include <Adafruit_PWMServoDriver.h>

#define SDA_PIN 21
#define SCL_PIN 22

#define MPU6500_ADDR 0x68
#define OLED_ADDR    0x3C

#define SCREEN_WIDTH 128
#define SCREEN_HEIGHT 64
#define OLED_RESET -1

Adafruit_SSD1306 display(SCREEN_WIDTH, SCREEN_HEIGHT, &Wire, OLED_RESET);
Adafruit_PWMServoDriver pwm = Adafruit_PWMServoDriver(0x40);

bool checkI2CDevice(uint8_t address);

void setup()
{
    Serial.begin(115200);

    Wire.begin(SDA_PIN, SCL_PIN);

    Serial.println();
    Serial.println("========================================");
    Serial.println(" Robotic Dog Hardware Bring-up");
    Serial.println("========================================");

    // ---------- MPU6500 ----------
    if(checkI2CDevice(MPU6500_ADDR))
        Serial.println("[PASS] MPU6500 Detected");
    else
        Serial.println("[FAIL] MPU6500 Not Found");

    // ---------- OLED ----------
    if(display.begin(SSD1306_SWITCHCAPVCC, OLED_ADDR))
    {
        Serial.println("[PASS] OLED Detected");

        display.clearDisplay();
        display.setTextSize(1);
        display.setTextColor(SSD1306_WHITE);

        display.setCursor(0,0);
        display.println("Robotic Dog");

        display.setCursor(0,15);
        display.println("Hardware Bring-up");

        display.setCursor(0,35);
        display.println("System Ready");

        display.display();
    }
    else
    {
        Serial.println("[FAIL] OLED Not Found");
    }

    // ---------- PCA9685 ----------
    if(checkI2CDevice(0x40))
    {
        pwm.begin();
        pwm.setPWMFreq(50);

        Serial.println("[PASS] PCA9685 Detected");
    }
    else
    {
        Serial.println("[FAIL] PCA9685 Not Found");
    }

    Serial.println("----------------------------------------");
    Serial.println("Hardware Initialization Complete");
    Serial.println("----------------------------------------");
}

void loop()
{
    delay(1000);
}

bool checkI2CDevice(uint8_t address)
{
    Wire.beginTransmission(address);
    return (Wire.endTransmission() == 0);
}
