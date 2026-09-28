"""Tests for stable character engagement transitions."""

from live_character_robot.engagement import EngagementEvent, EngagementTracker


def test_engages_only_after_continuous_visibility() -> None:
    """A brief face detection must not immediately engage the character."""
    tracker = EngagementTracker(engage_after=1.0)

    assert tracker.update(True, now=10.0) is EngagementEvent.NONE
    assert tracker.update(True, now=10.9) is EngagementEvent.NONE
    assert tracker.update(True, now=11.0) is EngagementEvent.ENGAGED
    assert tracker.engaged is True


def test_visibility_gap_resets_engagement_dwell() -> None:
    """The visible dwell timer should restart after a missed observation."""
    tracker = EngagementTracker(engage_after=1.0)

    tracker.update(True, now=10.0)
    tracker.update(False, now=10.8)
    assert tracker.update(True, now=11.0) is EngagementEvent.NONE
    assert tracker.update(True, now=12.0) is EngagementEvent.ENGAGED


def test_disengages_only_after_sustained_absence() -> None:
    """One dropped detection must not make an engaged character look away."""
    tracker = EngagementTracker(engage_after=0.0, disengage_after=1.5)
    tracker.update(True, now=1.0)

    assert tracker.update(False, now=2.0) is EngagementEvent.NONE
    assert tracker.update(False, now=3.4) is EngagementEvent.NONE
    assert tracker.update(False, now=3.5) is EngagementEvent.DISENGAGED
    assert tracker.engaged is False


def test_reacquired_face_cancels_pending_disengagement() -> None:
    """Seeing the face again should clear a pending absence transition."""
    tracker = EngagementTracker(engage_after=0.0, disengage_after=1.0)
    tracker.update(True, now=1.0)
    tracker.update(False, now=2.0)

    assert tracker.update(True, now=2.5) is EngagementEvent.NONE
    assert tracker.update(False, now=3.0) is EngagementEvent.NONE
    assert tracker.update(False, now=4.0) is EngagementEvent.DISENGAGED
