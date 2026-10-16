import math

import rclpy
from rclpy.node import Node
from std_msgs.msg import Float32

from cone_interfaces.msg import ConeArray


def calculate_cte(orangeX, blueX, width):
    if width <= 0 or orangeX < 0 or blueX < 0:
        return math.nan

    if orangeX >= blueX:
        return math.nan

    trackMid = (orangeX + blueX) / 2.0
    imageMid = width / 2.0
    return trackMid - imageMid


class TrackPlanner(Node):
    def __init__(self):
        super().__init__("track_planner")

        self.declare_parameter("image_width", 320)
        self.width = self.get_parameter("image_width").value
        self.orange = None

        self.pub = self.create_publisher(
            Float32, "/track_planner/cte", 10
        )
        self.sub = self.create_subscription(
            ConeArray,
            "/cone_detector/cones",
            self.cone_callback,
            10,
        )

    def cone_callback(self, msg):
        if msg.colour == "orange":
            self.orange = msg.pixel_x
            return

        if msg.colour != "blue":
            self.get_logger().warning(f"Ignoring unknown colour: {msg.colour}")
            return

        orangeX = -1 if self.orange is None else self.orange
        cte = calculate_cte(orangeX, msg.pixel_x, self.width)
        self.orange = None

        output = Float32()
        output.data = float(cte)
        self.pub.publish(output)


def main(args=None):
    rclpy.init(args=args)
    node = TrackPlanner()
    try:
        rclpy.spin(node)
    finally:
        node.destroy_node()
        rclpy.shutdown()


if __name__ == "__main__":
    main()
