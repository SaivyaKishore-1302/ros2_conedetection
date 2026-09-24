import os

from ament_index_python.packages import get_package_share_directory
from launch import LaunchDescription
from launch.actions import IncludeLaunchDescription
from launch.launch_description_sources import PythonLaunchDescriptionSource
from launch_ros.actions import Node


def generate_launch_description():
    world = os.path.join(
        get_package_share_directory("cone_navigator"),
        "worlds",
        "track_world.sdf")

    gazebo = IncludeLaunchDescription(
        PythonLaunchDescriptionSource(
            os.path.join(
                get_package_share_directory("gazebo_ros"),
                "launch",
                "gazebo.launch.py")),
        launch_arguments={"world": world}.items())

    model = os.path.join(
        get_package_share_directory("turtlebot3_gazebo"),
        "models",
        "turtlebot3_burger_cam",
        "model.sdf")

    spawn = Node(
        package="gazebo_ros",
        executable="spawn_entity.py",
        arguments=[
            "-file", model,
            "-entity", "turtlebot3_burger_cam",
            "-x", "0.0",
            "-y", "0.0",
            "-z", "0.02",
            "-Y", "0.0",
            "-timeout", "60.0"],
        output="screen")

    return LaunchDescription([
        gazebo,
        spawn,
    ])
