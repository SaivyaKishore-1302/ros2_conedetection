import math

from cone_navigator.velocity_controller import calculate_angular_velocity
from cone_navigator.velocity_controller import calculate_forward_velocity


def test_angular_velocity_rejects_invalid_cte():
    assert calculate_angular_velocity(math.nan, 0.012, 1.5) is None


def test_angular_velocity_is_clamped():
    assert calculate_angular_velocity(-200.0, 0.012, 1.5) == 1.5
    assert calculate_angular_velocity(200.0, 0.012, 1.5) == -1.5


def test_forward_velocity_uses_cruise_speed_on_straight():
    assert calculate_forward_velocity(0.0, 0.10, 0.04, 3.0) == 0.10


def test_forward_velocity_slows_for_turns():
    speed = calculate_forward_velocity(0.5, 0.10, 0.04, 3.0)
    assert 0.04 <= speed < 0.10


def test_forward_velocity_respects_minimum():
    assert calculate_forward_velocity(1.5, 0.10, 0.04, 3.0) == 0.04
