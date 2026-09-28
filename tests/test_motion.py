"""Tests for safe expressive motion generation."""

import numpy as np
import pytest

from live_character_robot.motion import pose_vector, smooth_transition
from live_character_robot.simulator import JointSpec

SPECS = (
    JointSpec("first", -1.0, 1.0),
    JointSpec("second", -0.5, 0.5),
)


def test_pose_vector_uses_joint_order_and_clamps_limits() -> None:
    """Unsafe requested positions should never reach the simulator."""
    vector = pose_vector({"first": 3.0, "second": -2.0}, SPECS)

    assert vector == pytest.approx([1.0, -0.5])


def test_smooth_transition_includes_exact_endpoints() -> None:
    """A generated trajectory should begin and end at its requested poses."""
    start = np.asarray([0.0, -0.5])
    target = np.asarray([1.0, 0.5])

    frames = tuple(smooth_transition(start, target, frame_count=5))

    assert frames[0] == pytest.approx(start)
    assert frames[-1] == pytest.approx(target)
    assert len(frames) == 5


def test_smooth_transition_rejects_single_frame() -> None:
    """An interpolation needs enough frames to represent both endpoints."""
    with pytest.raises(ValueError, match="at least two"):
        tuple(smooth_transition(np.zeros(1), np.ones(1), frame_count=1))
