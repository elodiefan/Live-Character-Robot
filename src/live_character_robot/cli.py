"""Command-line entry point for the Live Character Robot application."""

from __future__ import annotations

import argparse
from collections.abc import Sequence
from pathlib import Path

from live_character_robot import __version__
from live_character_robot.audio import (
    describe_audio_devices,
    play_audio,
    record_microphone,
    write_wav,
)
from live_character_robot.camera import run_engagement_camera
from live_character_robot.interaction import run_interaction_session
from live_character_robot.measurements import (
    format_results,
    measure_engagement,
    measure_runtime,
)
from live_character_robot.motion import MOTIONS, pose_vector
from live_character_robot.simulator import (
    animate_poses,
    joint_specs,
    launch_simulator,
    load_robot_model,
)
from live_character_robot.transcription import transcribe_file
from live_character_robot.voice import MOTION_RESPONSES, start_speech
from live_character_robot.voice_commands import resolve_voice_command


def build_parser() -> argparse.ArgumentParser:
    """Build the application argument parser."""
    parser = argparse.ArgumentParser(
        prog="live-character-robot",
        description="Run the Live Character Robot application.",
    )
    parser.add_argument(
        "--version",
        action="version",
        version=f"%(prog)s {__version__}",
    )
    subparsers = parser.add_subparsers(dest="command")
    subparsers.add_parser("inspect-model", help="Print the imported robot joints and limits.")
    subparsers.add_parser("simulate", help="Open the robot in the MuJoCo viewer.")
    animate_parser = subparsers.add_parser("animate", help="Play an expressive motion.")
    animate_parser.add_argument("motion", choices=tuple(MOTIONS))
    camera_parser = subparsers.add_parser(
        "camera", help="Preview frontal-face engagement detection."
    )
    camera_parser.add_argument(
        "--index",
        type=int,
        default=0,
        help="Camera device index (default: 0).",
    )
    subparsers.add_parser("audio-devices", help="List microphone and speaker devices.")
    microphone_parser = subparsers.add_parser(
        "microphone", help="Record a bounded microphone test clip."
    )
    microphone_parser.add_argument("--seconds", type=float, default=5.0)
    microphone_parser.add_argument(
        "--output",
        type=Path,
        default=Path("recordings/microphone-test.wav"),
    )
    microphone_parser.add_argument(
        "--playback",
        action="store_true",
        help="Play the recorded clip through the default speaker.",
    )
    transcribe_parser = subparsers.add_parser(
        "transcribe", help="Transcribe a completed local audio file."
    )
    transcribe_parser.add_argument("audio_file", type=Path)
    listen_parser = subparsers.add_parser(
        "listen", help="Record a bounded utterance and transcribe it."
    )
    listen_parser.add_argument("--seconds", type=float, default=5.0)
    listen_parser.add_argument(
        "--output",
        type=Path,
        default=Path("recordings/latest-utterance.wav"),
    )
    react_parser = subparsers.add_parser(
        "react", help="Listen once and perform a recognized lamp motion."
    )
    react_parser.add_argument("--seconds", type=float, default=5.0)
    react_parser.add_argument(
        "--output",
        type=Path,
        default=Path("recordings/latest-command.wav"),
    )
    session_parser = subparsers.add_parser(
        "session", help="Keep one viewer open and react to multiple commands."
    )
    session_parser.add_argument("--seconds", type=float, default=5.0)
    session_parser.add_argument(
        "--output",
        type=Path,
        default=Path("recordings/latest-command.wav"),
    )
    runtime_parser = subparsers.add_parser(
        "measure-runtime", help="Measure local speech-to-intent latency and resources."
    )
    runtime_parser.add_argument("audio_file", type=Path)
    runtime_parser.add_argument("--iterations", type=int, default=3)
    runtime_parser.add_argument(
        "--output",
        type=Path,
        default=Path("measurements/runtime.json"),
    )
    engagement_parser = subparsers.add_parser(
        "measure-engagement", help="Run guided camera engagement reliability trials."
    )
    engagement_parser.add_argument("--camera-index", type=int, default=0)
    engagement_parser.add_argument("--trials", type=int, default=3)
    engagement_parser.add_argument("--seconds-per-state", type=float, default=2.0)
    engagement_parser.add_argument(
        "--output",
        type=Path,
        default=Path("measurements/engagement.json"),
    )
    return parser


def main(argv: Sequence[str] | None = None) -> int:
    """Run the application command."""
    parser = build_parser()
    args = parser.parse_args(argv)

    if args.command == "inspect-model":
        model = load_robot_model()
        print(f"Loaded lamp model with {model.njnt} joints:")
        for joint in joint_specs(model):
            print(f"- {joint.name}: [{joint.lower:.3f}, {joint.upper:.3f}] rad")
        return 0

    if args.command == "simulate":
        launch_simulator(load_robot_model())
        return 0

    if args.command == "animate":
        model = load_robot_model()
        specs = joint_specs(model)
        poses = tuple(pose_vector(pose, specs) for pose in MOTIONS[args.motion])
        animate_poses(model, poses)
        return 0

    if args.command == "camera":
        run_engagement_camera(args.index)
        return 0

    if args.command == "audio-devices":
        print(describe_audio_devices())
        return 0

    if args.command == "microphone":
        print(f"Recording for {args.seconds:g} seconds...")
        samples = record_microphone(args.seconds)
        write_wav(args.output, samples)
        print(f"Saved recording to {args.output}")
        if args.playback:
            print("Playing recording...")
            play_audio(samples)
        return 0

    if args.command == "transcribe":
        print(f"Transcript: {transcribe_file(args.audio_file)}")
        return 0

    if args.command == "listen":
        print(f"Listening for {args.seconds:g} seconds...")
        samples = record_microphone(args.seconds)
        write_wav(args.output, samples)
        print("Transcribing bounded audio clip...")
        print(f"You said: {transcribe_file(args.output)}")
        return 0

    if args.command == "react":
        print(f"Listening for {args.seconds:g} seconds...")
        samples = record_microphone(args.seconds)
        write_wav(args.output, samples)
        transcript = transcribe_file(args.output)
        print(f"You said: {transcript}")
        motion = resolve_voice_command(transcript)
        if motion is None:
            print("I did not recognize a movement command, so I will stay still.")
            return 0
        print(f"Lamp response: {motion}")
        model = load_robot_model()
        specs = joint_specs(model)
        poses = tuple(pose_vector(pose, specs) for pose in MOTIONS[motion])
        speech = start_speech(MOTION_RESPONSES[motion])
        animate_poses(model, poses, hold_seconds=1.5)
        speech.wait()
        return 0

    if args.command == "session":
        run_interaction_session(args.seconds, recording_path=args.output)
        return 0

    if args.command == "measure-runtime":
        results = measure_runtime(
            args.audio_file,
            iterations=args.iterations,
            output_path=args.output,
        )
        print(format_results(results))
        print(f"Saved results to {args.output}")
        return 0

    if args.command == "measure-engagement":
        results = measure_engagement(
            camera_index=args.camera_index,
            trials=args.trials,
            seconds_per_state=args.seconds_per_state,
            output_path=args.output,
        )
        print(format_results(results))
        print(f"Saved results to {args.output}")
        return 0

    print("Live Character Robot scaffold is ready.")
    return 0
