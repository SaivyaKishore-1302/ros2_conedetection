import math

import cv2
import numpy as np

from cone_navigator.cone_detector import analyse_cone


def test_analysis_uses_boundary_centroid():
    mask = np.zeros((100, 100), dtype=np.uint8)
    points = np.array([[10, 10], [20, 10], [80, 90], [70, 90]])
    cv2.fillPoly(mask, [points], 255)

    detection = analyse_cone(mask, 30.0, 20.0)

    assert detection is not None
    assert 43 <= detection[0] <= 47
    assert math.isfinite(detection[1])


def test_analysis_rejects_small_regions():
    mask = np.zeros((100, 100), dtype=np.uint8)
    mask[10:12, 10:12] = 255

    assert analyse_cone(mask, 30.0, 20.0) is None
