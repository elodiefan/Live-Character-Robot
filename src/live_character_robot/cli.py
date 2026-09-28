"""Command-line entry point for the Live Character Robot application."""

from __future__ import annotations

import argparse
from collections.abc import Sequence

from live_character_robot import __version__
from live_character_robot.simulator import joint_specs, launch_simulator, load_robot_model


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

    print("Live Character Robot scaffold is ready.")
    return 0
