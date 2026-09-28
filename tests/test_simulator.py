"""Tests for loading the supplied lamp model."""

import pytest

from live_character_robot.simulator import joint_specs, load_robot_model

EXPECTED_JOINTS = (
    ("base_yaw_joint", -2.6, 2.6),
    ("shoulder_pitch_joint", -0.75, 1.05),
    ("elbow_pitch_joint", -1.85, 0.4),
    ("neck_yaw_joint", -1.35, 1.35),
    ("head_pitch_joint", -0.9, 0.7),
)


def test_supplied_urdf_loads_with_expected_joint_limits() -> None:
    """MuJoCo should preserve all five named joints and their safe ranges."""
    specs = joint_specs(load_robot_model())

    assert len(specs) == 5
    for spec, (name, lower, upper) in zip(specs, EXPECTED_JOINTS, strict=True):
        assert spec.name == name
        assert spec.lower == pytest.approx(lower)
        assert spec.upper == pytest.approx(upper)
