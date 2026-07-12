# 💻 Source Code

This folder contains the source code for the **Robotic Dog (Quadruped Robot)**. The software is responsible for controlling the robot's locomotion, sensor integration, balancing, and future autonomous navigation.

## Current Platform

- **Microcontroller:** ESP32
- **Development Environment:** Arduino IDE
- **Programming Language:** C++

> **Note:** The current implementation is based on the ESP32 for rapid prototyping and testing. Once the software is fully validated, the project will be migrated to an **STM32** platform for improved real-time performance and advanced control capabilities.

## Folder Structure

```
Code/
├── ESP32/
│   └── RoboticDog.ino
│
└── README.md
```

## Current Features

- Servo motor control
- Basic robot initialization
- I²C communication
- Sensor testing
- Hardware integration
- PWM control using PCA9685

## Planned Features

- Walking gait generation
- Inverse kinematics
- Self-balancing
- Sensor fusion
- Obstacle detection
- Terrain adaptation
- Power monitoring
- Autonomous navigation
- Wireless control
- ROS2 integration

## Libraries Used

- Wire
- Adafruit PWM Servo Driver
- Adafruit MPU6050 / MPU6500
- VL53L0X
- ESP32 Arduino Core

## Development Roadmap

### Phase 1 – Hardware Bring-up
- ✅ ESP32 setup
- ✅ Servo driver integration
- ✅ Basic servo testing
- ✅ Sensor communication

### Phase 2 – Motion Control
- 🚧 Servo calibration
- 🚧 Standing posture
- 🚧 Walking gait
- 🚧 Motion optimization

### Phase 3 – Stability
- ⏳ IMU-based balancing
- ⏳ Sensor fusion
- ⏳ Foot contact detection

### Phase 4 – Intelligence
- ⏳ STM32 migration
- ⏳ Computer vision
- ⏳ LiDAR integration
- ⏳ Autonomous navigation

## Future Repository Structure

As the project grows, the source code will be organized as follows:

```
Code/
├── ESP32/
│   ├── Main/
│   ├── Servo_Control/
│   ├── Sensors/
│   ├── Walking/
│   ├── Balancing/
│   └── Utilities/
│
├── STM32/
│   ├── Core/
│   ├── Drivers/
│   ├── Middleware/
│   ├── Sensors/
│   ├── Control/
│   └── Navigation/
│
└── README.md
```

---

> **Note:** This codebase is actively under development. New features, optimizations, and hardware support will be added as the project progresses.
