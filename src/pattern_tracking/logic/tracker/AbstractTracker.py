import uuid
from abc import ABC, abstractmethod
import cv2 as cv
import numpy as np

from src.pattern_tracking.shared import utils
from src.pattern_tracking.objects.RegionOfInterest import RegionOfInterest


class AbstractTracker(ABC):
    """
    Abstract base class for all trackers used in the software.

    This class defines a common interface and structure for trackers
    that aim to detect and track a region of interest (POI) in video frames.
    """

    DEFAULT_POI_COLOR = (255, 255, 255)
    DEFAULT_BOUNDS_COLOR = (0, 255, 0)

    def __init__(self,
                 name: str,
                 poi_rgb: tuple[int, int, int] = DEFAULT_POI_COLOR,
                 detection_bounds_rgb: tuple[int, int, int] = DEFAULT_BOUNDS_COLOR,
                 tracker_size: tuple[int, int] = (50, 50)) -> None:
        """
        Initialize the base tracker attributes.

        Args:
            name (str): Display name of the tracker (should be unique).
            poi_rgb (tuple[int, int, int]): RGB color to highlight the POI.
            detection_bounds_rgb (tuple[int, int, int]): RGB color for detection bounds.
            tracker_size (tuple[int, int]): Default size of the template tracker (in pixels).
        """
        self._id = uuid.uuid4()
        self._name = name
        self._tracker_size = tracker_size

        self._detection_region = RegionOfInterest.new_empty()
        self._template_poi = RegionOfInterest.new_empty()
        self._found_poi = RegionOfInterest.new_empty()

        self._base_frame: cv.Mat | np.ndarray = np.zeros((1, 1), dtype=np.uint8)
        self._drawing_frame: np.ndarray = np.zeros(self._base_frame.shape, dtype=np.uint8)

        self._initialized = False

        self._poi_color = poi_rgb
        self._detection_region_color = detection_bounds_rgb

    # ------------------------
    # Accessors and mutators
    # ------------------------

    def get_edited_frame(self) -> cv.Mat | np.ndarray:
        """
        Returns the edited frame (highlighted drawing frame).

        Returns:
            np.ndarray: Frame with annotations from tracker.
        """
        return self._drawing_frame

    def get_id(self) -> uuid.UUID:
        """
        Returns the unique identifier of this tracker.

        Returns:
            uuid.UUID: Unique ID.
        """
        return self._id

    def get_name(self) -> str:
        """
        Returns the name of the tracker.

        Returns:
            str: Tracker name.
        """
        return self._name

    def get_detection_region(self) -> RegionOfInterest:
        """
        Returns the current detection region.

        Returns:
            RegionOfInterest: Area to restrict POI detection.
        """
        return self._detection_region

    def set_detection_region(self, region: RegionOfInterest) -> None:
        """
        Sets the detection region.

        Args:
            region (RegionOfInterest): Region to restrict search.
        """
        self._detection_region = region

    def set_poi(self, poi: RegionOfInterest) -> None:
        """
        Sets the template POI to track.

        Args:
            poi (RegionOfInterest): Region of interest template.
        """
        self._template_poi = poi

    def get_found_poi_center(self) -> np.ndarray | None:
        """
        Returns the center point of the found POI in the current frame.

        Returns:
            np.ndarray | None: (x, y) coordinates of center, or None if undefined.
        """
        if self._found_poi.is_undefined():
            return None
        return utils.middle_of(*self._found_poi.get_coords())

    # ------------------------
    # Core tracking logic
    # ------------------------

    @abstractmethod
    def update(self, base_frame: np.ndarray, drawing_frame: np.ndarray) -> None:
        """
        Abstract method to be implemented by concrete trackers.

        Must detect the POI within the frame and draw overlays.
        Sets `self._found_poi` when the POI is found.

        Args:
            base_frame (np.ndarray): Source video frame.
            drawing_frame (np.ndarray): Frame to draw highlights on.
        """
        self._base_frame = base_frame
        self._drawing_frame = drawing_frame

        if not self._detection_region.is_undefined():
            self._detection_region.set_parent_image(self._base_frame)
            self._draw_detection_region(self._detection_region.get_coords())

    # ------------------------
    # Drawing utilities
    # ------------------------

    def _draw_poi(self, rect: RegionOfInterest | np.ndarray) -> None:
        """
        Draws a rectangle around the found POI.

        Args:
            rect (RegionOfInterest | np.ndarray): Coordinates or ROI of POI.
        """
        if isinstance(rect, RegionOfInterest):
            pt1, pt2 = map(tuple, rect.get_coords())
        else:
            pt1, pt2 = tuple(rect[0]), tuple(rect[1])

        cv.rectangle(
            self._drawing_frame,
            pt1,
            pt2,
            self._poi_color,
            thickness=2
        )

    def _draw_detection_region(self, rect: RegionOfInterest | np.ndarray) -> None:
        """
        Draws the detection region rectangle on the drawing frame.

        Args:
            rect (RegionOfInterest | np.ndarray): Coordinates or ROI.
        """
        pt1, pt2 = map(tuple, rect) if isinstance(rect, (list, tuple, np.ndarray)) else rect.get_coords()
        cv.rectangle(
            self._drawing_frame,
            pt1,
            pt2,
            self._detection_region_color,
            thickness=2
        )