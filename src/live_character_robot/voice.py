"""Offline operating-system voice output for character responses."""

from __future__ import annotations

import shutil
import subprocess

MOTION_RESPONSES: dict[str, str] = {
    "look-up": "Looking up.",
    "nod": "Hello there.",
    "shake": "No.",
    "sleep": "Good night.",
}


def speech_command(text: str) -> list[str]:
    """Return a safe argument list for an available offline speech engine."""
    if say_path := shutil.which("say"):
        return [say_path, text]
    if espeak_path := shutil.which("espeak-ng") or shutil.which("espeak"):
        return [espeak_path, text]
    raise RuntimeError(
        "No offline speech engine found. Install espeak-ng on Ubuntu."
    )


def start_speech(text: str) -> subprocess.Popen[bytes]:
    """Begin speaking without blocking the lamp's simultaneous motion."""
    return subprocess.Popen(  # noqa: S603 - executable path comes from shutil.which
        speech_command(text),
        stdout=subprocess.DEVNULL,
        stderr=subprocess.DEVNULL,
    )
