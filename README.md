# ROS 2 Vision and Navigation

A collection of ROS 2 Humble packages for camera-based cone navigation, lane
following, and reactive lidar obstacle avoidance on TurtleBot3.

The primary demonstration detects orange and blue track boundaries, estimates
the centre of the track, and adjusts both steering and forward speed while
driving through a closed Gazebo circuit.

## Packages

| Package | Description |
| --- | --- |
| `cone_interfaces` | Defines the `ConeArray` observation message. |
| `cone_navigator` | Detects cones, plans a track centre, and controls the robot. |
| `lane_follower` | Follows yellow and white lane markings from camera images. |
| `obstacle_avoider` | Avoids nearby lidar obstacles using reactive control. |

The controller packages publish directly to `/cmd_vel`. Run only one controller
at a time unless a velocity multiplexer is configured.

## Cone navigation pipeline

```text
/camera/image_raw
        |
        v
  cone_detector ----> /cone_detector/cones
                              |
                              v
                       track_planner ----> /track_planner/cte
                                                   |
                                                   v
                                        velocity_controller ----> /cmd_vel
```

The detector applies HSV colour masks and contour filtering. The planner uses
the nearest orange and blue observations to calculate cross-track error in
image pixels. The controller applies proportional steering, slows for larger
turns, and stops when perception data is invalid or stale.

## Requirements

- Ubuntu 22.04
- ROS 2 Humble
- Gazebo Classic with `gazebo_ros`
- TurtleBot3 Gazebo packages
- OpenCV, NumPy, and `cv_bridge`

Install the system dependencies:

```bash
sudo apt update
sudo apt install ros-humble-gazebo-ros-pkgs ros-humble-turtlebot3-gazebo \
  ros-humble-cv-bridge python3-opencv python3-numpy
```

## Build

Clone the repository into a ROS 2 workspace and resolve its dependencies:

```bash
mkdir -p ~/ros2_ws/src
cd ~/ros2_ws/src
git clone https://github.com/SaivyaKishore-1302/ros2_conedetection.git
cd ~/ros2_ws
source /opt/ros/humble/setup.bash
rosdep install --from-paths src --ignore-src -r -y
colcon build --symlink-install
source install/setup.bash
```

## Run the cone-track demonstration

Set the TurtleBot3 model and launch the Gazebo world:

```bash
export TURTLEBOT3_MODEL=burger
ros2 launch cone_navigator cone_world.launch.py
```

In another sourced terminal, launch the perception and control pipeline:

```bash
source /opt/ros/humble/setup.bash
source ~/ros2_ws/install/setup.bash
ros2 launch cone_navigator cone_navigator.launch.py
```

Useful diagnostics:

```bash
ros2 topic echo /cone_detector/cones
ros2 topic echo /track_planner/cte
ros2 topic echo /cmd_vel
```

## Run the additional controllers

Run the lane follower with a compatible camera source:

```bash
ros2 run lane_follower follower_node
```

Run reactive obstacle avoidance with a compatible lidar source:

```bash
ros2 run obstacle_avoider obstacle_avoider
```

## Parameters

### Cone detector

| Parameter | Default | Description |
| --- | ---: | --- |
| `min_contour_area` | `30.0` | Minimum accepted colour contour area. |
| `distance_scale` | `20.0` | Scale used for contour-based distance estimates. |

### Track planner

| Parameter | Default | Description |
| --- | ---: | --- |
| `image_width` | `320` | Camera width used to calculate image centre. |

### Velocity controller

| Parameter | Default | Description |
| --- | ---: | --- |
| `forward_speed` | `0.30` | Cruise speed in metres per second. |
| `minimum_forward_speed` | `0.10` | Minimum speed maintained during turns. |
| `braking_distance` | `0.40` | Cone distance at which turn braking increases. |
| `braking_turn_rate` | `0.65` | Turn rate that applies maximum steering braking. |
| `kp` | `0.012` | Proportional steering gain. |
| `max_angular_speed` | `0.9` | Maximum turn rate in radians per second. |
| `steering_smoothing` | `0.30` | Fraction of each new steering command applied per frame. |
| `steering_deadband` | `4.0` | Pixel error ignored near the image centre. |
| `command_timeout` | `0.8` | Seconds without valid input before stopping. |

### Lane follower

| Parameter | Default | Description |
| --- | ---: | --- |
| `forward_speed` | `0.10` | Forward speed in metres per second. |
| `kp` | `0.003` | Proportional steering gain. |
| `max_angular_speed` | `0.5` | Maximum turn rate in radians per second. |
| `lane_offset_pixels` | `80.0` | Estimated lane-centre offset from one boundary. |

### Obstacle avoider

| Parameter | Default | Description |
| --- | ---: | --- |
| `forward_speed` | `0.2` | Forward speed when the path is clear. |
| `turning_speed` | `0.5` | Turn rate used to avoid an obstacle. |
| `obstacle_distance` | `0.5` | Minimum front clearance in metres. |
| `scan_timeout` | `0.5` | Seconds without a lidar scan before stopping. |

Parameters can be overridden with standard ROS 2 arguments:

```bash
ros2 run obstacle_avoider obstacle_avoider --ros-args \
  -p obstacle_distance:=0.7 -p forward_speed:=0.15
```

## Tests

```bash
colcon test
colcon test-result --verbose
```

## Safety behaviour

The cone controller stops on invalid detections or stale planner data. The lane
follower stops when neither boundary is visible. The obstacle avoider stops
until it receives lidar data and whenever the scan stream becomes stale.

## Demonstration video

[View the original demonstration](https://drive.google.com/file/d/13nKGqd9Z5ggIJkrGQ4r6ISFWwyiYIKlq/view?usp=sharing).

## License

This project is licensed under the Apache License 2.0. See `LICENSE` for details.
