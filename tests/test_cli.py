"""Tests for the application command-line interface."""

from live_character_robot.cli import main


def test_main_reports_ready(capsys) -> None:
    """The initial command should confirm that the scaffold can run."""
    exit_code = main([])

    assert exit_code == 0
    assert capsys.readouterr().out == "Live Character Robot scaffold is ready.\n"
