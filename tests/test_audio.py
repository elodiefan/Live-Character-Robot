"""Tests for local audio utilities."""

import wave

import numpy as np
import pytest

from live_character_robot.audio import record_microphone, write_wav


def test_write_wav_creates_mono_pcm_file(tmp_path) -> None:
    """Recorded samples should be stored in the transcription-ready format."""
    output = tmp_path / "clip.wav"
    samples = np.asarray([-1000, 0, 1000], dtype=np.int16)

    write_wav(output, samples, sample_rate=16_000)

    with wave.open(str(output), "rb") as wav_file:
        assert wav_file.getnchannels() == 1
        assert wav_file.getsampwidth() == 2
        assert wav_file.getframerate() == 16_000
        assert wav_file.getnframes() == 3


def test_recording_duration_must_be_positive() -> None:
    """Invalid durations should fail before opening the microphone."""
    with pytest.raises(ValueError, match="positive"):
        record_microphone(0)
