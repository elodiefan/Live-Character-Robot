"""Tests for shared live-camera engagement transitions."""

from live_character_robot.engagement import EngagementEvent
from live_character_robot.live_camera import CameraMonitor


def test_monitor_publishes_engagement_and_disengagement() -> None:
    """Stable face transitions should become session-level signals."""
    monitor = CameraMonitor()
    monitor.tracker.engage_after = 1.0
    monitor.tracker.disengage_after = 1.5

    assert monitor.update_engagement(True, 1.0) is EngagementEvent.NONE
    assert monitor.update_engagement(True, 2.0) is EngagementEvent.ENGAGED
    assert monitor.disengaged is False
    assert monitor.update_engagement(False, 3.0) is EngagementEvent.NONE
    assert monitor.update_engagement(False, 4.5) is EngagementEvent.DISENGAGED
    assert monitor.disengaged is True


def test_recognized_speech_refreshes_engagement() -> None:
    """An active utterance should recover from face occlusion by an object."""
    monitor = CameraMonitor()
    monitor.tracker.engage_after = 0.0
    monitor.tracker.disengage_after = 1.5
    monitor.update_engagement(True, 1.0)
    monitor.update_engagement(False, 2.0)
    monitor.update_engagement(False, 3.5)
    assert monitor.disengaged is True

    monitor.mark_active_interaction()

    assert monitor.disengaged is False
    assert monitor.tracker.engaged is True
    assert monitor.update_engagement(False, 4.0) is EngagementEvent.NONE
    assert monitor.update_engagement(False, 5.5) is EngagementEvent.DISENGAGED
