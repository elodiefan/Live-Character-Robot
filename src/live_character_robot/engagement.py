"""Stable engagement state derived from noisy frame-level observations."""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum


class EngagementEvent(Enum):
    """A meaningful change in the character's attention state."""

    NONE = "none"
    ENGAGED = "engaged"
    DISENGAGED = "disengaged"


@dataclass
class EngagementTracker:
    """Apply dwell times so brief detection flicker does not change state."""

    engage_after: float = 0.75
    disengage_after: float = 1.5
    engaged: bool = False
    _visible_since: float | None = None
    _absent_since: float | None = None

    def update(self, face_visible: bool, now: float) -> EngagementEvent:
        """Update attention state from a timestamped frontal-face observation."""
        if face_visible:
            self._absent_since = None
            if self._visible_since is None:
                self._visible_since = now
            if not self.engaged and now - self._visible_since >= self.engage_after:
                self.engaged = True
                return EngagementEvent.ENGAGED
            return EngagementEvent.NONE

        self._visible_since = None
        if self._absent_since is None:
            self._absent_since = now
        if self.engaged and now - self._absent_since >= self.disengage_after:
            self.engaged = False
            return EngagementEvent.DISENGAGED
        return EngagementEvent.NONE
