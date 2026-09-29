"""Tests for local scene observation and short-term memory."""

import cv2
import numpy as np

from live_character_robot.scene import (
    ObjectObservation,
    SceneMemory,
    observe_colored_object,
)


def colored_frame(hue: int) -> np.ndarray:
    """Create a synthetic frame with a large colored center object."""
    hsv = np.zeros((200, 200, 3), dtype=np.uint8)
    hsv[50:150, 50:150] = (hue, 255, 255)
    return cv2.cvtColor(hsv, cv2.COLOR_HSV2BGR)


def test_observes_blue_center_object() -> None:
    """A large blue center region should become a grounded observation."""
    observation = observe_colored_object(colored_frame(hue=110))

    assert observation is not None
    assert observation.color == "blue"
    assert observation.confidence == 1.0


def test_observes_purple_center_object() -> None:
    """Camera-shifted purple near the blue boundary should remain purple."""
    observation = observe_colored_object(colored_frame(hue=118))

    assert observation is not None
    assert observation.color == "purple"


def test_ignores_frame_without_saturated_object() -> None:
    """A neutral scene must not be invented as a colored object."""
    frame = np.full((200, 200, 3), 180, dtype=np.uint8)

    assert observe_colored_object(frame) is None


def test_scene_memory_recalls_latest_color() -> None:
    """Memory should answer from the latest camera-derived fact."""
    memory = SceneMemory()
    assert memory.color_answer() == "I do not remember an object yet."

    memory.remember(ObjectObservation(color="green", confidence=0.8))

    assert memory.color_answer() == "The object was green."
