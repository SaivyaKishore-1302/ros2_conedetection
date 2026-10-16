import math

from geometry_msgs.msg import Twist
import rclpy
from rclpy.node import Node
from rclpy.qos import qos_profile_sensor_data as sensorQos
from sensor_msgs.msg import LaserScan


def nearestObstacles(scan, frontAngle=30.0, sideAngle=90.0):
    front = []
    left = []
    right = []

    angle = scan.angle_min
    for distance in scan.ranges:
        normalized = math.atan2(math.sin(angle), math.cos(angle))
        degrees = math.degrees(normalized)
        valid = (
            math.isfinite(distance)
            and scan.range_min <= distance <= scan.range_max
        )

        if valid:
            if abs(degrees) <= frontAngle:
                front.append(distance)
            elif frontAngle < degrees <= sideAngle:
                left.append(distance)
            elif -sideAngle <= degrees < -frontAngle:
                right.append(distance)

        angle += scan.angle_increment

    return (
        min(front, default=math.inf),
        min(left, default=math.inf),
        min(right, default=math.inf),
    )


def calculateCommand(
    frontDistance,
    leftDistance,
    rightDistance,
    obstacleDistance,
    forwardSpeed,
    turningSpeed,
):
    if frontDistance > obstacleDistance:
        return forwardSpeed, 0.0
    if leftDistance > rightDistance:
        return 0.0, turningSpeed
    return 0.0, -turningSpeed


class ObstacleAvoider(Node):
    def __init__(self):
        super().__init__("obstacle_avoider")

        self.declare_parameter("forward_speed", 0.2)
        self.declare_parameter("turning_speed", 0.5)
        self.declare_parameter("obstacle_distance", 0.5)
        self.declare_parameter("scan_timeout", 0.5)

        self.forwardSpeed = self.get_parameter("forward_speed").value
        self.turningSpeed = self.get_parameter("turning_speed").value
        self.obstacleDistance = self.get_parameter(
            "obstacle_distance"
        ).value
        self.scanTimeout = self.get_parameter("scan_timeout").value

        self.frontDistance = math.inf
        self.leftDistance = math.inf
        self.rightDistance = math.inf
        self.lastScanTime = None

        self.sub = self.create_subscription(
            LaserScan,
            "/scan",
            self.scanCallback,
            sensorQos,
        )
        self.pub = self.create_publisher(Twist, "/cmd_vel", 10)
        self.timer = self.create_timer(0.1, self.controlCallback)

    def scanCallback(self, scan):
        (
            self.frontDistance,
            self.leftDistance,
            self.rightDistance,
        ) = nearestObstacles(scan)
        self.lastScanTime = self.get_clock().now()

    def controlCallback(self):
        if self.lastScanTime is None:
            self.publishStop()
            return

        age = self.get_clock().now() - self.lastScanTime
        if age.nanoseconds / 1e9 > self.scanTimeout:
            self.lastScanTime = None
            self.publishStop()
            return

        linear, angular = calculateCommand(
            self.frontDistance,
            self.leftDistance,
            self.rightDistance,
            self.obstacleDistance,
            self.forwardSpeed,
            self.turningSpeed,
        )
        command = Twist()
        command.linear.x = float(linear)
        command.angular.z = float(angular)
        self.pub.publish(command)

    def publishStop(self):
        self.pub.publish(Twist())


def main(args=None):
    rclpy.init(args=args)
    node = ObstacleAvoider()
    try:
        rclpy.spin(node)
    finally:
        node.publishStop()
        node.destroy_node()
        rclpy.shutdown()


if __name__ == "__main__":
    main()
