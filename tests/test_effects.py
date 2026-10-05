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
    assert np.max(np.abs(samples.astype(np.int32))) < np.iinfo(np.int16).max


def test_success_music_is_distinct_and_bounded() -> None:
    """The completion melody should be longer and louder than acknowledgment."""
    acknowledgment = acknowledgment_sound()
    music = success_music()

    assert music.dtype == np.int16
    assert len(acknowledgment) < len(music) < SAMPLE_RATE * 2
    assert np.any(music != 0)
    assert np.max(np.abs(music.astype(np.int32))) > np.max(
        np.abs(acknowledgment.astype(np.int32))
    )
    assert np.max(np.abs(music.astype(np.int32))) < np.iinfo(np.int16).max
