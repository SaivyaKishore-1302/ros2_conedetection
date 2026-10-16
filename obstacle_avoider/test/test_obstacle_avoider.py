import math
from types import SimpleNamespace

from obstacle_avoider.obstacle_avoider import calculateCommand
from obstacle_avoider.obstacle_avoider import nearestObstacles


def test_nearest_obstacles_supports_negative_scan_angles():
    scan = SimpleNamespace(
        angle_min=math.radians(-90.0),
        angle_increment=math.radians(45.0),
        ranges=[0.8, 0.7, 0.4, 0.9, 1.0],
        range_min=0.1,
        range_max=5.0,
    )

    assert nearestObstacles(scan) == (0.4, 0.9, 0.7)


def test_nearest_obstacles_ignores_invalid_ranges():
    scan = SimpleNamespace(
        angle_min=0.0,
        angle_increment=0.1,
        ranges=[math.nan, math.inf, 0.01],
        range_min=0.1,
        range_max=5.0,
    )

    assert nearestObstacles(scan) == (math.inf, math.inf, math.inf)


def test_command_drives_forward_when_path_is_clear():
    assert calculateCommand(1.0, 0.8, 0.7, 0.5, 0.2, 0.5) == (0.2, 0.0)


def test_command_turns_toward_more_open_space():
    assert calculateCommand(0.3, 0.9, 0.4, 0.5, 0.2, 0.5) == (0.0, 0.5)
    assert calculateCommand(0.3, 0.4, 0.9, 0.5, 0.2, 0.5) == (0.0, -0.5)
