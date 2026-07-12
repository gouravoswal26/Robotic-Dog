# 🔌 Circuit Diagrams

This folder contains the electrical schematics, wiring diagrams, and hardware connection layouts for the Robotic Dog project.

## Contents

- **Diagram.png** – Complete wiring diagram of the robotic dog electronics.

## Electronics Overview

The robot integrates multiple sensors, actuators, and power management modules to achieve stable locomotion and autonomous operation.

### Main Components

- ESP32 Development Board *(Current Controller)*
- STM32 *(Planned Future Controller)*
- PCA9685 16-Channel Servo Driver
- 12 × Servo Motors
- 2 × MPU6500 IMU Sensors
- 2 × VL53L0X Time-of-Flight Sensors
- 2 × HC-SR04 Ultrasonic Sensors
- 4 × Force Sensitive Resistors (FSR)
- 3 × ACS758 Current Sensors
- Voltage Sensor Module
- 3S LiPo Battery
- Buck Converters

## Purpose

The circuit diagrams are provided to help users understand:

- Electrical connections
- Power distribution
- Sensor interfaces
- I²C communication
- PWM servo control
- Battery and power management

## Communication Interfaces

| Interface | Connected Devices |
|-----------|-------------------|
| I²C | PCA9685, MPU6500, VL53L0X |
| PWM | Servo Motors |
| Digital GPIO | HC-SR04, FSR Sensors |
| Analog | Current & Voltage Sensors |

## Future Updates

The circuit design will continue to evolve as the project progresses, including:

- Migration from ESP32 to STM32
- Improved PCB design
- Better power distribution
- Modular sensor connectors
- Cable management improvements
- Dedicated battery management system (BMS)

---

> **Note:** The current circuit diagram represents the development prototype and may be updated as new hardware is integrated.
