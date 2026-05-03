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