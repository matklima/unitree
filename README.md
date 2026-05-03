# Unitree GO2

## 🛠️ Installation Guide

This project was developed and tested on **Ubuntu 22.04** with **ROS 2 Humble**. **Gazebo** is used for the simulation environment.

### 1. Prerequisites
Ensure you have the Desktop version of ROS 2 Humble installed. If not, follow the [official installation instructions](https://docs.ros.org/en/humble/Installation.html).

Also, install Gazebo and the necessary ROS 2 packages for working with robots:
```bash
sudo apt update
sudo apt install ros-humble-desktop \
                 ros-humble-gazebo-ros-pkgs \
                 ros-humble-xacro \
                 ros-humble-joint-state-publisher-gui \
                 ros-humble-ros2-control \
                 ros-humble-ros2-controllers



### 2. Setting up the workspace

```bash
mkdir -p ~/ros2_ws/src
cd ~/ros2_ws/src

# Clone this repository
git clone <git@github.com:matklima/unitree.git> klimaby

# Clone the Unitree Go2 description package (required for URDF and Gazebo scenes)
git clone https://github.com/abizovnuralem/unitree_go2_ros2.git
```

# Patch Setup for unitree_go2_ros2

This project requires a patch to be applied to the `unitree_go2_ros2` repository before building the ROS2 workspace.

## Patch Location
The patch file is located at: ~/ros2_ws/src/klimaby/laser_unitree.patch
The patch must be applied inside: ~/ros2_ws/src/unitree_go2_ros2
Navigate to the target repository:

```bash
cd ~/ros2_ws/src/unitree_go2_ros2
git apply ~/ros2_ws/src/klimaby/laser_unitree.patch
```

### 3. Install and build

```bash
pip install numpy
cd ~/ros2_ws
rosdep install --from-paths src --ignore-src -r -y
colcon build --symlink-install
source install/setup.bash
```

### 4. Running the simulation and spawning the go2 robot

```bash
ros2 launch go2_config gazebo.launch.py rviz:=true world:=/home/mateo/ros2_ws/install/go2_config/share/go2_config/worlds/outdoor.world world_init_z:=0.6
```

### 5. Running the robot logic

```bash
ros2 launch klimaby autonomy.launch.py
```

## Sim2Real Considerations

This project is developed and validated in simulation (Gazebo), which introduces a gap between simulated and real-world performance. Below is an overview of known sim-to-real challenges, along with the mitigation strategies implemented in this repository where applicable.

---

### Addressed Sim2Real Challenges

#### 1. Sensor Noise and Outliers

**Problem:**  
Simulated LiDAR data is typically clean and deterministic, while real sensors produce noisy, inconsistent measurements with occasional spikes or dropouts.

**Mitigation implemented:**  
The perception pipeline applies:
- Percentile filtering (10th percentile)
- Sliding window median filtering

This reduces the impact of outliers and improves robustness against noisy measurements.

---

#### 2. Control Instability (Abrupt Motion Changes)

**Problem:**  
In simulation, robots respond instantly to velocity commands. In reality, motors have inertia and cannot change velocity abruptly.

**Mitigation implemented:**  
The actuation node includes:
- Velocity ramping (`accel_limit`)
- Gradual transitions between target velocities

This avoids sudden jumps in motion and better approximates real actuator behavior.

---

#### 3. Node Failure and Communication Loss

**Problem:**  
In real systems, nodes may crash or communication may be interrupted, potentially leaving the robot in an unsafe state.

**Mitigation implemented:**  
- Watchdog timers in both decision and actuation layers
- Automatic fallback to STOP if no updates are received within a timeout

This ensures the robot halts safely in case of system failure.

---

#### 4. Oscillatory Behavior Near Obstacles

**Problem:**  
Reactive systems often oscillate when switching rapidly between states (e.g. left/right turns).

**Mitigation implemented:**  
- Forced turn duration (`forced_turn_steps`)
- Short and long turn phases

This introduces temporal consistency in decisions and prevents rapid direction switching 
---

### Known Sim2Real Challenges (Not Fully Addressed)

The following issues are inherent to simulation-based development but are not fully mitigated in this project:

#### 1. Latency and Timing Delays
- Real systems introduce delays in sensing, processing, and actuation
- The current implementation assumes near-instant feedback

---

#### 2. Imperfect Robot Dynamics
- No modeling of wheel slip, actuator lag, or uneven terrain
- Simulated motion is more stable than real-world motion

---

#### 3. Sensor Placement and Calibration Errors
- Real sensors may be misaligned or offset
- Blind spots and occlusions are not explicitly modeled

---

#### 4. Environment Variability
- Simulation environments are static and predictable
- Real environments include moving objects, irregular surfaces, and dynamic obstacles

---

#### 5. Threshold Sensitivity
- Decision-making relies on fixed distance thresholds
- These values may not transfer directly to real hardware due to sensor inaccuracies

---

#### 6. Lack of Global Planning
- The system is purely reactive
- No mapping, localization, or path planning is implemented

This may result in:
- Local minima
- Circling behavior
- Inefficient paths

---

#### 7. Overfitting to Simulation Scenarios
- Behavior tuned for specific Gazebo worlds
- Performance may degrade in unseen environments

---

## Summary

This repository implements a reactive obstacle avoidance system with basic robustness improvements for real-world deployment, including filtering, motion smoothing, and safety fallbacks.

However, it does not attempt to fully bridge the sim-to-real gap. Additional work such as sensor modeling, dynamic tuning, and integration with higher-level navigation frameworks would be required for reliable real-world operation.