"""Safe, deterministic pose generation for expressive lamp motion."""

from __future__ import annotations

from collections.abc import Iterator, Mapping, Sequence

import numpy as np
from numpy.typing import NDArray

from live_character_robot.simulator import JointSpec

Pose = Mapping[str, float]

REST_POSE: Pose = {
    "base_yaw_joint": 0.0,
    "shoulder_pitch_joint": 0.35,
    "elbow_pitch_joint": -1.0,
    "neck_yaw_joint": 0.0,
    "head_pitch_joint": -0.1,
}

NOD_POSES: tuple[Pose, ...] = (
    REST_POSE,
    {**REST_POSE, "head_pitch_joint": 0.35},
    {**REST_POSE, "head_pitch_joint": -0.3},
    REST_POSE,
)

SHAKE_POSES: tuple[Pose, ...] = (
    REST_POSE,
    {**REST_POSE, "neck_yaw_joint": 0.65},
    {**REST_POSE, "neck_yaw_joint": -0.65},
    {**REST_POSE, "neck_yaw_joint": 0.45},
    {**REST_POSE, "neck_yaw_joint": -0.45},
    REST_POSE,
)

LOOK_UP_POSES: tuple[Pose, ...] = (
    REST_POSE,
    {**REST_POSE, "head_pitch_joint": -0.55},
)

SLEEP_POSES: tuple[Pose, ...] = (
    REST_POSE,
    {
        **REST_POSE,
        "shoulder_pitch_joint": -0.25,
        "elbow_pitch_joint": -1.55,
        "head_pitch_joint": -0.65,
    },
)

MOTIONS: dict[str, tuple[Pose, ...]] = {
    "look-up": LOOK_UP_POSES,
    "nod": NOD_POSES,
    "shake": SHAKE_POSES,
    "sleep": SLEEP_POSES,
}


def pose_vector(pose: Pose, specs: Sequence[JointSpec]) -> NDArray[np.float64]:
    """Convert a named pose to an ordered vector, clamped to safe joint limits."""
    return np.asarray(
        [np.clip(pose.get(spec.name, 0.0), spec.lower, spec.upper) for spec in specs],
        dtype=np.float64,
    )


def smooth_transition(
    start: NDArray[np.float64],
    target: NDArray[np.float64],
    frame_count: int,
) -> Iterator[NDArray[np.float64]]:
    """Yield a smoothstep trajectory between two joint vectors."""
    if frame_count < 2:
        raise ValueError("A transition needs at least two frames")
    for progress in np.linspace(0.0, 1.0, frame_count):
        eased = progress * progress * (3.0 - 2.0 * progress)
        yield start + (target - start) * eased
