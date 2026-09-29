"""Tests for grounded, deterministic scene-goal planning."""

import pytest

from live_character_robot.goals import (
    SceneGoal,
    parse_scene_goal,
    plan_scene_goal,
)
from live_character_robot.scene import ObjectObservation


@pytest.mark.parametrize(
    ("transcript", "color"),
    (
        ("Inspect the blue object", "blue"),
        ("Please find the purple object", "purple"),
        ("Look at the yellow object", "yellow"),
    ),
)
def test_parse_scene_goal(transcript: str, color: str) -> None:
    """Supported language should become an explicit color target."""
    assert parse_scene_goal(transcript) == SceneGoal(target_color=color)


@pytest.mark.parametrize("transcript", ("Inspect the object", "Hello", "Find my keys"))
def test_parse_scene_goal_rejects_unbounded_requests(transcript: str) -> None:
    """A goal without a supported visual target must not trigger motion."""
    assert parse_scene_goal(transcript) is None


@pytest.mark.parametrize(
    ("position", "expected"),
    (
        ("left", ("look-left", "nod")),
        ("center", ("nod",)),
        ("right", ("look-right", "nod")),
    ),
)
def test_plan_scene_goal_uses_observed_position(
    position: str,
    expected: tuple[str, ...],
) -> None:
    """Visual position should select only predefined motion primitives."""
    goal = SceneGoal(target_color="blue")
    observation = ObjectObservation("blue", 0.2, position)

    assert plan_scene_goal(goal, observation) == expected


def test_plan_scene_goal_refuses_missing_target() -> None:
    """The planner must stay still when live evidence does not match the goal."""
    assert plan_scene_goal(SceneGoal("blue"), None) == ()
    assert plan_scene_goal(
        SceneGoal("blue"), ObjectObservation("red", 0.2)
    ) == ()
