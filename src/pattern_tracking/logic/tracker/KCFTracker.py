import cv2 as cv
import numpy as np
from threading import Lock

from src.pattern_tracking.logic.tracker.AbstractTracker import AbstractTracker
from src.pattern_tracking.objects.RegionOfInterest import RegionOfInterest
from src.pattern_tracking.shared import utils


class KCFTracker(AbstractTracker):
    """
    Tracker utilisant l’algorithme OpenCV KCF (Kernelized Correlation Filters).
    Permet de suivre un objet défini par un gabarit initial (template POI),
    et de mettre à jour dynamiquement sa position dans une vidéo.

    Attributs :
        _base_tracker (cv.TrackerKCF): Instance OpenCV du tracker.
        _init_lock (Lock): Sécurise les appels concurrentiels au tracker.
    """

    def __init__(self, name: str, tracker_size: tuple[int, int] = (50, 50)) -> None:
        super().__init__(name, tracker_size=tracker_size)
        self._base_tracker = cv.TrackerKCF_create()
        self._init_lock = Lock()

    def update(self, base_frame: np.ndarray, drawing_frame: np.ndarray) -> None:
        """
        Met à jour la position du POI dans la frame courante.

        Args:
            base_frame (np.ndarray): Image brute à analyser.
            drawing_frame (np.ndarray): Copie à annoter avec la détection.
        """
        super().update(base_frame, drawing_frame)
        if not self._initialized:
            return

        try:
            frame, offset = utils.compute_detection_offset(
                base_frame,
                self._template_poi.get_image(),
                self._detection_region
            )
        except (IndexError, AssertionError):
            return

        # Vérifie que la zone de détection est cohérente
        if not self._detection_region.is_undefined():
            det_w, det_h = self._detection_region.get_xywh()[2:]
            poi_w, poi_h = self._template_poi.get_xywh()[2:]
            if det_w < poi_w or det_h < poi_h:
                return

        with self._init_lock:
            success, bbox = self._base_tracker.update(frame)
            if success:
                x, y, w, h = [int(v) for v in bbox]
                x += offset[0]
                y += offset[1]
                self._found_poi = RegionOfInterest.new(self._base_frame, x, w, y, h)
                self._draw_poi(self._found_poi)

    def set_poi(self, poi: RegionOfInterest) -> None:
        """
        Définit le gabarit de référence à suivre (template).

        Args:
            poi (RegionOfInterest): Région à suivre.
        """
        if poi.is_undefined() or poi.get_image().size == 0:
            print("[KCFTracker] ❌ POI invalide")
            return

        super().set_poi(poi)
        self._found_poi = poi
        self._initialized = True
        self._reset_base_tracker()

    def set_detection_region(self, region: RegionOfInterest) -> None:
        """
        Définit la région de recherche.

        Args:
            region (RegionOfInterest): Zone restreinte à analyser.
        """
        if not self._template_poi.is_undefined():
            reg_w, reg_h = region.get_xywh()[2:]
            poi_w, poi_h = self._template_poi.get_xywh()[2:]
            if reg_w >= poi_w and reg_h >= poi_h:
                self._detection_region = region
                self._reset_base_tracker()

    def _reset_base_tracker(self) -> None:
        """
        Réinitialise le tracker KCF avec la nouvelle zone et le gabarit.
        """
        with self._init_lock:
            self._base_tracker = cv.TrackerKCF_create()
            image = self._base_frame if self._detection_region.is_undefined() else self._detection_region.get_image()

            poi_x, poi_y, poi_w, poi_h = self._template_poi.get_xywh()
            if image is None or image.size == 0 or poi_w == 0 or poi_h == 0:
                print("[KCFTracker] ❌ Image ou POI vide — init annulé")
                return

            if self._detection_region.is_undefined():
                self._base_tracker.init(image, (poi_x, poi_y, poi_w, poi_h))
            else:
                dx, dy = self._template_poi.offset(self._detection_region.get_xywh()[:2], reverse=True)
                self._base_tracker.init(image, (dx, dy, poi_w, poi_h))

    def _draw_poi(self, rect: RegionOfInterest | np.ndarray) -> None:
        """
        Dessine la boîte englobante du POI détecté.
        """
        super()._draw_poi(rect)