# PCA9685 Test

This folder contains firmware used to verify communication with the PCA9685 16-channel PWM servo driver and validate servo operation during the hardware bring-up phase.

## Objective

- Verify I²C communication with the PCA9685
- Initialize the servo driver
- Set the PWM frequency to 50 Hz
- Test each servo channel individually
- Center all connected servos

## Files

- **PCA9685_Test.ino** – Initializes the PCA9685, centers all servos, and sequentially tests the first 12 servo channels.

## Hardware

- ESP32
- PCA9685 16-Channel PWM Servo Driver
- Up to 12 Servo Motors

## Development Stage

Hardware Bring-up
