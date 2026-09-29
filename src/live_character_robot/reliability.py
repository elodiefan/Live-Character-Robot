"""Recovery boundaries for optional local perception and output components."""

from __future__ import annotations

import subprocess
from pathlib import Path

import numpy as np
import sounddevice as sd
from numpy.typing import NDArray

from live_character_robot.effects import start_audio, wait_for_audio
from live_character_robot.scene import (
    ObjectObservation,
    capture_camera_frame,
    observe_colored_object,
)
from live_character_robot.transcription import transcribe_file
from live_character_robot.voice import start_speech


def transcribe_safely(audio_path: Path) -> str | None:
    """Return no transcript for silence or a recoverable local model failure."""
    try:
        return transcribe_file(audio_path)
    except (FileNotFoundError, OSError, RuntimeError) as error:
        print(f"Transcription unavailable for this turn: {error}")
        return None


def observe_safely(
    *,
    center_only: bool = True,
    target_color: str | None = None,
) -> ObjectObservation | None:
    """Return no observation when the local camera cannot provide a frame."""
    try:
        return observe_colored_object(
            capture_camera_frame(),
            center_only=center_only,
            target_color=target_color,
        )
    except (OSError, RuntimeError) as error:
        print(f"Camera observation unavailable: {error}")
        return None


def start_speech_safely(text: str) -> subprocess.Popen[bytes] | None:
    """Allow visual behavior to continue when no speech engine is available."""
    try:
        return start_speech(text)
    except (OSError, RuntimeError) as error:
        print(f"Voice output unavailable: {error}")
        return None


def wait_for_speech(process: subprocess.Popen[bytes] | None) -> None:
    """Wait for speech when it started, tolerating an output process failure."""
    if process is None:
        return
    try:
        process.wait()
    except OSError as error:
        print(f"Voice output ended unexpectedly: {error}")


def play_audio_safely(samples: NDArray[np.int16]) -> None:
    """Play a local cue when possible without terminating character behavior."""
    started = start_audio_safely(samples)
    wait_for_audio_safely(started)


def start_audio_safely(samples: NDArray[np.int16]) -> bool:
    """Start a local cue and report whether playback began."""
    try:
        start_audio(samples)
        return True
    except (OSError, RuntimeError, sd.PortAudioError) as error:
        print(f"Character audio unavailable: {error}")
        return False


def wait_for_audio_safely(started: bool) -> None:
    """Wait for local audio only when playback started successfully."""
    if not started:
        return
    try:
        wait_for_audio()
    except (OSError, RuntimeError, sd.PortAudioError) as error:
        print(f"Character audio unavailable: {error}")
