# Hardware Bring-up

This folder contains the master hardware initialization firmware for the robotic dog.

## Objective

- Initialize the I²C bus
- Verify communication with the MPU6500 IMU
- Verify OLED display initialization
- Verify PCA9685 servo driver detection
- Confirm that core hardware is operational before subsystem testing

## Files

- **Hardware_Bringup.ino** – Performs startup checks on major hardware components and reports the results via the Serial Monitor.

## Hardware

- ESP32
- MPU6500 IMU
- SSD1306 OLED Display
- PCA9685 Servo Driver

## Development Stage

Hardware Bring-up
