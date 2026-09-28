"""Local CPU speech transcription for bounded audio clips."""

from __future__ import annotations

from functools import lru_cache
from pathlib import Path
from typing import Any

from faster_whisper import WhisperModel

TRANSCRIPTION_MODEL = "base.en"


@lru_cache(maxsize=1)
def load_transcription_model() -> WhisperModel:
    """Load and cache the CPU-optimized English transcription model."""
    return WhisperModel(TRANSCRIPTION_MODEL, device="cpu", compute_type="int8")


def transcribe_file(audio_path: Path, *, model: Any | None = None) -> str:
    """Transcribe a completed audio file locally and return normalized text."""
    if not audio_path.is_file():
        raise FileNotFoundError(f"Audio file not found: {audio_path}")
    active_model = model or load_transcription_model()
    segments, _ = active_model.transcribe(
        str(audio_path),
        beam_size=1,
        language="en",
        vad_filter=True,
    )
    text = " ".join(segment.text.strip() for segment in segments).strip()
    if not text:
        raise RuntimeError("Transcription returned no text")
    return text
