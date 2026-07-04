# Robotics Journey

A hands-on portfolio of mobile-robotics projects built on **ROS 2 Humble** and **Gazebo Classic**, working up from a robot that can barely move to autonomous navigation with SLAM.

Each project is a self-contained colcon package under `src/`, introducing one core pillar of mobile robotics. Built to learn the *why* alongside the *how* — see `LEARNING_LOG.md` for notes and reasoning along the way.

## Projects

| # | Project | Core concepts |
|---|---------|---------------|
| 1 | Differential-drive robot + teleop | URDF, TF2, diff-drive kinematics |
| 2 | Reactive sensing | LiDAR, RViz, reactive control |
| 3 | State estimation | Odometry, sensor fusion (EKF) |
| 4 | SLAM | Mapping, scan matching, loop closure |
| 5 | Autonomous navigation | Nav2, costmaps, planning & control |

*Autonomous navigation (Nav2) milestone complete*

## Stack

- ROS 2 Humble
- Gazebo Classic 11
- Ubuntu 22.04

See [docs/SETUP.md](docs/SETUP.md) for full environment setup instructions.

## Build

```bash
colcon build
source install/setup.bash
```

## Getting Started (Daily Workflow)

This project runs entirely inside a containerised ROS 2 Humble + Gazebo environment.
See [docs/SETUP.md](docs/SETUP.md) for one-time setup. Once set up, the daily ritual is:

### 1. Allow GUI apps (once per login session)

```bash
xhost +local:root
```

> Needed after every reboot/login — X11 access resets per session.

### 2. Start the environment (once per work session)

```bash
docker compose up -d        # starts the container in the background
docker compose ps           # confirm the 'ros' service shows "running"
```

### 3. Open as many terminals as you need

Each terminal enters the *same* running container, so all nodes share one ROS network:

```bash
docker compose exec ros bash
```

Inside the container you have the full ROS 2 + Gazebo toolchain. Examples:

```bash
ign gazebo                          # launch the simulator
rviz2                               # launch RViz
ros2 run demo_nodes_cpp talker      # run a node
ros2 topic list                     # inspect topics
```

Your code lives in `src/` on the host and appears at `/root/ros2_ws/src` inside the container.

### 4. Stop the environment (end of session)

```bash
docker compose down         # stops and removes the container
```

> The container is disposable — your code is safe on the host in `src/`. Stopping it loses nothing that matters.