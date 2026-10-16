import math

from cone_navigator.velocity_controller import calculate_angular_velocity
from cone_navigator.velocity_controller import calculate_forward_velocity


def test_angular_velocity_rejects_invalid_cte():
    assert calculate_angular_velocity(math.nan, 0.012, 1.5) is None


def test_angular_velocity_is_clamped():
    assert calculate_angular_velocity(-200.0, 0.012, 1.5) == 1.5
    assert calculate_angular_velocity(200.0, 0.012, 1.5) == -1.5


def test_angular_velocity_uses_deadband():
    assert calculate_angular_velocity(3.0, 0.012, 1.5, 4.0) == 0.0


def test_forward_velocity_uses_cruise_speed_on_straight():
    speed = calculate_forward_velocity(0.0, 0.2, 0.30, 0.10, 0.65, 0.4)
    assert speed == 0.30


def test_forward_velocity_brakes_more_near_cones():
    nearSpeed = calculate_forward_velocity(0.5, 0.15, 0.30, 0.10, 0.65, 0.4)
    farSpeed = calculate_forward_velocity(0.5, 0.50, 0.30, 0.10, 0.65, 0.4)
    assert 0.10 <= nearSpeed < farSpeed < 0.30


def test_forward_velocity_respects_minimum():
    speed = calculate_forward_velocity(1.5, 0.0, 0.30, 0.10, 0.65, 0.4)
    assert speed == 0.10
