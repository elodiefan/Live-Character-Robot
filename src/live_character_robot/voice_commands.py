"""Map bounded speech transcripts to safe, predefined lamp motions."""

from __future__ import annotations

import re

COMMAND_PHRASES: tuple[tuple[str, tuple[str, ...]], ...] = (
    ("sleep", ("go to sleep", "good night", "sleep")),
    ("look-up", ("look up", "look at the ceiling")),
    ("shake", ("shake your head", "say no", "no")),
    ("nod", ("nod your head", "say yes", "hello", "hi", "yes")),
)

SCENE_COMMAND_PHRASES: tuple[tuple[str, tuple[str, ...]], ...] = (
    ("remember-object", ("remember this object", "remember the object")),
    (
        "recall-color",
        (
            "what color was the object",
            "what was the color of the object",
            "what color is the object",
            "what color was it",
            "what is the color of it",
            "what is the color",
        ),
    ),
)

FAREWELL_PHRASES = ("goodbye", "good bye", "bye bye", "bye")


def resolve_voice_command(transcript: str) -> str | None:
    """Return the motion associated with a recognized phrase, if any."""
    normalized = " ".join(re.findall(r"[a-z]+", transcript.lower()))
    padded = f" {normalized} "
    for motion, phrases in COMMAND_PHRASES:
        if any(f" {phrase} " in padded for phrase in phrases):
            return motion
    return None


def resolve_scene_command(transcript: str) -> str | None:
    """Return a scene-memory intent associated with a recognized phrase."""
    normalized = " ".join(re.findall(r"[a-z]+", transcript.lower()))
    normalized = normalized.replace("what s ", "what is ")
    padded = f" {normalized} "
    for command, phrases in SCENE_COMMAND_PHRASES:
        if any(f" {phrase} " in padded for phrase in phrases):
            return command
    return None


def is_farewell_command(transcript: str) -> bool:
    """Return whether speech explicitly asks to end the interaction."""
    normalized = " ".join(re.findall(r"[a-z]+", transcript.lower()))
    padded = f" {normalized} "
    return any(f" {phrase} " in padded for phrase in FAREWELL_PHRASES)
