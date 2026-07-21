/*
 * ------------------------------------------------------------
 * Project : Robotic Dog
 * File    : Power_System.ino
 * Author  : Gourav Jain
 * Board   : ESP32
 * ------------------------------------------------------------
 * Purpose:
 * Monitor battery voltage and current consumption of the
 * robotic dog during hardware bring-up.
 *
 * Hardware:
 * - ESP32
 * - Voltage Sensor Module
 * - ACS758 Current Sensor
 * - 3S LiPo Battery
 *
 * Development Stage:
 * Hardware Bring-up
 * ------------------------------------------------------------
 */

#define VOLTAGE_PIN 34
#define CURRENT_PIN 35

const float ADC_REFERENCE = 3.3;
const int ADC_RESOLUTION = 4095;

// Voltage divider ratio (Update according to your module)
const float VOLTAGE_DIVIDER_RATIO = 5.0;

// ACS758 Parameters (Adjust if using another version)
const float CURRENT_SENSOR_OFFSET = 2.5;
const float CURRENT_SENSOR_SENSITIVITY = 0.040;   // 40mV/A

void setup()
{
    Serial.begin(115200);

    pinMode(VOLTAGE_PIN, INPUT);
    pinMode(CURRENT_PIN, INPUT);

    Serial.println("----------------------------------------");
    Serial.println(" Robotic Dog - Power System Test");
    Serial.println("----------------------------------------");
}

void loop()
{
    float batteryVoltage = readBatteryVoltage();
    float batteryCurrent = readCurrent();
    float batteryPower = batteryVoltage * batteryCurrent;

    Serial.println("----------------------------------------");

    Serial.print("Battery Voltage : ");
    Serial.print(batteryVoltage, 2);
    Serial.println(" V");

    Serial.print("Battery Current : ");
    Serial.print(batteryCurrent, 2);
    Serial.println(" A");

    Serial.print("Power Usage     : ");
    Serial.print(batteryPower, 2);
    Serial.println(" W");

    if (batteryVoltage < 10.5)
    {
        Serial.println("WARNING : Battery Voltage Low!");
    }
    else
    {
        Serial.println("Battery Status : OK");
    }

    Serial.println("----------------------------------------");

    delay(1000);
}

float readBatteryVoltage()
{
    int adc = analogRead(VOLTAGE_PIN);

    float voltage = ((float)adc / ADC_RESOLUTION) * ADC_REFERENCE;

    return voltage * VOLTAGE_DIVIDER_RATIO;
}

float readCurrent()
{
    int adc = analogRead(CURRENT_PIN);

    float sensorVoltage = ((float)adc / ADC_RESOLUTION) * ADC_REFERENCE;

    float current = (sensorVoltage - CURRENT_SENSOR_OFFSET) / CURRENT_SENSOR_SENSITIVITY;

    return current;
}
