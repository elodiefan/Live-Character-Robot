"""Tests for locally synthesized character audio cues."""

import numpy as np

from live_character_robot.audio import SAMPLE_RATE
from live_character_robot.effects import acknowledgment_sound, success_music


def test_acknowledgment_is_short_audible_pcm() -> None:
    """The object-memory effect should be a bounded non-silent PCM clip."""
    samples = acknowledgment_sound()

    assert samples.dtype == np.int16
    assert 0 < len(samples) < SAMPLE_RATE
    assert np.any(samples != 0)


def test_success_music_is_distinct_and_bounded() -> None:
    """The completion melody should be longer than the acknowledgment."""
    acknowledgment = acknowledgment_sound()
    music = success_music()

    assert music.dtype == np.int16
    assert len(acknowledgment) < len(music) < SAMPLE_RATE
    assert np.any(music != 0)
