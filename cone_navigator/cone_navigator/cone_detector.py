import math

import cv2
from cv_bridge import CvBridge, CvBridgeError
import numpy as np
import rclpy
from rclpy.node import Node
from rclpy.qos import qos_profile_sensor_data
from sensor_msgs.msg import Image

from cone_interfaces.msg import ConeArray


orangeLow = np.array([5, 100, 70], dtype=np.uint8)
orangeHigh = np.array([20, 255, 255], dtype=np.uint8)
blueLow = np.array([100, 100, 70], dtype=np.uint8)
blueHigh = np.array([130, 255, 255], dtype=np.uint8)


def analyse_cone(mask, minArea=200.0, scale=20.0):
    contours, _ = cv2.findContours(
        mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE
    )
    if not contours:
        return None

    contour = max(contours, key=cv2.contourArea)
    area = cv2.contourArea(contour)
    if area < minArea:
        return None

    moments = cv2.moments(contour)
    if moments["m00"] == 0.0:
        return None

    px = int(round(moments["m10"] / moments["m00"]))
    distance = scale / math.sqrt(area)
    return px, distance


class ConeDetector(Node):
    def __init__(self):
        super().__init__("cone_detector")

        self.declare_parameter("min_contour_area", 30.0)
        self.declare_parameter("distance_scale", 20.0)
        self.minArea = self.get_parameter("min_contour_area").value
        self.scale = self.get_parameter("distance_scale").value

        self.bridge = CvBridge()
        self.kernel = np.ones((5, 5), dtype=np.uint8)

        self.pub = self.create_publisher(
            ConeArray, "/cone_detector/cones", 10
        )
        self.sub = self.create_subscription(
            Image,
            "/camera/image_raw",
            self.image_callback,
            qos_profile_sensor_data,
        )

    def image_callback(self, msg):
        try:
            frame = self.bridge.imgmsg_to_cv2(msg, desired_encoding="bgr8")
        except CvBridgeError as error:
            self.get_logger().error(f"Could not convert camera image: {error}")
            return

        hsv = cv2.cvtColor(frame, cv2.COLOR_BGR2HSV)
        orangeMask = self._clean_mask(cv2.inRange(hsv, orangeLow, orangeHigh))
        blueMask = self._clean_mask(cv2.inRange(hsv, blueLow, blueHigh))

        orange = analyse_cone(orangeMask, self.minArea, self.scale)
        blue = analyse_cone(blueMask, self.minArea, self.scale)

        self._publish_observation("orange", orange)
        self._publish_observation("blue", blue)

    def _clean_mask(self, mask):
        mask = cv2.morphologyEx(
            mask, cv2.MORPH_OPEN, self.kernel
        )
        return cv2.morphologyEx(
            mask, cv2.MORPH_CLOSE, self.kernel
        )

    def _publish_observation(self, colour, detection):
        cone = ConeArray()
        cone.colour = colour
        if detection is None:
            cone.pixel_x = -1
            cone.distance = float("nan")
        else:
            cone.pixel_x = detection[0]
            cone.distance = float(detection[1])
        self.pub.publish(cone)


def main(args=None):
    rclpy.init(args=args)
    node = ConeDetector()
    try:
        rclpy.spin(node)
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == "__main__":
    main()
