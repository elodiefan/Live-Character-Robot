"""Tests for local scene observation and short-term memory."""

import cv2
import numpy as np

from live_character_robot.scene import (
    ObjectObservation,
    SceneMemory,
    color_diagnostics,
    observe_colored_object,
)


def colored_frame(hue: int, saturation: int = 255) -> np.ndarray:
    """Create a synthetic frame with a large colored center object."""
    hsv = np.zeros((200, 200, 3), dtype=np.uint8)
    hsv[50:150, 50:150] = (hue, saturation, 255)
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


def test_observes_light_blue_center_object() -> None:
    """A pale blue object should remain visible below the old saturation floor."""
    observation = observe_colored_object(colored_frame(hue=115, saturation=20))

    assert observation is not None
    assert observation.color == "blue"


def test_distinguishes_warm_yellow_from_orange() -> None:
    """Camera-warmed yellow and true orange should fall on opposite boundaries."""
    yellow = observe_colored_object(colored_frame(hue=22))
    orange = observe_colored_object(colored_frame(hue=16))

    assert yellow is not None
    assert orange is not None
    assert yellow.color == "yellow"
    assert orange.color == "orange"


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


def test_observes_target_position_across_full_frame() -> None:
    """Goal perception should retain where the requested object appears."""
    hsv = np.zeros((200, 300, 3), dtype=np.uint8)
    hsv[60:140, 15:95] = (110, 255, 255)
    frame = cv2.cvtColor(hsv, cv2.COLOR_HSV2BGR)

    observation = observe_colored_object(
        frame,
        center_only=False,
        target_color="blue",
    )

    assert observation is not None
    assert observation.horizontal_position == "left"


def test_color_diagnostics_reports_pale_center_object() -> None:
    """Diagnostics should expose low-saturation object values for calibration."""
    frame = colored_frame(hue=105, saturation=35)

    diagnostics = color_diagnostics(frame)

    assert diagnostics["median_hue"] == 105.0
    assert diagnostics["median_saturation"] == 35.0
    assert diagnostics["colored_fraction"] == 1.0
