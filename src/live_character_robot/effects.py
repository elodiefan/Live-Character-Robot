"""Locally synthesized character sound effects and short music cues."""

from __future__ import annotations

from collections.abc import Sequence

import numpy as np
import sounddevice as sd
from numpy.typing import NDArray

from live_character_robot.audio import SAMPLE_RATE


def synthesize_tones(
    notes: Sequence[tuple[float, float]],
    *,
    volume: float = 0.22,
) -> NDArray[np.int16]:
    """Synthesize an enveloped monophonic sequence as signed 16-bit audio."""
    chunks = []
    for frequency, duration in notes:
        frame_count = round(duration * SAMPLE_RATE)
        time_axis = np.arange(frame_count, dtype=np.float64) / SAMPLE_RATE
        envelope = np.sin(np.linspace(0.0, np.pi, frame_count)) ** 2
        wave = np.sin(2.0 * np.pi * frequency * time_axis) * envelope
        chunks.append(wave)
    signal = np.concatenate(chunks) if chunks else np.zeros(0, dtype=np.float64)
    return np.asarray(signal * volume * np.iinfo(np.int16).max, dtype=np.int16)


def acknowledgment_sound() -> NDArray[np.int16]:
    """Return a short rising two-note object-memory acknowledgment."""
    return synthesize_tones(((660.0, 0.10), (880.0, 0.14)))


def success_music() -> NDArray[np.int16]:
    """Return a brief three-note musical goal-completion cue."""
    return synthesize_tones(((523.25, 0.16), (659.25, 0.16), (783.99, 0.28)))


def start_audio(samples: NDArray[np.int16]) -> None:
    """Start local audio playback without blocking simultaneous animation."""
    sd.play(samples, samplerate=SAMPLE_RATE)


def wait_for_audio() -> None:
    """Wait for the current local sound effect or music cue to finish."""
    sd.wait()
