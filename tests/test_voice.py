"""Tests for offline operating-system voice output."""

from unittest.mock import Mock

import pytest

from live_character_robot import voice


def test_speech_command_prefers_macos_say(monkeypatch: pytest.MonkeyPatch) -> None:
    """The built-in macOS voice should be selected when available."""
    monkeypatch.setattr(
        voice.shutil,
        "which",
        lambda name: "/usr/bin/say" if name == "say" else None,
    )

    assert voice.speech_command("Hello") == ["/usr/bin/say", "Hello"]


def test_speech_command_uses_espeak_ng(monkeypatch: pytest.MonkeyPatch) -> None:
    """Ubuntu should use the local espeak-ng executable."""
    paths = {"espeak-ng": "/usr/bin/espeak-ng"}
    monkeypatch.setattr(voice.shutil, "which", paths.get)

    assert voice.speech_command("Hello") == ["/usr/bin/espeak-ng", "Hello"]


def test_speech_command_reports_missing_engine(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    """A missing local engine should produce an actionable error."""
    monkeypatch.setattr(voice.shutil, "which", lambda _name: None)

    with pytest.raises(RuntimeError, match="espeak-ng"):
        voice.speech_command("Hello")


def test_start_speech_launches_without_shell(monkeypatch: pytest.MonkeyPatch) -> None:
    """Speech text should be passed as an argument, never through a shell."""
    process = Mock()
    popen = Mock(return_value=process)
    monkeypatch.setattr(voice, "speech_command", lambda text: ["/usr/bin/say", text])
    monkeypatch.setattr(voice.subprocess, "Popen", popen)

    assert voice.start_speech("Hello") is process
    popen.assert_called_once_with(
        ["/usr/bin/say", "Hello"],
        stdout=voice.subprocess.DEVNULL,
        stderr=voice.subprocess.DEVNULL,
    )
