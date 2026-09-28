"""Command-line entry point for the Live Character Robot application."""

from __future__ import annotations

import argparse
from collections.abc import Sequence

from live_character_robot import __version__
from live_character_robot.camera import run_engagement_camera
from live_character_robot.motion import NOD_POSES, pose_vector
from live_character_robot.simulator import (
    animate_poses,
    joint_specs,
    launch_simulator,
    load_robot_model,
)


def build_parser() -> argparse.ArgumentParser:
    """Build the application argument parser."""
    parser = argparse.ArgumentParser(
        prog="live-character-robot",
        description="Run the Live Character Robot application.",
    )
    parser.add_argument(
        "--version",
        action="version",
        version=f"%(prog)s {__version__}",
    )
    subparsers = parser.add_subparsers(dest="command")
    subparsers.add_parser("inspect-model", help="Print the imported robot joints and limits.")
    subparsers.add_parser("simulate", help="Open the robot in the MuJoCo viewer.")
    animate_parser = subparsers.add_parser("animate", help="Play an expressive motion.")
    animate_parser.add_argument("motion", choices=("nod",))
    camera_parser = subparsers.add_parser(
        "camera", help="Preview frontal-face engagement detection."
    )
    camera_parser.add_argument(
        "--index",
        type=int,
        default=0,
        help="Camera device index (default: 0).",
    )
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    """Run the application command."""
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.command == "inspect-model":
        model = load_robot_model()
        print(f"Loaded lamp model with {model.njnt} joints:")
        for joint in joint_specs(model):
            print(f"- {joint.name}: [{joint.lower:.3f}, {joint.upper:.3f}] rad")
        return 0

    if args.command == "simulate":
        launch_simulator(load_robot_model())
        return 0

    if args.command == "animate":
        model = load_robot_model()
        specs = joint_specs(model)
        poses = tuple(pose_vector(pose, specs) for pose in NOD_POSES)
        animate_poses(model, poses)
        return 0

    if args.command == "camera":
        run_engagement_camera(args.index)
        return 0

    print("Live Character Robot scaffold is ready.")
    return 0
