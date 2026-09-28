"""Local camera preview and frontal-face engagement detection."""

from __future__ import annotations

import time

import cv2

from live_character_robot.engagement import EngagementTracker

WINDOW_TITLE = "Live Character Robot - press Q to quit"
MAX_CONSECUTIVE_FRAME_FAILURES = 100
FRAME_RETRY_DELAY_SECONDS = 0.05


def run_engagement_camera(camera_index: int = 0) -> None:
    """Show a live preview with stable engagement state overlays."""
    cascade_path = cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
    detector = cv2.CascadeClassifier(cascade_path)
    if detector.empty():
        raise RuntimeError(f"Could not load frontal-face detector: {cascade_path}")

    camera = cv2.VideoCapture(camera_index)
    if not camera.isOpened():
        camera.release()
        raise RuntimeError(
            f"Could not open camera {camera_index}. Check camera access and macOS permissions."
        )

    tracker = EngagementTracker()
    consecutive_failures = 0
    try:
        while True:
            ok, frame = camera.read()
            if not ok:
                consecutive_failures += 1
                if consecutive_failures >= MAX_CONSECUTIVE_FRAME_FAILURES:
                    raise RuntimeError(
                        f"Camera {camera_index} stopped returning frames. "
                        "If macOS selected an iPhone Continuity Camera, reconnect it or "
                        "try the built-in camera with: live-character-robot camera --index 1"
                    )
                time.sleep(FRAME_RETRY_DELAY_SECONDS)
                continue
            consecutive_failures = 0

            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            faces = detector.detectMultiScale(
                gray,
                scaleFactor=1.1,
                minNeighbors=5,
                minSize=(80, 80),
            )
            tracker.update(face_visible=len(faces) > 0, now=time.monotonic())

            color = (60, 200, 90) if tracker.engaged else (80, 160, 255)
            state = "ENGAGED" if tracker.engaged else "IDLE"
            for x, y, width, height in faces:
                cv2.rectangle(frame, (x, y), (x + width, y + height), color, 2)
            cv2.putText(
                frame,
                f"State: {state}",
                (20, 40),
                cv2.FONT_HERSHEY_SIMPLEX,
                0.9,
                color,
                2,
                cv2.LINE_AA,
            )
            cv2.imshow(WINDOW_TITLE, frame)
            key = cv2.waitKey(1) & 0xFF
            if key in (ord("q"), 27):
                break
    finally:
        camera.release()
        cv2.destroyAllWindows()
