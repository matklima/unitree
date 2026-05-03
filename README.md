# Unitree


## 🛠️ Installation Guide

Ovaj projekt je razvijen i testiran na operacijskom sustavu **Ubuntu 22.04** uz **ROS 2 Humble**. Za simulacijsko okruženje koristi se **Gazebo**.

### 1. Preduvjeti
Osigurajte da imate instaliranu Desktop verziju ROS 2 Humble. Ako nemate, slijedite [službene upute za instalaciju](https://docs.ros.org/en/humble/Installation.html).

Također, instalirajte Gazebo i potrebne ROS 2 pakete za rad s robotima:
```bash
sudo apt update
sudo apt install ros-humble-desktop \
                 ros-humble-gazebo-ros-pkgs \
                 ros-humble-xacro \
                 ros-humble-joint-state-publisher-gui \
                 ros-humble-ros2-control \
                 ros-humble-ros2-controllers



### 2. Postavljanje workspacea

```bash
mkdir -p ~/ros2_ws/src
cd ~/ros2_ws/src

# Klonirajte ovaj repozitorij
git clone <git@github.com:matklima/unitree.git> klimaby

# Klonirajte Unitree Go2 opisni paket (potreban za URDF i Gazebo scene)
git clone https://github.com/abizovnuralem/unitree_go2_ros2.git
```

### 3. Install i build

```bash
pip install numpy
cd ~/ros2_ws
rosdep install --from-paths src --ignore-src -r -y
colcon build --symlink-install
source install/setup.bash
```

### 4. Pokretanje simulacije i spawnanje robota go2

```bash
ros2 launch go2_config gazebo.launch.py rviz:=true world:=/home/mateo/ros2_ws/install/go2_config/share/go2_config/worlds/outdoor.world world_init_z:=0.6
```

### 5. Pokretanje logike robota

```bash
ros2 launch klimaby autonomy.launch.py
```

### 6. Dodavanje overlay-a (opcionalno)

Ako želite dodati vlastite modifikacije na robota (npr. dodatne senzore ili linkove) bez mijenjanja originalnog koda:

1. Napravite overlay workspace:
   ```bash
   mkdir -p ~/overlay_ws/src
   cp -r ~/ros2_ws/src/unitree-go2-ros2/robots/descriptions/go2_description ~/overlay_ws/src/
   ```

2. Modificirajte `~/overlay_ws/src/go2_description/xacro/robot.xacro` da dodate svoje elemente na kraj.

3. Build-ajte overlay:
   ```bash
   cd ~/overlay_ws && colcon build
   source install/setup.bash
   ```

4. Sada će launch koristiti overlay verziju s vašim dodacima.
