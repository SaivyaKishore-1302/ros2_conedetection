import cv2
from cv_bridge import CvBridge, CvBridgeError
from geometry_msgs.msg import Twist
import numpy as np
import rclpy
from rclpy.node import Node
from rclpy.qos import qos_profile_sensor_data as sensorQos
from sensor_msgs.msg import Image


yellowLow = np.array([20, 100, 100], dtype=np.uint8)
yellowHigh = np.array([30, 255, 255], dtype=np.uint8)
whiteLow = np.array([0, 0, 200], dtype=np.uint8)
whiteHigh = np.array([180, 30, 255], dtype=np.uint8)


def maskCentroid(mask):
    moments = cv2.moments(mask)
    if moments["m00"] <= 0.0:
        return None
    return float(moments["m10"] / moments["m00"])


def calculateTarget(yellowX, whiteX, imageWidth, laneOffset):
    if yellowX is not None and whiteX is not None:
        return (yellowX + whiteX) / 2.0
    if yellowX is not None:
        return yellowX + laneOffset
    if whiteX is not None:
        return whiteX - laneOffset
    return None


def calculateAngularVelocity(targetX, imageWidth, kp, maxSpeed):
    error = targetX - imageWidth / 2.0
    turn = kp * error
    return max(-maxSpeed, min(maxSpeed, turn))


class ColourFollower(Node):
    def __init__(self):
        super().__init__("colour_follower")

        self.declare_parameter("forward_speed", 0.10)
        self.declare_parameter("kp", 0.003)
        self.declare_parameter("max_angular_speed", 0.5)
        self.declare_parameter("lane_offset_pixels", 80.0)

        self.forwardSpeed = self.get_parameter("forward_speed").value
        self.kp = self.get_parameter("kp").value
        self.maxAngularSpeed = self.get_parameter(
            "max_angular_speed"
        ).value
        self.laneOffset = self.get_parameter("lane_offset_pixels").value

        self.bridge = CvBridge()
        self.imageSub = self.create_subscription(
            Image,
            "/camera/image_raw",
            self.imageCallback,
            sensorQos,
        )
        self.cmdPub = self.create_publisher(Twist, "/cmd_vel", 10)

    def imageCallback(self, msg):
        try:
            frame = self.bridge.imgmsg_to_cv2(msg, desired_encoding="bgr8")
        except CvBridgeError as error:
            self.get_logger().error(f"Could not convert camera image: {error}")
            self.publishStop()
            return

        width = frame.shape[1]
        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        yellowX = maskCentroid(cv2.inRange(hsv, yellowLow, yellowHigh))
        whiteX = maskCentroid(cv2.inRange(hsv, whiteLow, whiteHigh))
        targetX = calculateTarget(yellowX, whiteX, width, self.laneOffset)

        if targetX is None:
            self.publishStop()
            return

        command = Twist()
        command.linear.x = float(self.forwardSpeed)
        command.angular.z = float(calculateAngularVelocity(
            targetX,
            width,
            self.kp,
            self.maxAngularSpeed,
        ))
        self.cmdPub.publish(command)

    def publishStop(self):
        self.cmdPub.publish(Twist())


def main(args=None):
    rclpy.init(args=args)
    node = ColourFollower()
    try:
        rclpy.spin(node)
    finally:
        node.publishStop()
        node.destroy_node()
        rclpy.shutdown()


if __name__ == "__main__":
    main()
