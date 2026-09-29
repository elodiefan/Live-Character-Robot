"""Tests for deterministic spoken-command interpretation."""

import pytest

from live_character_robot.voice_commands import (
    resolve_scene_command,
    resolve_voice_command,
)


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


@pytest.mark.parametrize(
    ("transcript", "expected"),
    (
        ("Please remember this object.", "remember-object"),
        ("What color was the object?", "recall-color"),
        ("What was the color of the object?", "recall-color"),
        ("What color was it?", "recall-color"),
        ("What's the color of it?", "recall-color"),
        ("What is the color?", "recall-color"),
    ),
)
def test_resolve_scene_command(transcript: str, expected: str) -> None:
    """Scene-memory phrases should resolve to bounded memory operations."""
    assert resolve_scene_command(transcript) == expected
