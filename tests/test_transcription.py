"""Tests for bounded local transcription."""

from types import SimpleNamespace

import pytest

from live_character_robot.transcription import transcribe_file


class FakeModel:
    """Capture transcription arguments without loading a model."""

    def __init__(self, texts=("  hello ", " lamp  ")) -> None:
        self.texts = texts
        self.audio_path = None
        self.options = None

    def transcribe(self, audio_path, **options):
        self.audio_path = audio_path
        self.options = options
        return (SimpleNamespace(text=text) for text in self.texts), SimpleNamespace()


def test_transcribe_file_runs_local_model_with_cpu_friendly_options(tmp_path) -> None:
    """A bounded file should use deterministic local transcription options."""
    audio_path = tmp_path / "speech.wav"
    audio_path.write_bytes(b"test audio")
    model = FakeModel()

    transcript = transcribe_file(audio_path, model=model)

    assert transcript == "hello lamp"
    assert model.audio_path == str(audio_path)
    assert model.options == {"beam_size": 1, "language": "en", "vad_filter": True}


def test_transcribe_file_rejects_missing_input(tmp_path) -> None:
    """A missing recording should fail before making an API request."""
    with pytest.raises(FileNotFoundError, match="Audio file not found"):
        transcribe_file(tmp_path / "missing.wav", model=FakeModel())


def test_transcribe_file_rejects_empty_result(tmp_path) -> None:
    """An empty provider result should not be treated as understood speech."""
    audio_path = tmp_path / "silence.wav"
    audio_path.write_bytes(b"test audio")

    with pytest.raises(RuntimeError, match="no text"):
        transcribe_file(audio_path, model=FakeModel(("  ",)))
