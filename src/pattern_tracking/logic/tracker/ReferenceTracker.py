import numpy as np

from src.pattern_tracking.logic.tracker.AbstractTracker import AbstractTracker
from src.pattern_tracking.objects.RegionOfInterest import RegionOfInterest


class ReferenceTracker(AbstractTracker):
    """
    A tracker that holds a fixed position and does not perform any detection.

    Used to mark a static reference point (world frame), for measuring
    distances relative to a fixed location in the frame.
    """

    def __init__(self, name: str, tracker_size: tuple[int, int] = (50, 50)) -> None:
        super().__init__(name, tracker_size=tracker_size)

    def set_detection_region(self, region: RegionOfInterest) -> None:
        """No-op: detection region is not applicable to a fixed reference."""
        pass

    def set_poi(self, poi: RegionOfInterest) -> None:
        super().set_poi(poi)
        self._found_poi = poi

    def update(self, base_frame: np.ndarray, drawing_frame: np.ndarray) -> None:
        super().update(base_frame, drawing_frame)
        if not self._template_poi.is_undefined():
            self._draw_poi(self._template_poi)
