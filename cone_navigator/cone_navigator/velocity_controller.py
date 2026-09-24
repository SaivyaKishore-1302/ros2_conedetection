import math

from geometry_msgs.msg import Twist
import rclpy
from rclpy.node import Node
from std_msgs.msg import Float32


def calculate_angular_velocity(cte, kp, maxSpeed):
    if not math.isfinite(cte):
        return None

    turn = -kp * cte
    return max(-maxSpeed, min(maxSpeed, turn))


class VelocityController(Node):
    def __init__(self):
        super().__init__("velocity_controller")

        self.declare_parameter("forward_speed", 0.2)
        self.declare_parameter("kp", 0.004)
        self.declare_parameter("max_angular_speed", 1.0)
        self.declare_parameter("command_timeout", 0.5)

        self.speed = self.get_parameter("forward_speed").value
        self.kp = self.get_parameter("kp").value
        self.maxSpeed = self.get_parameter("max_angular_speed").value
        self.timeout = self.get_parameter("command_timeout").value
        self.lastTime = None

        self.pub = self.create_publisher(Twist, "/cmd_vel", 10)
        self.sub = self.create_subscription(
            Float32,
            "/track_planner/cte",
            self.cte_callback,
            10,
        )
        self.timer = self.create_timer(0.1, self.watchdog_callback)

    def cte_callback(self, msg):
        turn = calculate_angular_velocity(
            msg.data, self.kp, self.maxSpeed
        )
        if turn is None:
            self.lastTime = None
            self.publish_stop()
            return

        cmd = Twist()
        cmd.linear.x = float(self.speed)
        cmd.angular.z = float(turn)
        self.pub.publish(cmd)
        self.lastTime = self.get_clock().now()

    def watchdog_callback(self):
        if self.lastTime is None:
            self.publish_stop()
            return

        age = self.get_clock().now() - self.lastTime
        if age.nanoseconds / 1e9 > self.timeout:
            self.lastTime = None
            self.publish_stop()

    def publish_stop(self):
        self.pub.publish(Twist())


def main(args=None):
    rclpy.init(args=args)
    node = VelocityController()
    try:
        rclpy.spin(node)
    finally:
        node.publish_stop()
        node.destroy_node()
        rclpy.shutdown()


if __name__ == "__main__":
    main()
