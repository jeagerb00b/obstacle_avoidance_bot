# UGV Obstacle Avoidance — ROS 2 & Gazebo Simulation

A reactive obstacle avoidance system for an Unmanned Ground Vehicle (UGV),
built with ROS 2 Humble and simulated in Gazebo on Ubuntu 22.04.
The robot navigates autonomously using a Finite State Machine (FSM)
driven by real-time LiDAR sensor data — no maps, no ML, no path planning.

---


## Demo

> Robot navigating around obstacles in Gazebo with LiDAR rays visible in RViz2
![Pi7_GIF_CMP](https://github.com/user-attachments/assets/fc4b0ca9-4f48-4ba4-a5d3-c4724a597986)

---

## Overview

This project implements a **reactive control system** for a differential-drive UGV.
The robot uses a 360° simulated LiDAR to detect obstacles and reacts in real time
by transitioning through a 6-state FSM to avoid collisions and continue moving.

Developed as part of a Robotics & Control Systems internship assessment
focused on state machine design and ROS 2 simulation.

---

## Approach

| Aspect | Detail |
|---|---|
| **Algorithm** | Reactive FSM + Threshold-based LiDAR control |
| **Path Planning** | None (purely reactive) |
| **Sensor** | Simulated 360° LiDAR (libgazebo_ros_laser) |
| **Control** | Differential drive via /cmd_vel |
| **Turn Strategy** | Greedy — steers toward the more open side |

---

## State Machine
```
         ┌─────────┐
    ─────►  IDLE   │
         └────┬────┘
              │ on start
         ┌────▼────┐
    ┌───►  MOVING  ◄──────────┐
    │    └────┬────┘          │
    │         │ front < 1.2m  │
    │    ┌────▼──────┐        │
    │    │  AVOIDING │        │
    │    └────┬──────┘        │ clear
    │         │               │
    │    ┌────▼────┐          │
    │    │ TURNING ├──────────┘
    │    └────┬────┘
    │         │ front < 0.5m
    │    ┌────▼────┐
    │    │ STOPPED │
    │    └────┬────┘
    │         │
    │    ┌────▼──────────┐
    └────┤  RECOVERING   │ (reverse)
         └───────────────┘
```

| State | Trigger | Action |
|---|---|---|
| `IDLE` | On launch | Initializes, transitions to MOVING |
| `MOVING` | Path clear | Forward at 0.3 m/s |
| `AVOIDING` | Front < 1.2m | Slow forward + steer to open side |
| `TURNING` | Direction chosen | Rotate in place |
| `STOPPED` | Front < 0.5m | Full stop |
| `RECOVERING` | Stuck/stopped | Reverse at 0.2 m/s |

---

## Project Structure
```
ugv_obstacle_avoidance/
├── ugv_obstacle_avoidance/
│   ├── __init__.py
│   ├── state_machine.py          # Pure Python FSM (ROS-independent)
│   └── obstacle_avoidance_node.py # ROS 2 node — sensor & control
├── launch/
│   └── simulation.launch.py      # Gazebo + robot + node
├── worlds/
│   └── obstacle_world.world      # SDF world with obstacles
├── urdf/
│   └── ugv_robot.urdf            # Robot model + LiDAR + diff drive
├── package.xml
└── setup.py
```

---

## Tech Stack

- **ROS 2 Humble** — middleware, topics, nodes
- **Gazebo** — physics simulation
- **Python 3** — state machine + ROS node
- **RViz2** — visualization (LiDAR, odometry, TF)
- **Ubuntu 22.04**

---

## Requirements
```bash
sudo apt install -y \
  ros-humble-desktop \
  ros-humble-gazebo-ros-pkgs \
  ros-humble-robot-state-publisher \
  ros-humble-rviz2 \
  python3-colcon-common-extensions
```

---

## Build & Run
```bash
# Clone
git clone https://github.com/jeagerb00b/obstacle_avoidance_bot.git
cd ~/ros2_ws

# Build
colcon build --packages-select ugv_obstacle_avoidance --symlink-install
source install/setup.bash

# Launch simulation
ros2 launch ugv_obstacle_avoidance simulation.launch.py

# Visualize (new terminal)
source install/setup.bash
rviz2
```

---

## Verify Topics
```bash
ros2 topic list              # /scan /cmd_vel /odom /robot_state
ros2 topic hz /scan          # ~10 Hz
ros2 topic echo /robot_state # live state transitions
```

---

## RViz2 Setup

| Display | Topic | Purpose |
|---|---|---|
| `LaserScan` | `/scan` | Live LiDAR rays |
| `RobotModel` | — | 3D robot body |
| `Odometry` | `/odom` | Movement trail |
| `TF` | — | Coordinate frames |

> Set **Fixed Frame** to `odom`
> Set LaserScan **Reliability Policy** to `Best Effort`

---

## Key Design Decisions

- **FSM is decoupled from ROS** — `state_machine.py` is pure Python,
  making it independently testable without a running simulation
- **LiDAR split into 4 sectors** — front, left, right, rear for
  clean directional decision making
- **Greedy turn selection** — robot always steers toward whichever
  side has more free space
- **No global map needed** — fully reactive, works in unknown environments

---

---

## GitHub Repo Description (one-liner for the repo subtitle)
```
Reactive obstacle avoidance for a UGV using a 6-state FSM and simulated LiDAR — ROS 2 Humble + Gazebo on Ubuntu 22.04
```

## Topics/Tags to add on GitHub
```
ros2  gazebo  robotics  obstacle-avoidance  state-machine  
lidar  ugv  python  rviz2  ubuntu  simulation  autonomous-robot
