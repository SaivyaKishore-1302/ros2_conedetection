import math

from geometry_msgs.msg import Twist
import rclpy
from rclpy.node import Node
from rclpy.signals import SignalHandlerOptions
from std_msgs.msg import Float32

from cone_interfaces.msg import ConeArray


def calculate_angular_velocity(cte, kp, maxSpeed, deadband=0.0):
    if not math.isfinite(cte):
        return None

    if abs(cte) <= deadband:
        return 0.0

    turn = -kp * cte
    return max(-maxSpeed, min(maxSpeed, turn))


def calculate_forward_velocity(
    turn,
    coneDistance,
    cruiseSpeed,
    minSpeed,
    brakingTurnRate,
    brakingDistance,
):
    turnRatio = (
        min(1.0, abs(turn) / brakingTurnRate)
        if brakingTurnRate > 0.0
        else 1.0
    )
    if math.isfinite(coneDistance) and brakingDistance > 0.0:
        proximity = max(
            0.0,
            min(1.0, (brakingDistance - coneDistance) / brakingDistance),
        )
    else:
        proximity = 0.5
    braking = min(1.0, turnRatio * (0.45 + proximity))
    speed = cruiseSpeed - (cruiseSpeed - minSpeed) * braking
    return max(minSpeed, min(cruiseSpeed, speed))


class VelocityController(Node):
    def __init__(self):
        super().__init__("velocity_controller")

        self.declare_parameter("forward_speed", 0.30)
        self.declare_parameter("minimum_forward_speed", 0.10)
        self.declare_parameter("braking_distance", 0.40)
        self.declare_parameter("braking_turn_rate", 0.65)
        self.declare_parameter("kp", 0.012)
        self.declare_parameter("max_angular_speed", 0.9)
        self.declare_parameter("steering_smoothing", 0.30)
        self.declare_parameter("steering_deadband", 4.0)
        self.declare_parameter("command_timeout", 0.8)

        self.speed = self.get_parameter("forward_speed").value
        self.minSpeed = self.get_parameter("minimum_forward_speed").value
        self.brakingDistance = self.get_parameter("braking_distance").value
        self.brakingTurnRate = self.get_parameter("braking_turn_rate").value
        self.kp = self.get_parameter("kp").value
        self.maxSpeed = self.get_parameter("max_angular_speed").value
        self.smoothing = self.get_parameter("steering_smoothing").value
        self.deadband = self.get_parameter("steering_deadband").value
        self.timeout = self.get_parameter("command_timeout").value
        self.lastTime = None
        self.orangeDistance = math.inf
        self.blueDistance = math.inf
        self.nearestDistance = math.inf
        self.turn = 0.0

        self.pub = self.create_publisher(Twist, "/cmd_vel", 10)
        self.sub = self.create_subscription(
            Float32,
            "/track_planner/cte",
            self.cte_callback,
            10,
        )
        self.coneSub = self.create_subscription(
            ConeArray,
            "/cone_detector/cones",
            self.coneCallback,
            10,
        )
        self.timer = self.create_timer(0.1, self.watchdog_callback)

    def coneCallback(self, msg):
        distance = msg.distance
        if not math.isfinite(distance) or distance <= 0.0:
            distance = math.inf
        if msg.colour == "orange":
            self.orangeDistance = distance
        elif msg.colour == "blue":
            self.blueDistance = distance
        self.nearestDistance = min(self.orangeDistance, self.blueDistance)

    def cte_callback(self, msg):
        requestedTurn = calculate_angular_velocity(
            msg.data, self.kp, self.maxSpeed, self.deadband
        )
        if requestedTurn is None:
            if self.lastTime is None:
                self.publish_stop()
            return

        blend = max(0.0, min(1.0, self.smoothing))
        self.turn += blend * (requestedTurn - self.turn)
        turn = self.turn

        cmd = Twist()
        cmd.linear.x = float(calculate_forward_velocity(
            turn,
            self.nearestDistance,
            self.speed,
            self.minSpeed,
            self.brakingTurnRate,
            self.brakingDistance,
        ))
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
        self.turn = 0.0
        self.pub.publish(Twist())


def main(args=None):
    rclpy.init(args=args, signal_handler_options=SignalHandlerOptions.NO)
    node = VelocityController()
    try:
        rclpy.spin(node)
    except KeyboardInterrupt:
        pass
    finally:
        node.publish_stop()
        node.destroy_node()
        rclpy.shutdown()


if __name__ == "__main__":
    main()
