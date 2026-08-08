# 🛠️ CAD Files

This folder contains the complete 3D CAD models of the Robotic Dog used for mechanical design, assembly, and manufacturing.

## Contents

- **ROBOTIC DOG.step** – Complete 3D assembly of the robotic dog in STEP format.

## Design Features

- 12-DOF Quadruped Mechanical Structure
- Modular Leg Design
- Lightweight 3D Printable Parts
- Servo Mounting Brackets
- Expandable Electronics Compartment
- Easy Assembly and Maintenance

## Software Used

- Autodesk Fusion 360

## Manufacturing

The robot is designed primarily for **3D printing** using PLA And Pla-CF filament. The modular design allows damaged components to be replaced individually without reprinting the entire robot.

## 🧩 Part Naming Convention

The STL files are exported from the CAD assembly and use the original
part/component naming used during mechanical development.

Common naming references:

- `L` — Left-side component
- `R` — Right-side component
- `F` — Front component
- `B` — Back component
- `T` — Top component
- `foot` — Foot component
- `plate` — Structural plate
- `cover` — Protective/servo cover
- `arm` — Leg/arm structural component
- `joint` — Joint component
- `shoulder` — Shoulder/upper-leg component
- `wrist` — Lower joint component
- `ultra_sonic` — Ultrasonic sensor mounting component
- `mg` — Component associated with the servo/motor mounting assembly
## Future Updates

The CAD model will be updated as the project progresses, including:

- Weight optimization
- Improved structural strength
- STM32 electronics enclosure
- Sensor mounting brackets
- Battery compartment redesign

## 📦 Available Files

### Complete Assembly

- `ROBOTIC DOG.step` — Complete CAD assembly of the robotic dog.

### Printable Components

The folder also contains individual STL files exported from the CAD assembly for 3D printing.

These files represent the current prototype components and may change as the mechanical design is revised.

---

## 🖨️ 3D Printing

The STL files are intended for additive manufacturing and prototype fabrication.

Printing parameters may vary depending on:

- Printer
- Nozzle diameter
- Layer height
- Infill
- Material
- Part orientation
- Structural requirements

Recommended printing parameters will be documented as the design is validated.

---

## 🔧 Mechanical Design

The robot is designed as a modular 12-DOF quadruped platform.

The mechanical design focuses on:

- Modular leg assemblies
- Servo accessibility
- Replaceable structural components
- 3D-printable geometry
- Compact packaging
- Ease of assembly and maintenance

---

## 📐 Design Analysis

Mechanical analysis is currently under development.

Planned analysis includes:

- Joint torque requirements
- Servo torque margin
- Robot mass
- Center of mass
- Structural loading
- FEA of critical components
- Manufacturing tolerances

Measured and calculated results will be added as the prototype is experimentally validated.

---

## 🔄 Design Status

The CAD model represents the current physical prototype.

The design is **not considered final** and may change based on:

- Servo performance
- Structural testing
- Walking experiments
- Weight distribution
- Mechanical failures
- Manufacturing tolerances
- Electronics integration

Future revisions will be documented through Git commits and updated CAD/STL files.

## 🧪 Structural / FEA Analysis

Finite Element Analysis will be used to identify mechanically critical components and improve the design.

Planned analysis includes:

- Static loading
- Joint mounting stress
- Leg deformation
- Factor of safety
- Critical component identification

FEA results will be added to the repository as the mechanical design is finalized.

---

## 📏 Tolerance & Manufacturing Notes

The robot is manufactured using 3D printing, so dimensional tolerances are important for:

- Servo mounting
- Bearing interfaces
- Screw holes
- Joint alignment
- Press-fit components
- Interlocking parts

Print-specific tolerances and design revisions will be documented as the prototype is iterated.

---
- Cable management improvements

---

> **Note:** This CAD model is actively under development and may change as the mechanical design evolves.
