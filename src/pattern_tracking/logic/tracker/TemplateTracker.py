import numpy as np

from src.pattern_tracking.shared import utils, constants
from src.pattern_tracking.logic.tracker.AbstractTracker import AbstractTracker
from src.pattern_tracking.objects.RegionOfInterest import RegionOfInterest


class TemplateTracker(AbstractTracker):
    """
    Tracker that uses template matching to locate a POI (pattern of interest)
    within a video frame or a defined detection region.

    Inherits from AbstractTracker and implements the core `update` method
    using OpenCV's template matching utilities.

    Attributes:
        name (str): User-defined name of the tracker.
        tracker_size (tuple[int, int]): Default size (w, h) for template regions.
    """

    def __init__(self, name: str, tracker_size: tuple[int, int] = (50, 50)) -> None:
        """
        Initialize a TemplateTracker instance.

        Args:
            name (str): The name of this tracker.
            tracker_size (tuple[int, int]): Size in pixels of the template to track.
        """
        super().__init__(name, tracker_size=tracker_size)

    def update(self, base_frame: np.ndarray, drawing_frame: np.ndarray) -> None:
        """
        Core tracking method.

        Locates the POI within the frame using template matching, and stores
        the result in `self._found_poi`. Draws the POI if found and in bounds.

        Args:
            base_frame (np.ndarray): Frame in which to search the POI.
            drawing_frame (np.ndarray): Frame on which to draw visual output.
        """
        super().update(base_frame, drawing_frame)

        # Skip if no template is defined
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

        # Determine drawing logic
        if self._detection_region.is_undefined():
            if not self._found_poi.is_undefined():
                self._draw_poi(self._found_poi.get_coords())
        else:
            if self._detection_region.intersects(self._template_poi):
                self._draw_poi(self._found_poi.get_coords())