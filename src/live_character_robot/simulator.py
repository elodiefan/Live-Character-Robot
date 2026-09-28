"""MuJoCo loading and inspection for the supplied lamp robot."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

import mujoco
import mujoco.viewer

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
