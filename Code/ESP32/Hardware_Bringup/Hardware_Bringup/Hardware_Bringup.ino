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
#include <Adafruit_PWMServoDriver.h>
#include <Adafruit_MPU6050.h>
#include <Adafruit_Sensor.h>
#include <Adafruit_VL53L0X.h>

// ESP32 Default I2C Pins
#define I2C_SDA 21
#define I2C_SCL 22

// Initialize PCA9685 Servo Driver
Adafruit_PWMServoDriver pwm = Adafruit_PWMServoDriver(0x40);

// Initialize Dual MPU6500 Sensors (Using different I2C addresses)
Adafruit_MPU6050 mpu1; // Will be initialized at 0x68
Adafruit_MPU6050 mpu2; // Will be initialized at 0x69

// Initialize ToF Distance Sensor
Adafruit_VL53L0X lox = Adafruit_VL53L0X();

// PCA9685 standard servo settings
#define SERVOMIN  150 
#define SERVOMAX  600 

// ==========================================
// HARDCODED STANDING ANGLES
// ==========================================
const int FL_HIP   = 75;  const int FL_THIGH = 105; const int FL_KNEE  = 15; 
const int FR_HIP   = 90;  const int FR_THIGH = 95;  const int FR_KNEE  = 135;
const int BL_HIP   = 88;  const int BL_THIGH = 145; const int BL_KNEE  = 45;
const int BR_HIP   = 80;  const int BR_THIGH = 50;  const int BR_KNEE  = 145;

// Function Prototypes
int angleToPulse(int angle);
void standUp();
void readSensors();

void setup() {
  Serial.begin(115200);
  delay(500); 
  Serial.println("ESP32 Robotic Dog Initializing...");

  // Explicitly initialize I2C on ESP32 pins 21 and 22
  Wire.begin(I2C_SDA, I2C_SCL); 
  
  // 1. Initialize PCA9685
  pwm.begin();
  pwm.setPWMFreq(60);  

  // 2. Initialize MPU6500 #1 (AD0 to GND -> 0x68)
  if (!mpu1.begin(0x68)) {
    Serial.println("Failed to find MPU6500 #1 chip (0x68)");
  }

  // 3. Initialize MPU6500 #2 (AD0 to 3.3V -> 0x69)
  if (!mpu2.begin(0x69)) {
    Serial.println("Failed to find MPU6500 #2 chip (0x69)");
  }

  // 4. Initialize VL53L0X Distance Sensor
  if (!lox.begin()) {
    Serial.println(F("Failed to boot VL53L0X"));
  }

  // Configure IMU Ranges (Optional but recommended)
  mpu1.setAccelerometerRange(MPU6050_RANGE_8_G);
  mpu1.setGyroRange(MPU6050_RANGE_500_DEG);
  mpu2.setAccelerometerRange(MPU6050_RANGE_8_G);
  mpu2.setGyroRange(MPU6050_RANGE_500_DEG);

  delay(1000);
  
  // Command the dog to stand up immediately on boot
  standUp();
}

void loop() {
  // Read and print sensor information
  readSensors();
  
  delay(200); // 5Hz update rate for readings to keep the loop readable
}

// Function to convert degrees (0-180) to PCA9685 pulse width ticks
int angleToPulse(int angle) {
  return map(angle, 0, 180, SERVOMIN, SERVOMAX);
}

void standUp() {
  Serial.println("Moving servos to standing angles...");

  // ---- LEG 1: FRONT LEFT ----
  pwm.setPWM(0, 0, angleToPulse(FL_HIP));
  pwm.setPWM(1, 0, angleToPulse(FL_THIGH));
  pwm.setPWM(2, 0, angleToPulse(FL_KNEE));

  // ---- LEG 2: FRONT RIGHT ----
  pwm.setPWM(3, 0, angleToPulse(FR_HIP));
  pwm.setPWM(4, 0, angleToPulse(FR_THIGH));
  pwm.setPWM(5, 0, angleToPulse(FR_KNEE));

  // ---- LEG 3: BACK LEFT ----
  pwm.setPWM(12, 0, angleToPulse(BL_HIP));
  pwm.setPWM(13, 0, angleToPulse(BL_THIGH));
  pwm.setPWM(14, 0, angleToPulse(BL_KNEE));

  // ---- LEG 4: BACK RIGHT ----
  pwm.setPWM(9, 0, angleToPulse(BR_HIP));
  pwm.setPWM(10, 0, angleToPulse(BR_THIGH));
  pwm.setPWM(11, 0, angleToPulse(BR_KNEE));

  Serial.println("Dog is now standing.");
}

void readSensors() {
  // Container variables for MPU data
  sensors_event_t a1, g1, temp1;
  sensors_event_t a2, g2, temp2;
  
  // Fetch data from both IMUs
  mpu1.getEvent(&a1, &g1, &temp1);
  mpu2.getEvent(&a2, &g2, &temp2);

  // Fetch data from Distance Sensor
  VL53L0X_RangingMeasurementData_t measure;
  lox.rangingTest(&measure, false); 

  // Print IMU 1 Data
  Serial.print("IMU1 -> Accel X: "); Serial.print(a1.acceleration.x);
  Serial.print(" Y: "); Serial.print(a1.acceleration.y);
  Serial.print(" Z: "); Serial.print(a1.acceleration.z);
  Serial.print(" m/s^2 | Gyro X: "); Serial.print(g1.gyro.x);
  Serial.print(" Y: "); Serial.print(g1.gyro.y);
  Serial.print(" Z: "); Serial.println(g1.gyro.z);

  // Print IMU 2 Data
  Serial.print("IMU2 -> Accel X: "); Serial.print(a2.acceleration.x);
  Serial.print(" Y: "); Serial.print(a2.acceleration.y);
  Serial.print(" Z: "); Serial.print(a2.acceleration.z);
  Serial.print(" m/s^2 | Gyro X: "); Serial.print(g2.gyro.x);
  Serial.print(" Y: "); Serial.print(g2.gyro.y);
  Serial.print(" Z: "); Serial.println(g2.gyro.z);

  // Print Distance Data
  Serial.print("Distance: ");
  if (measure.RangeStatus != 4) {  // Phase 4 means out of range
    Serial.print(measure.RangeMilliMeter);
    Serial.println(" mm");
  } else {
    Serial.println(" Out of range ");
  }
  Serial.println("-------------------------------------------------------");
}
