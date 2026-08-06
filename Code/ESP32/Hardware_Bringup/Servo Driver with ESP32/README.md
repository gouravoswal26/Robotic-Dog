# ESP32 Bring-up & Firmware Validation

This milestone marks the successful bring-up of the ESP32-WROOM-32E controller used in the quadruped robot. Before integrating sensors and ST3215 serial bus servos, the development board was validated to ensure reliable firmware uploads and serial communication.

## Objectives

- Configure the Arduino IDE for the ESP32-WROOM-32E
- Verify firmware upload process
- Validate USB serial communication
- Confirm stable execution of user applications
- Prepare the controller for ST3215 servo integration

## Hardware

- ESP32-WROOM-32E Servo Driver Board
- USB-C Data Cable
- Development Laptop (Windows 11)

## Development Environment

- Arduino IDE 2.x
- ESP32 Arduino Core v3.3.11
- Board Profile: ESP32 Dev Module

## Test Program

The firmware initializes the serial interface and continuously outputs a heartbeat message to verify that the microcontroller is executing correctly.

### Expected Output

## Result

✔ Firmware uploaded successfully.

✔ Serial communication verified.

✔ ESP32 board validated and ready for ST3215 servo communication.

## Next Milestone

- ST3215 Serial Bus Servo Communication
- Servo ID Configuration
- Position Control
- Feedback Monitoring
