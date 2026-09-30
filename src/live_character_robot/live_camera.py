"""Shared live camera ownership for engagement and scene observation."""

from __future__ import annotations

import threading
import time
from contextlib import contextmanager
from types import TracebackType

import cv2
import numpy as np
from numpy.typing import NDArray

from live_character_robot.engagement import EngagementEvent, EngagementTracker


class CameraMonitor:
    """Capture frames once while tracking stable engagement in the background."""

    def __init__(self, camera_index: int = 0) -> None:
        self.camera_index = camera_index
        self.tracker = EngagementTracker()
        self._camera: cv2.VideoCapture | None = None
        self._thread: threading.Thread | None = None
        self._stop = threading.Event()
        self._engaged = threading.Event()
        self._disengaged = threading.Event()
        self._frame_ready = threading.Event()
        self._lock = threading.Lock()
        self._latest_frame: NDArray[np.uint8] | None = None
        self._pause_count = 0
        self._error: RuntimeError | None = None

    @property
    def disengaged(self) -> bool:
        """Report whether attention moved away after initial engagement."""
        return self._disengaged.is_set()

    def update_engagement(self, face_visible: bool, now: float) -> EngagementEvent:
        """Update stable attention state and publish meaningful transitions."""
        with self._lock:
            event = self.tracker.update(face_visible, now)
        if event is EngagementEvent.ENGAGED:
            self._engaged.set()
        elif event is EngagementEvent.DISENGAGED:
            self._disengaged.set()
        return event

    def mark_active_interaction(self) -> None:
        """Treat recognized speech as engagement and restart absence timing."""
        with self._lock:
            self.tracker = EngagementTracker(
                engage_after=self.tracker.engage_after,
                disengage_after=self.tracker.disengage_after,
                engaged=True,
            )
            self._disengaged.clear()

    def start(self) -> None:
        """Open the local camera and start background capture."""
        cascade_path = cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
        self._detector = cv2.CascadeClassifier(cascade_path)
        if self._detector.empty():
            raise RuntimeError(f"Could not load face detector: {cascade_path}")
        self._camera = cv2.VideoCapture(self.camera_index)
        if not self._camera.isOpened():
            self._camera.release()
            raise RuntimeError(f"Could not open camera {self.camera_index}")
        self._thread = threading.Thread(target=self._capture_loop, daemon=True)
        self._thread.start()

    def _capture_loop(self) -> None:
        """Continuously retain one current frame and sample face visibility."""
        assert self._camera is not None
        last_detection = 0.0
        consecutive_failures = 0
        while not self._stop.is_set():
            ok, frame = self._camera.read()
            if not ok:
                consecutive_failures += 1
                if consecutive_failures >= 100:
                    self._error = RuntimeError("Camera stopped returning frames")
                    return
                time.sleep(0.05)
                continue
            consecutive_failures = 0
            with self._lock:
                self._latest_frame = frame.copy()
            self._frame_ready.set()

            now = time.monotonic()
            with self._lock:
                tracking_paused = self._pause_count > 0
            if tracking_paused or now - last_detection < 0.1:
                continue
            gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
            faces = self._detector.detectMultiScale(
                gray,
                scaleFactor=1.1,
                minNeighbors=5,
                minSize=(80, 80),
            )
            self.update_engagement(len(faces) > 0, now)
            last_detection = now

    def wait_for_engagement(self) -> None:
        """Block until stable eye contact or a camera failure occurs."""
        while not self._engaged.wait(0.1):
            if self._error is not None:
                raise self._error

    def latest_frame(self, timeout: float = 2.0) -> NDArray[np.uint8]:
        """Return a copy of the newest frame without storing it on disk."""
        if not self._frame_ready.wait(timeout):
            raise RuntimeError("Camera did not provide a current frame")
        if self._error is not None:
            raise self._error
        with self._lock:
            if self._latest_frame is None:
                raise RuntimeError("Camera frame was unavailable")
            return self._latest_frame.copy()

    @contextmanager
    def pause_engagement_tracking(self):
        """Keep capturing while scene observation temporarily obscures a face."""
        with self._lock:
            self._pause_count += 1
        try:
            yield
        finally:
            with self._lock:
                self._pause_count -= 1

    def close(self) -> None:
        """Stop capture and release the camera device."""
        self._stop.set()
        if self._thread is not None:
            self._thread.join(timeout=2.0)
        if self._camera is not None:
            self._camera.release()

    def __enter__(self) -> CameraMonitor:
        self.start()
        return self

    def __exit__(
        self,
        _exc_type: type[BaseException] | None,
        _exc_value: BaseException | None,
        _traceback: TracebackType | None,
    ) -> None:
        self.close()
