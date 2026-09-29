"""Continuous local speech-and-motion interaction session."""

from __future__ import annotations

from pathlib import Path

import mujoco
import mujoco.viewer
import sounddevice as sd

from live_character_robot.audio import record_microphone, write_wav
from live_character_robot.effects import (
    acknowledgment_sound,
    success_music,
)
from live_character_robot.goals import parse_scene_goal, plan_scene_goal
from live_character_robot.motion import MOTIONS, REST_POSE, pose_vector
from live_character_robot.reliability import (
    observe_safely,
    play_audio_safely,
    start_audio_safely,
    start_speech_safely,
    transcribe_safely,
    wait_for_audio_safely,
    wait_for_speech,
)
from live_character_robot.scene import SceneMemory
from live_character_robot.simulator import (
    animate_targets,
    joint_specs,
    load_robot_model,
)
from live_character_robot.voice import MOTION_RESPONSES
from live_character_robot.voice_commands import (
    resolve_scene_command,
    resolve_voice_command,
)


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
    memory = SceneMemory()

    print("Continuous session started. Close the viewer or press Ctrl+C to stop.")
    try:
        with mujoco.viewer.launch_passive(model, data) as viewer:
            while viewer.is_running():
                print(f"Listening for {duration_seconds:g} seconds...")
                try:
                    samples = record_microphone(duration_seconds)
                    write_wav(recording_path, samples)
                except (OSError, RuntimeError, sd.PortAudioError) as error:
                    print(f"Microphone unavailable; ending session: {error}")
                    break
                if not viewer.is_running():
                    break

                transcript = transcribe_safely(recording_path)
                if transcript is None:
                    continue
                print(f"You said: {transcript}")
                goal = parse_scene_goal(transcript)
                if goal is not None:
                    print(f"Looking for a {goal.target_color} object...")
                    observation = observe_safely(
                        center_only=False,
                        target_color=goal.target_color,
                    )
                    actions = plan_scene_goal(goal, observation)
                    if not actions:
                        response = f"I could not find a {goal.target_color} object."
                        print(f"Lamp response: {response}")
                        wait_for_speech(start_speech_safely(response))
                        continue

                    position_phrase = (
                        "in front of me"
                        if observation.horizontal_position == "center"
                        else f"on my {observation.horizontal_position}"
                    )
                    response = (
                        f"I found the {goal.target_color} object {position_phrase}."
                    )
                    print(f"Plan: {' -> '.join(actions)}")
                    speech = start_speech_safely(response)
                    viewer_open = True
                    for action in actions:
                        targets = tuple(
                            pose_vector(pose, specs) for pose in MOTIONS[action]
                        )
                        viewer_open = animate_targets(model, data, viewer, targets)
                        if not viewer_open:
                            break
                    wait_for_speech(speech)
                    if not viewer_open:
                        break

                    print("Observing the scene again before completion...")
                    final_observation = observe_safely(
                        center_only=False,
                        target_color=goal.target_color,
                    )
                    if final_observation is None:
                        completion = "I cannot confirm the object is still visible."
                    else:
                        completion = (
                            f"Inspection complete. The {goal.target_color} object "
                            "is still visible."
                        )
                    print(f"Lamp response: {completion}")
                    wait_for_speech(start_speech_safely(completion))
                    if final_observation is not None:
                        audio_started = start_audio_safely(success_music())
                        celebration_targets = tuple(
                            pose_vector(pose, specs) for pose in MOTIONS["nod"]
                        )
                        viewer_open = animate_targets(
                            model,
                            data,
                            viewer,
                            celebration_targets,
                            light_pulse=True,
                        )
                        wait_for_audio_safely(audio_started)
                        if not viewer_open:
                            break
                    continue

                scene_command = resolve_scene_command(transcript)
                response = None
                motion = None
                if scene_command == "remember-object":
                    print("Observing the object in the center of the camera...")
                    observation = observe_safely()
                    if observation is None:
                        response = "I could not see a clearly colored object."
                    else:
                        memory.remember(observation)
                        response = f"I remember a {observation.color} object."
                        motion = "nod"
                        play_audio_safely(acknowledgment_sound())
                elif scene_command == "recall-color":
                    response = memory.color_answer()
                    motion = "nod"
                else:
                    motion = resolve_voice_command(transcript)

                if motion is None:
                    if response is None:
                        print("No movement command recognized; the lamp will stay still.")
                        continue
                    print(f"Lamp response: {response}")
                    wait_for_speech(start_speech_safely(response))
                    continue

                print(f"Lamp response: {motion}")
                targets = tuple(
                    pose_vector(pose, specs) for pose in MOTIONS[motion]
                )
                speech = start_speech_safely(response or MOTION_RESPONSES[motion])
                viewer_open = animate_targets(model, data, viewer, targets)
                wait_for_speech(speech)
                if not viewer_open:
                    break
    except KeyboardInterrupt:
        print("Session stopped.")
