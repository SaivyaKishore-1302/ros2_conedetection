import numpy as np

from lane_follower.follower_node import calculateAngularVelocity
from lane_follower.follower_node import calculateTarget
from lane_follower.follower_node import maskCentroid


def test_mask_centroid_returns_none_for_empty_mask():
    assert maskCentroid(np.zeros((4, 4), dtype=np.uint8)) is None


def test_mask_centroid_finds_horizontal_centre():
    mask = np.zeros((3, 5), dtype=np.uint8)
    mask[:, 3] = 255
    assert maskCentroid(mask) == 3.0


def test_target_uses_both_lane_boundaries():
    assert calculateTarget(80.0, 240.0, 320, 80.0) == 160.0


def test_target_uses_single_visible_boundary():
    assert calculateTarget(70.0, None, 320, 80.0) == 150.0
    assert calculateTarget(None, 250.0, 320, 80.0) == 170.0


def test_target_is_missing_without_lane_boundaries():
    assert calculateTarget(None, None, 320, 80.0) is None


def test_angular_velocity_is_clamped():
    assert calculateAngularVelocity(320.0, 320, 0.01, 0.5) == 0.5
    assert calculateAngularVelocity(0.0, 320, 0.01, 0.5) == -0.5
