# Live Character Robot

An expressive, camera-aware character built around a simulated five-degree-of-freedom lamp. One continuous interaction combines engagement detection, speech, short-term scene memory, goal-directed motion, light, voice, a sound effect, and music.

![Five-degree-of-freedom lamp robot](robot/dummy-lamp.png)

## Run the robot

Requirements: Python 3.12, a camera, microphone, and speakers. The project was developed on macOS and targets Ubuntu 24.04 on a four-core CPU with 8 GB RAM and no discrete GPU.

From the repository root:

```bash
python3.12 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -e '.[dev]'
```

The first transcription downloads the English `base.en` model; later runs use the local cache. On Ubuntu, follow [UBUNTU_SETUP.md](UBUNTU_SETUP.md) and install `espeak-ng` for voice output.

Run the complete demo on macOS:

```bash
.venv/bin/mjpython -m live_character_robot demo --seconds 5
```

On Ubuntu:

```bash
live-character-robot demo --seconds 5
```

Look directly at the camera until the lamp greets you. Wait for `Listening for 5 seconds...`, say one exact command, and allow the response to finish before speaking again.

| Say | Result |
| --- | --- |
| `hello` | Nods and greets you. |
| `no` | Shakes its head. |
| `look up` | Tilts its head upward. |
| `go to sleep` | Moves into a sleep pose. |
| `remember this object` | Observes a centrally held colored object, remembers its color, nods, and plays a two-note sound effect. |
| `what was the color of the object?` | Speaks the last remembered color. |
| `inspect the yellow object` | Locates the named color, turns toward it, nods, observes again, and reports completion. Replace `yellow` with the recognized color. |
| `goodbye` | Says goodbye, performs a farewell movement, returns to idle, and closes the session. |

For the object sequence, use a large, saturated red, orange, yellow, green, blue, or purple object in even lighting. Keep it visible through the inspection's final confirmation. A successful inspection produces a warm shade-light pulse and a three-note musical cue. Left and right are reported from the lamp camera's perspective, opposite the facing person's sides.

Looking fully away or leaving the frame also ends the interaction through visual disengagement. Close the viewer or press `Ctrl+C` to stop manually. Camera frames are processed locally and are not saved or transmitted; temporary microphone recordings are excluded from Git.

Useful checks:

```bash
live-character-robot inspect-model
live-character-robot camera
live-character-robot audio-devices
live-character-robot microphone --seconds 5 --playback
pytest
ruff check .
```

On macOS, select the built-in camera rather than iPhone Continuity Camera if prompted.

## Measured results

Measurements were taken on the Apple Silicon development machine with local speech recognition warmed up. They show feasibility for the target specification but do not replace testing on the actual Ubuntu laptop.

| Measurement | Result |
| --- | --- |
| Warm speech-to-intent latency | `0.507–0.570 s` |
| First-run latency | `1.207 s` |
| Three-run mean latency | `0.7612 s` |
| Average process CPU use | `143.1%`, approximately `1.4` CPU cores |
| Transcription thread cap | `2` CPU threads |
| Peak memory | `504.1 MiB` |
| Guided engagement test | `100%` across `360` frames and `3` controlled trials |
| Automated tests | `69 passed` |

The engagement result is a small controlled test, not a claim of reliability across all people, cameras, poses, or lighting. Reproduce the measurements with:

```bash
live-character-robot measure-runtime recordings/microphone-test.wav
live-character-robot measure-engagement --trials 3
```

## Important choices and tradeoffs

The supplied URDF defines the lamp model and joint limits, not the software architecture. This implementation therefore separates perception, memory, planning, safe named actions, simulation, and audio.

| Choice | Benefit | Tradeoff |
| --- | --- | --- |
| MuJoCo simulation | Imports the five-DOF model, exposes joint limits, and runs without a GPU. | Does not validate physical actuator dynamics, collision safety, or real lighting. |
| Predefined joint-limited motions | Keeps execution safe, predictable, explainable, and testable. | Cannot invent unrestricted movements or execute open-ended goals. |
| Local `faster-whisper` transcription | Avoids API cost and audio upload and can run offline after setup. | Model startup adds latency and transcription uses noticeable CPU. |
| Fixed command parsing | Produces reliable bounded behavior. | Requires the documented phrases instead of unrestricted conversation. |
| Local HSV color detection | Fast, private, and inexpensive on CPU. | Sensitive to exposure, saturation, background, and lighting; yellow/orange and blue/purple may be confused. |
| One-object in-memory scene model | Private and easy to reason about. | Cannot remember multiple objects or retain memory between sessions. |
| Shared camera engagement monitor | Connects engagement, observation, and disengagement in one experience. | Face detection can be affected by glare, glasses, occlusion, and pose. |
| System voice and synthesized tones | Supplies voice, sound effects, and music locally without bundled copyrighted audio. | Voice quality and available speech engines vary by operating system. |

Cloud perception was intentionally not used. Staying local avoids usage cost, network dependence, and camera/audio transfer, at the cost of bounded language and six heuristic color categories.

## Completed and intentionally left out

### Completed

- One continuous engagement-to-disengagement character demo
- Five-DOF MuJoCo simulation with imported joint limits and safe named motions
- Local speech recognition and operating-system voice output
- Camera engagement detection with dwell-time stabilization
- One-object color memory and spoken recall
- Spoken scene goals, deterministic planning, and post-action observation
- Purposeful motion, shade-light pulse, voice, two-note sound effect, and three-note music
- Graceful handling of silence and unavailable camera, microphone, or audio
- Automated tests and latency, CPU, memory, and engagement measurements
- Ubuntu 24.04 setup guidance and a two-page [technical note](TECHNICAL_NOTE.md)

### Intentionally left out

- Physical robot actuation, hardware safety systems, and real-world dynamics
- Open-ended cloud vision, language models, or unrestricted conversation
- General object recognition beyond six heuristic color categories
- Multiple-object, persistent, or cross-session memory
- Model-generated joint trajectories
- Photometrically accurate simulated light output
- Validation on physical Ubuntu 24.04 hardware

These boundaries keep the result coherent, explainable, private, and appropriate for the challenge timebox. The main known limitation is lighting-sensitive color classification; pale or low-saturation objects and colors near category boundaries may be misidentified.

## Documentation and provided materials

See [CHALLENGE.md](CHALLENGE.md) for the brief, [SUBMISSION.md](SUBMISSION.md) for the evaluation criteria, [UBUNTU_SETUP.md](UBUNTU_SETUP.md) for deployment, and [TECHNICAL_NOTE.md](TECHNICAL_NOTE.md) for the two-page technical summary.

Human Computer Lab provided the challenge brief, submission requirements, five-degree-of-freedom lamp URDF, lamp reference image, and lamp-shade STL mesh. The application architecture, simulation integration, perception, interaction, motion, audio, tests, measurements, and documentation were developed for this submission.
