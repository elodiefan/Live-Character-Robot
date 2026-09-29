"""Tests for deterministic spoken-command interpretation."""

import pytest

from live_character_robot.voice_commands import resolve_voice_command


@pytest.mark.parametrize(
    ("transcript", "expected"),
    (
        ("Hello there!", "nod"),
        ("Could you say yes?", "nod"),
        ("No, please.", "shake"),
        ("Please look up now.", "look-up"),
        ("Okay, go to sleep.", "sleep"),
    ),
)
def test_resolve_voice_command(transcript: str, expected: str) -> None:
    """Known phrases should resolve despite casing and punctuation."""
    assert resolve_voice_command(transcript) == expected


@pytest.mark.parametrize("transcript", ("snow", "I know", "dance for me", ""))
def test_resolve_voice_command_ignores_unknown_speech(transcript: str) -> None:
    """Unknown phrases and words containing 'no' must not trigger motion."""
    assert resolve_voice_command(transcript) is None
