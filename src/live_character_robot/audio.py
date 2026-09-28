"""Local microphone capture and speaker playback."""

from __future__ import annotations

import wave
from pathlib import Path

import numpy as np
import sounddevice as sd
from numpy.typing import NDArray

SAMPLE_RATE = 16_000
CHANNELS = 1


def write_wav(
    path: Path,
    samples: NDArray[np.int16],
    *,
    sample_rate: int = SAMPLE_RATE,
) -> None:
    """Write mono signed 16-bit samples to a PCM WAV file."""
    path.parent.mkdir(parents=True, exist_ok=True)
    with wave.open(str(path), "wb") as wav_file:
        wav_file.setnchannels(CHANNELS)
        wav_file.setsampwidth(np.dtype(np.int16).itemsize)
        wav_file.setframerate(sample_rate)
        wav_file.writeframes(np.asarray(samples, dtype=np.int16).tobytes())


def record_microphone(
    duration_seconds: float,
    *,
    sample_rate: int = SAMPLE_RATE,
    device: int | str | None = None,
) -> NDArray[np.int16]:
    """Record a bounded mono clip from the selected input device."""
    if duration_seconds <= 0:
        raise ValueError("Recording duration must be positive")
    frame_count = round(duration_seconds * sample_rate)
    recording = sd.rec(
        frame_count,
        samplerate=sample_rate,
        channels=CHANNELS,
        dtype="int16",
        device=device,
    )
    sd.wait()
    return recording.reshape(-1)


def play_audio(samples: NDArray[np.int16], *, sample_rate: int = SAMPLE_RATE) -> None:
    """Play a mono sample array through the default speaker."""
    sd.play(samples, samplerate=sample_rate)
    sd.wait()


def describe_audio_devices() -> str:
    """Return PortAudio's available input and output device table."""
    return str(sd.query_devices())
