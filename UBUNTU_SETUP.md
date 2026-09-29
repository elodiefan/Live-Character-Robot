# Ubuntu 24.04 Setup and Demo

## Target

This guide targets a clean Ubuntu 24.04 LTS laptop with four CPU cores, 8 GB of
RAM, no discrete GPU, and standard camera, microphone, and speaker devices.

## Install system packages

```bash
sudo apt update
sudo apt install -y \
  python3.12 python3.12-venv python3-pip build-essential \
  libgl1 libglib2.0-0 libglfw3 libportaudio2 portaudio19-dev \
  espeak-ng
```

The MuJoCo Python wheel provides the simulation runtime. `espeak-ng` supplies
offline voice output, PortAudio exposes local audio devices, and the OpenGL
libraries support the interactive viewer.

## Create the environment

From the repository root:

```bash
python3.12 -m venv .venv
source .venv/bin/activate
python -m pip install --upgrade pip
python -m pip install -e '.[dev]'
pytest
ruff check .
```

The first transcription downloads the CPU-oriented English `base.en` model.
Run this once while online; subsequent transcription can use the local cache.

## Check local devices

```bash
live-character-robot audio-devices
live-character-robot camera --index 0
```

Press `Q` or `Esc` to close the camera preview. If the intended USB camera is
not index `0`, try another non-negative index. Confirm that the user belongs to
the desktop session with access to `/dev/video*` and local PipeWire/PulseAudio.

## Run the complete interaction

Unlike macOS, Ubuntu does not require MuJoCo's `mjpython` launcher:

```bash
live-character-robot session --seconds 5
```

Suggested demonstration sequence:

1. Say `hello`, `no`, or `look up` to show speech, voice, and safe motion.
2. Hold a bright supported color centrally and say `remember this object`.
3. Ask `what was the color of the object?` to demonstrate short-term recall.
4. Hold the object left, center, or right and say `inspect the blue object`,
   substituting its actual color. Keep it visible through the second camera
   observation.
5. Observe the completion nod, shade pulse, sound effect, and musical cue.
6. Close the viewer or press `Ctrl+C` to stop.

Supported colors are red, orange, yellow, green, blue, and purple. Camera
left/right is reported from the character's perspective.

## Privacy and generated data

Camera frames are processed in memory and discarded. Microphone clips stay
under ignored `recordings/`; raw measurement JSON stays under ignored
`measurements/`. No cloud API is used during the interaction. Delete those
local directories after the demonstration if the recordings are no longer
needed.

## Known Ubuntu risks

The implementation was developed and measured on macOS, not on the final
Ubuntu hardware. Before submission, validate camera indexing, audio routing,
OpenGL viewer startup, `espeak-ng`, and performance on the actual target.
Wayland/OpenGL or PipeWire device configuration may vary by laptop.
