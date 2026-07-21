# Servo Test

This folder contains firmware used to verify the operation of all servo motors connected to the PCA9685 servo driver.

## Objective

- Verify servo wiring
- Verify PWM output from the PCA9685
- Test each servo individually
- Confirm neutral (center) position
- Detect reversed or faulty servos before gait development

## Files

- **Servo_Test.ino** – Sequentially moves each servo through minimum, center, and maximum positions before returning it to the neutral position.

## Hardware

- ESP32
- PCA9685 16-Channel Servo Driver
- 12 Servo Motors

## Development Stage

Hardware Bring-up
