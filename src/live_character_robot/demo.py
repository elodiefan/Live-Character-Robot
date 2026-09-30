"""One coherent engagement-to-disengagement character demonstration."""

from __future__ import annotations

from pathlib import Path

from live_character_robot.interaction import run_interaction_session
from live_character_robot.live_camera import CameraMonitor


def run_integrated_demo(
    duration_seconds: float = 5.0,
    *,
    camera_index: int = 0,
    recording_path: Path = Path("recordings/latest-command.wav"),
) -> None:
    """Wait for engagement, interact, then disengage through one camera owner."""
    print("Starting integrated demo. Look directly at the camera to engage.")
    with CameraMonitor(camera_index) as camera:
        camera.wait_for_engagement()
        print("Engagement detected. Starting character interaction.")
        run_interaction_session(
            duration_seconds,
            recording_path=recording_path,
            camera_monitor=camera,
            acknowledge_engagement=True,
        )
