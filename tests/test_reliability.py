"""Tests for recoverable local component failures."""

from pathlib import Path

import pytest

from live_character_robot import reliability


def test_silence_does_not_terminate_session(
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    """An empty transcription should skip one turn with a useful message."""
    def fail(_path: Path) -> str:
        raise RuntimeError("Transcription returned no text")

    monkeypatch.setattr(reliability, "transcribe_file", fail)

    assert reliability.transcribe_safely(Path("silence.wav")) is None
    assert "Transcription unavailable for this turn" in capsys.readouterr().out


def test_camera_failure_returns_no_observation(
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    """A disconnected camera should not crash the interaction controller."""
    def fail() -> None:
        raise RuntimeError("camera disconnected")

    monkeypatch.setattr(reliability, "capture_camera_frame", fail)

    assert reliability.observe_safely() is None
    assert "Camera observation unavailable" in capsys.readouterr().out


def test_missing_voice_returns_none(
    monkeypatch: pytest.MonkeyPatch,
    capsys: pytest.CaptureFixture[str],
) -> None:
    """Motion should remain available without an operating-system voice."""
    def fail(_text: str) -> None:
        raise RuntimeError("no speech engine")

    monkeypatch.setattr(reliability, "start_speech", fail)

    assert reliability.start_speech_safely("Hello") is None
    assert "Voice output unavailable" in capsys.readouterr().out
