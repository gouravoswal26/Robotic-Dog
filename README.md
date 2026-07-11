# 🐕 Robotic Dog (Quadruped Robot)
# 🐕 Robotic Dog (Quadruped Robot)

> **Project Status:** 🚧 Under Active Development
>
> This project is currently being developed and tested on an ESP32 platform. Once the software and hardware are fully validated, it will be migrated to an STM32 platform.

---

## 📸 Robot Prototype

<p align="center">
  <img src="Images/front.jpeg" width="700">
</p>

<p align="center">
  <img src="Images/side.jpeg" width="340">
  <img src="Images/back.jpeg" width="340">
</p>
A 12-DOF Quadruped Robot designed for stable walking, balancing, and autonomous navigation using multiple sensors. This project combines embedded systems, robotics, inverse kinematics, and sensor fusion to create a versatile robotic platform.

---

## 📖 Overview

This project aims to develop a four-legged robotic dog capable of:

- Stable walking
- Self-balancing
- Obstacle detection
- Terrain adaptation
- Autonomous movement

The robot uses multiple sensors along with inverse kinematics to generate smooth leg motion while maintaining stability on uneven surfaces.

---

## ✨ Features

- 🦿 12 Degrees of Freedom (3 DOF per leg)
- 🤖 Quadruped Walking Gait
- ⚖️ Real-Time Self Balancing
- 📡 Obstacle Detection
- 📏 Ground Distance Measurement
- 🔄 Sensor Fusion
- 🎯 Inverse Kinematics
- 🔋 Battery Monitoring
- 📈 Current & Voltage Monitoring
- 🚧 Modular Software Architecture

---
## 📋 Specifications

| Feature | Specification |
|----------|--------------|
| Robot Type | Quadruped Robot |
| DOF | 12 |
| Controller | ESP32 (Current) |
| Future Controller | STM32 |
| Servo Driver | PCA9685 |
| Actuators | 12 Servo Motors |
| IMU | MPU6500 ×2 |
| ToF Sensor | VL53L0X ×2 |
| Ultrasonic | HC-SR04 ×2 |
| Foot Sensors | FSR ×4 |
| Battery | 3S LiPo |
---
# Hardware

## Controller

- ESP32

## Servo Driver

- PCA9685 (16-Channel PWM)

## Actuators

- 12 × MG996R Servo Motors

## Sensors

- 2 × MPU6500 IMU
- 2 × VL53L0X Time-of-Flight Sensors
- 2 × HC-SR04 Ultrasonic Sensors
- 4 × Force Sensitive Resistors (FSR)
- 3 × ACS758 Current Sensors
- Voltage Sensor Module

## Power

- 3S LiPo Battery (5300mAh)
- Multiple Buck Converters

---

# Software Stack

- Arduino IDE
- ESP32 Framework
- C++
- I2C Communication
- PWM Servo Control
- Inverse Kinematics
- Sensor Fusion Algorithms

---

# Repository Structure

```
Robotic-Dog/
│
├── Code/
│   ├── Walking/
│   ├── Balancing/
│   ├── Sensors/
│   ├── Servo_Control/
│   └── Utilities/
│
├── CAD/
│
├── Electronics/
│
├── Images/
│
├── Videos/
│
├── Documentation/
│
└── README.md
```

---

# Working Principle

1. Read sensor data from both IMUs.
2. Measure ground distance using ToF sensors.
3. Detect nearby obstacles using ultrasonic sensors.
4. Monitor foot contact using FSR sensors.
5. Calculate body orientation.
6. Apply inverse kinematics.
7. Generate servo angles.
8. Drive all 12 servos through the PCA9685.
9. Continuously adjust posture to maintain stability.

---

# Libraries Used

- Wire
- Adafruit PWM Servo Driver
- Adafruit MPU6050 / MPU6500
- VL53L0X
- ESP32 Core

---

# Future Improvements

- SLAM Navigation
- ROS2 Integration
- Computer Vision
- Object Detection
- Path Planning
- Wireless Teleoperation
- AI-Based Locomotion
- Terrain Classification

---

# Current Status

- ✅ Servo Control
- ✅ Dual IMU Integration
- ✅ I2C Communication
- ✅ Sensor Testing
- ✅ Balancing Algorithm (In Progress)
- 🚧 Walking Optimization
- 🚧 Autonomous Navigation

---

# Contributing

Contributions, ideas, and improvements are always welcome.

Feel free to fork the repository and submit a pull request.

---

# License

This project is licensed under the MIT License.

---

# Author
Gourav Jain
Electronics & Communication Engineering
Passionate about Robotics, Embedded Systems, AI, and Autonomous Robots.

---

## ⭐ Support

If you found this project helpful, please consider giving it a ⭐ on GitHub!
