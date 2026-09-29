"""Structured scene goals and deterministic safe action planning."""

from __future__ import annotations

import re
from dataclasses import dataclass

from live_character_robot.scene import ObjectObservation

SUPPORTED_COLORS = ("red", "orange", "yellow", "green", "blue", "purple")
GOAL_VERBS = ("inspect", "find", "look at", "check")


@dataclass(frozen=True)
class SceneGoal:
    """A bounded language goal grounded by a requested object color."""

    target_color: str


def parse_scene_goal(transcript: str) -> SceneGoal | None:
    """Parse supported goal language without inventing an unspecified target."""
    normalized = " ".join(re.findall(r"[a-z]+", transcript.lower()))
    if not any(verb in normalized for verb in GOAL_VERBS):
        return None
    color = next((item for item in SUPPORTED_COLORS if item in normalized.split()), None)
    return None if color is None else SceneGoal(target_color=color)


def plan_scene_goal(
    goal: SceneGoal,
    observation: ObjectObservation | None,
) -> tuple[str, ...]:
    """Map grounded visual evidence to a validated lamp-motion sequence."""
    if observation is None or observation.color != goal.target_color:
        return ()
    if observation.horizontal_position == "left":
        return ("look-left", "nod")
    if observation.horizontal_position == "right":
        return ("look-right", "nod")
    return ("nod",)
