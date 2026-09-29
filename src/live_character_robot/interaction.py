"""Continuous local speech-and-motion interaction session."""

from __future__ import annotations

from pathlib import Path

import mujoco
import mujoco.viewer

from live_character_robot.audio import record_microphone, write_wav
from live_character_robot.motion import MOTIONS, REST_POSE, pose_vector
from live_character_robot.simulator import (
    animate_targets,
    joint_specs,
    load_robot_model,
)
from live_character_robot.transcription import transcribe_file
from live_character_robot.voice import MOTION_RESPONSES, start_speech
from live_character_robot.voice_commands import resolve_voice_command


def run_interaction_session(
    duration_seconds: float = 5.0,
    *,
    recording_path: Path = Path("recordings/latest-command.wav"),
) -> None:
    """Keep one viewer open while listening and reacting to bounded clips."""
    model = load_robot_model()
    specs = joint_specs(model)
    rest = pose_vector(REST_POSE, specs)
    data = mujoco.MjData(model)
    data.qpos[:] = rest
    mujoco.mj_forward(model, data)

    print("Continuous session started. Close the viewer or press Ctrl+C to stop.")
    try:
        with mujoco.viewer.launch_passive(model, data) as viewer:
            while viewer.is_running():
                print(f"Listening for {duration_seconds:g} seconds...")
                samples = record_microphone(duration_seconds)
                write_wav(recording_path, samples)
                if not viewer.is_running():
                    break

                transcript = transcribe_file(recording_path)
                print(f"You said: {transcript}")
                motion = resolve_voice_command(transcript)
                if motion is None:
                    print("No movement command recognized; the lamp will stay still.")
                    continue

                print(f"Lamp response: {motion}")
                targets = tuple(
                    pose_vector(pose, specs) for pose in MOTIONS[motion]
                )
                speech = start_speech(MOTION_RESPONSES[motion])
                viewer_open = animate_targets(model, data, viewer, targets)
                speech.wait()
                if not viewer_open:
                    break
    except KeyboardInterrupt:
        print("Session stopped.")
