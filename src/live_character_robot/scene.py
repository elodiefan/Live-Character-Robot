"""Local colored-object observation and bounded in-session scene memory."""

from __future__ import annotations

import time
from dataclasses import dataclass

import cv2
import numpy as np
from numpy.typing import NDArray

MIN_COLOR_FRACTION = 0.08


@dataclass(frozen=True)
class ObjectObservation:
    """A compact fact retained from a camera observation."""

    color: str
    confidence: float


@dataclass
class SceneMemory:
    """Keep only the most recent object fact for the current session."""

    last_object: ObjectObservation | None = None

    def remember(self, observation: ObjectObservation) -> None:
        """Replace stale scene information with the latest observation."""
        self.last_object = observation

    def color_answer(self) -> str:
        """Answer a color recall question without inventing missing facts."""
        if self.last_object is None:
            return "I do not remember an object yet."
        return f"The object was {self.last_object.color}."


def observe_colored_object(frame: NDArray[np.uint8]) -> ObjectObservation | None:
    """Identify the dominant saturated color in the center of a BGR frame."""
    height, width = frame.shape[:2]
    region = frame[height // 4 : 3 * height // 4, width // 4 : 3 * width // 4]
    hsv = cv2.cvtColor(region, cv2.COLOR_BGR2HSV)
    hue = hsv[:, :, 0]
    saturation = hsv[:, :, 1]
    value = hsv[:, :, 2]
    visible = (saturation >= 90) & (value >= 60)

    masks = {
        "red": visible & ((hue <= 10) | (hue >= 170)),
        "orange": visible & (hue >= 11) & (hue <= 24),
        "yellow": visible & (hue >= 25) & (hue <= 37),
        "green": visible & (hue >= 38) & (hue <= 85),
        "blue": visible & (hue >= 86) & (hue <= 115),
        "purple": visible & (hue >= 116) & (hue <= 169),
    }
    color, mask = max(masks.items(), key=lambda item: np.count_nonzero(item[1]))
    confidence = float(np.count_nonzero(mask) / mask.size)
    if confidence < MIN_COLOR_FRACTION:
        return None
    return ObjectObservation(color=color, confidence=confidence)


def capture_camera_frame(camera_index: int = 0) -> NDArray[np.uint8]:
    """Capture a warmed-up frame from the selected local camera."""
    camera = cv2.VideoCapture(camera_index)
    if not camera.isOpened():
        camera.release()
        raise RuntimeError(f"Could not open camera {camera_index}")
    frame = None
    try:
        deadline = time.monotonic() + 2.0
        while time.monotonic() < deadline:
            ok, candidate = camera.read()
            if ok:
                frame = candidate
        if frame is None:
            raise RuntimeError(f"Camera {camera_index} did not return a frame")
        return frame
    finally:
        camera.release()
