from collections import namedtuple
from enum import Enum

from src.pattern_tracking.logic.tracker.PatternTracker import PatternTracker
from src.pattern_tracking.logic.tracker.ReferenceTracker import ReferenceTracker

TrackerTypeData = namedtuple("TrackerTypeData", "name constructor")


class TrackerType(Enum):
    """
    Available tracker types.
    - PatternTracker: tracks a moving region using template matching.
    - ReferenceTracker: holds a fixed reference point (world frame).
    """
    PATTERN_TRACKER = TrackerTypeData("Pattern tracker", PatternTracker)
    REFERENCE_TRACKER = TrackerTypeData("Reference tracker", ReferenceTracker)
