"""Map bounded speech transcripts to safe, predefined lamp motions."""

from __future__ import annotations

import re

COMMAND_PHRASES: tuple[tuple[str, tuple[str, ...]], ...] = (
    ("sleep", ("go to sleep", "good night", "sleep")),
    ("look-up", ("look up", "look at the ceiling")),
    ("shake", ("shake your head", "say no", "no")),
    ("nod", ("nod your head", "say yes", "hello", "hi", "yes")),
)


def resolve_voice_command(transcript: str) -> str | None:
    """Return the motion associated with a recognized phrase, if any."""
    normalized = " ".join(re.findall(r"[a-z]+", transcript.lower()))
    padded = f" {normalized} "
    for motion, phrases in COMMAND_PHRASES:
        if any(f" {phrase} " in padded for phrase in phrases):
            return motion
    return None
