# ROS 2 Cone Detection and Navigation

A camera-based TurtleBot3 navigation pipeline for ROS 2 Humble and Gazebo. The robot detects orange and blue cones, estimates the track centre, and publishes velocity commands that steer it between the cone boundaries.

## Pipeline

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

The detector uses HSV colour masks and contour filtering. The planner pairs the nearest orange and blue observations and calculates cross-track error in image pixels. The controller applies proportional steering and stops the robot when valid perception data is unavailable.

## Repository structure

```text
ros2_conedetection/
├── cone_interfaces/       Custom ConeArray message
└── cone_navigator/
    ├── cone_navigator/    Detector, planner, and controller nodes
    ├── launch/            Gazebo and navigation launch files
    └── worlds/            Cone-track Gazebo world
```

## Requirements

- Ubuntu 22.04
- ROS 2 Humble
- Gazebo Classic with `gazebo_ros`
- TurtleBot3 Gazebo packages
- OpenCV, NumPy, and `cv_bridge`

Install the ROS dependencies:

```bash
sudo apt update
sudo apt install ros-humble-gazebo-ros-pkgs ros-humble-turtlebot3-gazebo \
  ros-humble-cv-bridge python3-opencv python3-numpy
```

## Build

Clone the repository into the `src` directory of a ROS 2 workspace:

```bash
mkdir -p ~/ros2_ws/src
cd ~/ros2_ws/src
git clone https://github.com/SaivyaKishore-1302/ros2_conedetection.git
cd ~/ros2_ws
source /opt/ros/humble/setup.bash
rosdep install --from-paths src --ignore-src -r -y
colcon build --packages-select cone_interfaces cone_navigator
source install/setup.bash
```

## Run

Set the TurtleBot3 model and start the Gazebo world:

```bash
export TURTLEBOT3_MODEL=burger
ros2 launch cone_navigator cone_world.launch.py
```

In a second terminal, source the workspace and start the navigation pipeline:

```bash
source /opt/ros/humble/setup.bash
source ~/ros2_ws/install/setup.bash
ros2 launch cone_navigator cone_navigator.launch.py
```

## Nodes and parameters

### `cone_detector`

Subscribes to `/camera/image_raw` and publishes cone observations on `/cone_detector/cones`.

| Parameter | Default | Purpose |
| --- | ---: | --- |
| `min_contour_area` | `30.0` | Rejects small colour blobs |
| `distance_scale` | `20.0` | Scales contour area into estimated distance |

### `track_planner`

Publishes cross-track error on `/track_planner/cte`.

| Parameter | Default | Purpose |
| --- | ---: | --- |
| `image_width` | `320` | Camera image width used to calculate its centre |

### `velocity_controller`

Publishes motion commands on `/cmd_vel`.

| Parameter | Default | Purpose |
| --- | ---: | --- |
| `forward_speed` | `0.2` | Forward velocity in metres per second |
| `kp` | `0.004` | Proportional steering gain |
| `max_angular_speed` | `1.0` | Maximum turn rate in radians per second |
| `command_timeout` | `0.5` | Seconds without a valid error before stopping |

## Useful checks

```bash
ros2 topic echo /cone_detector/cones
ros2 topic echo /track_planner/cte
ros2 topic echo /cmd_vel
```

## Safety behaviour

The controller publishes a zero velocity command when detections are invalid, the cone pair is reversed, or the perception update times out.

## Video

https://drive.google.com/file/d/13nKGqd9Z5ggIJkrGQ4r6ISFWwyiYIKlq/view?usp=sharing
