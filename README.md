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

*Projects added as the journey progresses.*

## Stack

- ROS 2 Humble
- Gazebo Classic 11
- Ubuntu 22.04

## Build

```bash
colcon build
source install/setup.bash
```