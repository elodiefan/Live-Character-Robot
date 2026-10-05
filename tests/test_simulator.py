"""Tests for loading and rendering the supplied lamp model."""

from typing import Any

import mujoco
import numpy as np
import pytest

from live_character_robot.simulator import (
    animate_targets,
    joint_specs,
    load_robot_model,
)

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


def test_light_pulse_renders_restored_shade_color() -> None:
    """The final visible frame should not remain on the yellow pulse color."""
    model = load_robot_model()
    data = mujoco.MjData(model)
    shade_geom_id = model.ngeom - 1
    original_color = model.geom_rgba[shade_geom_id].copy()

    class RecordingViewer:
        def __init__(self) -> None:
            self.rendered_colors: list[np.ndarray[Any, Any]] = []

        def is_running(self) -> bool:
            return True

        def sync(self) -> None:
            self.rendered_colors.append(model.geom_rgba[shade_geom_id].copy())

    viewer = RecordingViewer()
    target = data.qpos.copy()

    assert animate_targets(
        model,
        data,
        viewer,
        (target,),
        frames_per_transition=3,
        frames_per_second=100_000.0,
        light_pulse=True,
    )
    assert viewer.rendered_colors[-1] == pytest.approx(original_color)
