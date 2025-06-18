import cv2 as cv
import numpy as np
from PySide6.QtGui import QImage, QPixmap
from src.pattern_tracking.objects.RegionOfInterest import RegionOfInterest


def get_roi(image: np.ndarray, x: int, w: int, y: int, h: int) -> np.ndarray:
    """
    Extracts a region of interest (ROI) from the given image.

    Args:
        image (np.ndarray): Source image.
        x (int): Top-left x coordinate of the ROI.
        w (int): Width of the ROI.
        y (int): Top-left y coordinate of the ROI.
        h (int): Height of the ROI.

    Returns:
        np.ndarray: Cropped region as an image.
    """
    x_edge = min(x + w, image.shape[1])
    y_edge = min(y + h, image.shape[0])
    x = max(0, x)
    y = max(0, y)
    return image[y:y_edge, x:x_edge]


def middle_of(p1: np.ndarray | tuple[int, int], p2: np.ndarray | tuple[int, int]) -> np.ndarray:
    """
    Computes the center point between two coordinates.

    Args:
        p1 (tuple[int, int] | np.ndarray): First point.
        p2 (tuple[int, int] | np.ndarray): Second point.

    Returns:
        np.ndarray: Midpoint as [x, y].
    """
    return np.array([(p1[0] + p2[0]) // 2, (p1[1] + p2[1]) // 2])


def normalize_region(pt1: np.ndarray | tuple[int, int], pt2: np.ndarray | tuple[int, int]) -> np.ndarray:
    """
    Ensures two points define a rectangle from top-left to bottom-right.

    Args:
        pt1 (tuple[int, int] | np.ndarray): One corner.
        pt2 (tuple[int, int] | np.ndarray): Opposite corner.

    Returns:
        np.ndarray: Two normalized corners as [[min_x, min_y], [max_x, max_y]].
    """
    x_min, x_max = sorted([pt1[0], pt2[0]])
    y_min, y_max = sorted([pt1[1], pt2[1]])
    return np.array([[x_min, y_min], [x_max, y_max]])


def find_template_in_image(image: np.ndarray, roi: np.ndarray, detection_threshold: float,
                           detection_bounds: RegionOfInterest = RegionOfInterest.new_empty()) -> RegionOfInterest:
    """
    Searches for a template image (ROI) in a given base image using template matching.

    Args:
        image (np.ndarray): Base image.
        roi (np.ndarray): Template image to search for.
        detection_threshold (float): Match quality threshold.
        detection_bounds (RegionOfInterest, optional): Search bounds.

    Returns:
        RegionOfInterest: Region where the match was found, or empty if none.
    """
    matched_region = RegionOfInterest.new_empty()

    try:
        base, offset = compute_detection_offset(image, roi, detection_bounds)
    except IndexError:
        return matched_region

    if base is None or roi is None or base.size == 0 or roi.size == 0:
        print("❌ Aborted matchTemplate: empty image or template")
        return matched_region

    base = base.astype(np.uint8)
    roi = roi.astype(np.uint8)

    if base.shape[0] < roi.shape[0] or base.shape[1] < roi.shape[1]:
        print("❌ Aborted matchTemplate: template larger than base")
        return matched_region

    confidence_map = cv.matchTemplate(base, roi, cv.TM_CCORR_NORMED)
    _, max_val, _, top_left = cv.minMaxLoc(confidence_map)
    bottom_right = (top_left[0] + roi.shape[1], top_left[1] + roi.shape[0])

    if max_val >= detection_threshold:
        coords = np.array((top_left, bottom_right)) + offset
        matched_region = RegionOfInterest.from_points(image, *coords)

    return matched_region


def compute_detection_offset(base_image: np.ndarray, poi: np.ndarray, detection_bounds: RegionOfInterest) \
        -> tuple[np.ndarray, np.ndarray]:
    """
    Computes the base image and position offset to apply during detection.

    Args:
        base_image (np.ndarray): Full input frame.
        poi (np.ndarray): Template region.
        detection_bounds (RegionOfInterest): Area where search is restricted.

    Returns:
        tuple[np.ndarray, np.ndarray]: (search base image, offset to full image)

    Raises:
        IndexError: If the POI is larger than the detection region.
    """
    if detection_bounds.is_undefined():
        return base_image, np.zeros(2, dtype=int)

    region_img = detection_bounds.get_image()
    if (np.array(poi.shape[:2]) > np.array(region_img.shape[:2])).any():
        raise IndexError("POI is larger than detection bounds")

    offset = detection_bounds.get_coords(RegionOfInterest.PointCoords.TOP_LEFT.value)
    return region_img, offset


def convert_points_to_xwyh(p1, p2) -> tuple[int, int, int, int]:
    """
    Converts two opposite rectangle corners to (x, width, y, height) format.

    Args:
        p1 (tuple[int, int]): Top-left corner.
        p2 (tuple[int, int]): Bottom-right corner.

    Returns:
        tuple[int, int, int, int]: x, width, y, height.
    """
    x, y = p1
    w = p2[0] - p1[0]
    h = p2[1] - p1[1]
    return x, w, y, h


def ndarray_to_qimage(image: np.ndarray,
                      swap_rgb: bool = False,
                      as_qpixmap: bool = False) -> QImage | QPixmap:
    """
    Converts a NumPy RGB image to QImage or QPixmap.

    Args:
        image (np.ndarray): RGB image (HxWx3).
        swap_rgb (bool): Whether to swap RGB to BGR.
        as_qpixmap (bool): Return as QPixmap if True.

    Returns:
        QImage | QPixmap: Converted image.
    """
    height, width, _ = image.shape
    bytes_per_line = 3 * width
    q_img = QImage(image.data, width, height, bytes_per_line, QImage.Format_RGB888)

    if swap_rgb:
        q_img = q_img.rgbSwapped()

    return q_img if not as_qpixmap else QPixmap(q_img)


def opencv_list_available_camera_ports() -> tuple[list[int], list[int], list[int]]:
    """
    Probes available camera ports.

    Returns:
        tuple[list[int], list[int], list[int]]: (available, working, non-working ports)

    Source:
        https://stackoverflow.com/a/62639343
    """
    non_working_ports = []
    dev_port = 0
    working_ports = []
    available_ports = []

    while len(non_working_ports) < 6:
        camera = cv.VideoCapture(dev_port)
        if not camera.isOpened():
            non_working_ports.append(dev_port)
        else:
            is_reading, _ = camera.read()
            if is_reading:
                working_ports.append(dev_port)
            else:
                available_ports.append(dev_port)
        dev_port += 1

    return available_ports, working_ports, non_working_ports