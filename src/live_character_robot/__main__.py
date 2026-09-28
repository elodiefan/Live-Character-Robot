"""Allow the application to run with ``python -m live_character_robot``."""

from live_character_robot.cli import main


if __name__ == "__main__":
    raise SystemExit(main())
