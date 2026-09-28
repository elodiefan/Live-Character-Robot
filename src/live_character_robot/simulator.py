"""MuJoCo loading and inspection for the supplied lamp robot."""

from __future__ import annotations

import time
from collections.abc import Sequence
from dataclasses import dataclass
from pathlib import Path

import mujoco
import mujoco.viewer
import numpy as np
from numpy.typing import NDArray

ROBOT_URDF = Path(__file__).resolve().parents[2] / "robot" / "dummy_lamp_5dof.urdf"


@dataclass(frozen=True)
class JointSpec:
    """A controllable joint and its safe position range in radians."""

    name: str
    lower: float
    upper: float


def load_robot_model(urdf_path: Path = ROBOT_URDF) -> mujoco.MjModel:
    """Load the lamp URDF as a MuJoCo model."""
    if not urdf_path.is_file():
        raise FileNotFoundError(f"Robot URDF not found: {urdf_path}")
    return mujoco.MjModel.from_xml_path(str(urdf_path))


def joint_specs(model: mujoco.MjModel) -> tuple[JointSpec, ...]:
    """Return ordered joint names and imported position limits."""
    specs = []
    for joint_id in range(model.njnt):
        name = mujoco.mj_id2name(model, mujoco.mjtObj.mjOBJ_JOINT, joint_id)
        lower, upper = model.jnt_range[joint_id]
        specs.append(JointSpec(name=name, lower=float(lower), upper=float(upper)))
    return tuple(specs)


def launch_simulator(model: mujoco.MjModel) -> None:
    """Open MuJoCo's interactive viewer for the lamp model."""
    data = mujoco.MjData(model)
    mujoco.mj_forward(model, data)
    mujoco.viewer.launch(model, data)


def animate_poses(
    model: mujoco.MjModel,
    poses: Sequence[NDArray[np.float64]],
    *,
    frames_per_transition: int = 36,
    frames_per_second: float = 60.0,
) -> None:
    """Animate pose targets until the viewer is closed."""
    from live_character_robot.motion import smooth_transition

    if len(poses) < 2:
        raise ValueError("An animation needs at least two poses")

    data = mujoco.MjData(model)
    data.qpos[:] = poses[0]
    mujoco.mj_forward(model, data)
    frame_period = 1.0 / frames_per_second

    with mujoco.viewer.launch_passive(model, data) as viewer:
        while viewer.is_running():
            for target in poses[1:]:
                start = data.qpos.copy()
                for frame in smooth_transition(start, target, frames_per_transition):
                    if not viewer.is_running():
                        return
                    frame_start = time.monotonic()
                    data.qpos[:] = frame
                    mujoco.mj_forward(model, data)
                    viewer.sync()
                    remaining = frame_period - (time.monotonic() - frame_start)
                    if remaining > 0:
                        time.sleep(remaining)
