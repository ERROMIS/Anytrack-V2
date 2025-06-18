import numpy as np

from src.pattern_tracking.logic.tracker.AbstractTracker import AbstractTracker
from src.pattern_tracking.objects.RegionOfInterest import RegionOfInterest


class FixedPointTracker(AbstractTracker):
    """
    A tracker that holds a fixed position and does not perform any detection or tracking.

    This type of tracker is useful for marking a static reference point, such as for
    measuring distances relative to a fixed location in the frame.

    Inherited attributes:
        - _template_poi: Manually defined region of interest.
        - _found_poi: Identical to _template_poi, not automatically updated.
    """

    def __init__(self, name: str, tracker_size: tuple[int, int] = (50, 50)) -> None:
        """
        Initialize a fixed tracker.

        Args:
            name (str): Unique name for the tracker.
            tracker_size (tuple[int, int]): Initial size for the POI (not used).
        """
        super().__init__(name, tracker_size=tracker_size)

    def set_detection_region(self, region: RegionOfInterest) -> None:
        """
        No-op for this tracker type. Detection region is not used.
        
        Args:
            region (RegionOfInterest): Unused parameter.
        """
        pass

    def set_poi(self, poi: RegionOfInterest) -> None:
        """
        Set the fixed region of interest for this tracker.

        Args:
            poi (RegionOfInterest): The fixed location to mark.
        """
        super().set_poi(poi)
        self._found_poi = poi

    def update(self, base_frame: np.ndarray, drawing_frame: np.ndarray) -> None:
        """
        Does not update the POI automatically. Simply draws the fixed location.

        Args:
            base_frame (np.ndarray): Input image (not used).
            drawing_frame (np.ndarray): Output image for overlaying the POI.
        """
        super().update(base_frame, drawing_frame)
        if not self._template_poi.is_undefined():
            self._draw_poi(self._template_poi)