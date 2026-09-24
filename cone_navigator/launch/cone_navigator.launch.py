from launch import LaunchDescription
from launch_ros.actions import Node


def generate_launch_description():
    return LaunchDescription([
        Node(
            package="cone_navigator",
            executable="cone_detector",
            name="cone_detector",
            output="screen",
        ),
        Node(
            package="cone_navigator",
            executable="track_planner",
            name="track_planner",
            output="screen",
        ),
        Node(
            package="cone_navigator",
            executable="velocity_controller",
            name="velocity_controller",
            output="screen",
        ),
    ])
