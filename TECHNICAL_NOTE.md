# Live Character Robot - Technical Note

## Architecture and data flow

The system composes local perception, language, deterministic planning, safe
motion, and character effects around the supplied five-DOF lamp. Camera frames
feed frontal-face engagement and HSV colored-object observation. Bounded
microphone clips feed the CPU `faster-whisper` `base.en` model. Normalized text
becomes either a fixed motion command, a scene-memory operation, or a structured
color goal. Only the deterministic controller writes simulated joint state.

```text
Camera -> engagement / object observation --+
                                             +-> controller <-> scene memory
Mic -> local transcription -> bounded intent-+       |
                                                     v
                                    validated motion + light + local audio
                                                     |
                                                     v
                                      MuJoCo lamp + laptop speaker
```

## Protocol, decisions, and execution boundary

The internal protocol is a small typed vocabulary: named scene observations
(color, confidence, horizontal position), goals (target color), and actions
(`look-left`, `look-right`, `nod`, `shake`, `look-up`, `sleep`). Language never
produces arbitrary joint values. The planner selects only named actions; the
motion layer converts named poses to ordered vectors and clamps every value to
the URDF joint limits. Smoothstep interpolation owns body execution.

For `inspect the blue object`, the camera first searches the full frame for the
requested color. The planner uses its left/center/right position to select a
bounded orientation-and-nod sequence. After execution, the camera observes
again; the character reports completion only if the requested target remains
visible. Scene memory retains only the latest compact color observation for the
running session. Frames are not stored or transmitted.

MuJoCo was selected for quick URDF import, deterministic joint inspection, and
an interactive CPU-capable simulation. Speech recognition is local to avoid API
cost and data transfer. macOS `say` or Ubuntu `espeak-ng` provides offline voice;
sound effects and music are synthesized at runtime. A warm shade-color pulse
represents lamp light in simulation. The target deployment is Ubuntu 24.04,
Python 3.12, four CPU cores, and 8 GB RAM; development validation used macOS.

## Measurements

On an Apple Silicon Mac running macOS 14.4.1, three runs over the same recorded
utterance produced speech-to-intent latencies of 1.2071, 0.5071, and 0.5695 s
(mean 0.7612 s; warm runs 0.507-0.570 s). Peak resident memory was 504.1 MiB.
CPU time was 3.2677 s over the measurement, averaging 143.1% of one core
(about 1.4 cores) with transcription capped at two CPU threads. The transcript
and resolved intent were correct in all
three runs.

Engagement reliability was measured in three guided trials with clear glasses:
direct gaze followed by three disengagement variants (turning away, leaving the
frame, and looking down/elsewhere). Face-visible accuracy, face-absent accuracy,
and overall frame accuracy were each 100% across 360 evaluated frames. This is a
small controlled test, not a population-level reliability claim. The commands
save aggregate JSON locally; no face images are retained.

## Reliability, physical reasoning, and limitations

Engagement uses dwell times to suppress frame flicker. Silence skips one turn;
camera failure yields no invented observation; missing voice/audio preserves
visual behavior; microphone failure ends cleanly. The five-DOF vocabulary is
deliberately bounded, all targets respect imported joint limits, and simulated
motions avoid implying unvalidated torque or collision safety on real hardware.
A physical robot would additionally require actuator feedback, velocity and
acceleration enforcement, collision limits, an emergency stop, watchdogs, and
a hardware-specific controller.

Known limitations: fixed HSV color segmentation supports only six colors and is
sensitive to exposure, lighting, shadows, reflections, and background colors.
Pale or low-saturation objects and hues near yellow/orange or blue/purple
boundaries may be misclassified. Face detection is frontal and may degrade with
glare, occlusion, or dim light; speech uses fixed English phrases and five-second turns; memory is
single-object and nonpersistent; the camera and simulated lamp do not share a
calibrated physical frame; the shade pulse is visual rather than photometric;
and Ubuntu behavior remains to be verified on the final target laptop.
