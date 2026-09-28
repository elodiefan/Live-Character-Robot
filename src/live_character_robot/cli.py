"""Command-line entry point for the Live Character Robot application."""

from __future__ import annotations

import argparse
from collections.abc import Sequence

from live_character_robot import __version__


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
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    """Run the application command."""
    parser = build_parser()
    parser.parse_args(argv)
    print("Live Character Robot scaffold is ready.")
    return 0
