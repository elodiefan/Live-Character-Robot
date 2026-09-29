"""Repeatable local performance and engagement measurements."""

from __future__ import annotations

import json
import platform
import resource
import time
from pathlib import Path
from statistics import mean

import cv2

from live_character_robot.transcription import transcribe_file
from live_character_robot.voice_commands import (
    resolve_scene_command,
    resolve_voice_command,
)


def peak_memory_mb(max_rss: float | None = None, system: str | None = None) -> float:
    """Normalize ru_maxrss to MiB across macOS bytes and Linux KiB."""
    value = resource.getrusage(resource.RUSAGE_SELF).ru_maxrss if max_rss is None else max_rss
    active_system = platform.system() if system is None else system
    divisor = 1024.0 * 1024.0 if active_system == "Darwin" else 1024.0
    return value / divisor


def write_results(path: Path, results: dict[str, object]) -> None:
    """Write stable, human-readable measurement evidence as JSON."""
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(results, indent=2) + "\n", encoding="utf-8")


def measure_runtime(
    audio_path: Path,
    *,
    iterations: int = 3,
    output_path: Path = Path("measurements/runtime.json"),
) -> dict[str, object]:
    """Measure local audio-to-intent latency and process resource use."""
    if iterations < 1:
        raise ValueError("Measurement iterations must be positive")

    wall_start = time.perf_counter()
    cpu_start = time.process_time()
    latencies = []
    transcripts = []
    intents = []
    for _ in range(iterations):
        iteration_start = time.perf_counter()
        transcript = transcribe_file(audio_path)
        intent = resolve_scene_command(transcript) or resolve_voice_command(transcript)
        latencies.append(time.perf_counter() - iteration_start)
        transcripts.append(transcript)
        intents.append(intent)

    wall_seconds = time.perf_counter() - wall_start
    cpu_seconds = time.process_time() - cpu_start
    results: dict[str, object] = {
        "platform": platform.platform(),
        "audio_file": str(audio_path),
        "iterations": iterations,
        "latency_seconds": {
            "samples": [round(value, 4) for value in latencies],
            "mean": round(mean(latencies), 4),
            "minimum": round(min(latencies), 4),
            "maximum": round(max(latencies), 4),
        },
        "cpu_seconds": round(cpu_seconds, 4),
        "average_cpu_percent_one_core": round(cpu_seconds / wall_seconds * 100.0, 1),
        "peak_memory_mb": round(peak_memory_mb(), 1),
        "transcripts": transcripts,
        "resolved_intents": intents,
    }
    write_results(output_path, results)
    return results


def _face_visibility_rate(
    camera: cv2.VideoCapture,
    detector: cv2.CascadeClassifier,
    duration_seconds: float,
) -> tuple[int, int]:
    visible_frames = 0
    total_frames = 0
    deadline = time.monotonic() + duration_seconds
    while time.monotonic() < deadline:
        ok, frame = camera.read()
        if not ok:
            continue
        gray = cv2.cvtColor(frame, cv2.COLOR_BGR2GRAY)
        faces = detector.detectMultiScale(
            gray,
            scaleFactor=1.1,
            minNeighbors=5,
            minSize=(80, 80),
        )
        visible_frames += int(len(faces) > 0)
        total_frames += 1
    return visible_frames, total_frames


def measure_engagement(
    *,
    camera_index: int = 0,
    trials: int = 3,
    seconds_per_state: float = 2.0,
    output_path: Path = Path("measurements/engagement.json"),
) -> dict[str, object]:
    """Run guided face-visible/face-absent trials and save frame accuracy."""
    if trials < 1 or seconds_per_state <= 0:
        raise ValueError("Trials and seconds per state must be positive")
    cascade_path = cv2.data.haarcascades + "haarcascade_frontalface_default.xml"
    detector = cv2.CascadeClassifier(cascade_path)
    camera = cv2.VideoCapture(camera_index)
    if detector.empty() or not camera.isOpened():
        camera.release()
        raise RuntimeError("Could not initialize camera engagement measurement")

    expected_visible_correct = 0
    expected_absent_correct = 0
    visible_total = 0
    absent_total = 0
    try:
        for trial in range(1, trials + 1):
            input(f"Trial {trial}/{trials}: look directly at the camera, then press Enter.")
            visible, total = _face_visibility_rate(camera, detector, seconds_per_state)
            expected_visible_correct += visible
            visible_total += total

            input(f"Trial {trial}/{trials}: turn away or leave the frame, then press Enter.")
            visible, total = _face_visibility_rate(camera, detector, seconds_per_state)
            expected_absent_correct += total - visible
            absent_total += total
    finally:
        camera.release()

    correct = expected_visible_correct + expected_absent_correct
    total = visible_total + absent_total
    results: dict[str, object] = {
        "platform": platform.platform(),
        "camera_index": camera_index,
        "trials": trials,
        "seconds_per_state": seconds_per_state,
        "face_visible_accuracy_percent": round(
            expected_visible_correct / visible_total * 100.0, 1
        ),
        "face_absent_accuracy_percent": round(
            expected_absent_correct / absent_total * 100.0, 1
        ),
        "overall_engagement_accuracy_percent": round(correct / total * 100.0, 1),
        "evaluated_frames": total,
    }
    write_results(output_path, results)
    return results


def format_results(results: dict[str, object]) -> str:
    """Format JSON-compatible results for terminal review."""
    return json.dumps(results, indent=2)
