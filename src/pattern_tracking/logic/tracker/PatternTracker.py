import numpy as np

from src.pattern_tracking.shared import utils, constants
from src.pattern_tracking.logic.tracker.AbstractTracker import AbstractTracker
from src.pattern_tracking.objects.RegionOfInterest import RegionOfInterest


class PatternTracker(AbstractTracker):
    """
    Tracker that uses template matching to locate a POI (pattern of interest)
    within a video frame or a defined detection region.
    """

    def __init__(self, name: str, tracker_size: tuple[int, int] = (50, 50)) -> None:
        super().__init__(name, tracker_size=tracker_size)

    def update(self, base_frame: np.ndarray, drawing_frame: np.ndarray) -> None:
        super().update(base_frame, drawing_frame)

        if self._template_poi.is_undefined():
            return

        try:
            self._found_poi = utils.find_template_in_image(
                self._base_frame,
                self._template_poi.get_image(),
                constants.DETECTION_THRESHOLD,
                detection_bounds=self._detection_region
            )
        except AssertionError:
            self._found_poi = RegionOfInterest.new_empty()

        if self._detection_region.is_undefined():
            if not self._found_poi.is_undefined():
                self._draw_poi(self._found_poi.get_coords())
        else:
            if self._detection_region.intersects(self._template_poi):
                self._draw_poi(self._found_poi.get_coords())
