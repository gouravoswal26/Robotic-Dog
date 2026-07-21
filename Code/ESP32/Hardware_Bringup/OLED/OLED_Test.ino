/*
 * ------------------------------------------------------------
 * Project : Robotic Dog
 * File    : OLED_Test.ino
 * Author  : Gourav Jain
 * Board   : ESP32
 * Display : SSD1306 OLED (128x64)
 * ------------------------------------------------------------
 * Purpose:
 * Verify OLED display initialization and display
 * important system information during hardware bring-up.
 *
 * Development Stage:
 * Hardware Bring-up
 * ------------------------------------------------------------
 */

#include <Wire.h>
#include <Adafruit_GFX.h>
#include <Adafruit_SSD1306.h>

#define SCREEN_WIDTH 128
#define SCREEN_HEIGHT 64

#define OLED_RESET -1
#define OLED_ADDRESS 0x3C

#define SDA_PIN 21
#define SCL_PIN 22

Adafruit_SSD1306 display(SCREEN_WIDTH, SCREEN_HEIGHT, &Wire, OLED_RESET);

void setup()
{
    Serial.begin(115200);

    Wire.begin(SDA_PIN, SCL_PIN);

    if (!display.begin(SSD1306_SWITCHCAPVCC, OLED_ADDRESS))
    {
        Serial.println("OLED Initialization Failed!");

        while (true);
    }

    Serial.println("OLED Initialized Successfully");

    display.clearDisplay();

    display.setTextSize(2);
    display.setTextColor(SSD1306_WHITE);
    display.setCursor(10,5);
    display.println("Robotic");

    display.setCursor(28,28);
    display.println("Dog");

    display.display();

    delay(2000);
}

void loop()
{
    display.clearDisplay();

    display.setTextSize(1);
    display.setCursor(0,0);
    display.println("Hardware Bring-up");

    display.drawLine(0,10,128,10,SSD1306_WHITE);

    display.setCursor(0,18);
    display.print("ESP32 : OK");

    display.setCursor(0,30);
    display.print("OLED  : OK");

    display.setCursor(0,42);
    display.print("Status: Running");

    display.setCursor(0,54);
    display.print("Ready");

    display.display();

    delay(1000);
}
