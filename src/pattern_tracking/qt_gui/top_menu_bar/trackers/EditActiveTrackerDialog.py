from PySide6.QtWidgets import (
    QDialog, QLabel, QLineEdit, QVBoxLayout,
    QDialogButtonBox
)
from src.pattern_tracking.objects.RegionOfInterest import RegionOfInterest


class EditActiveTrackerDialog(QDialog):
    """
    Dialog window used to modify the properties of an active tracker.

    This includes the tracker's name, POI width, and POI height.
    Once validated, the new values are directly applied to the tracker.
    """

    def __init__(self, tracker, parent=None):
        """
        Initializes the dialog for editing an active tracker.

        Args:
            tracker: The tracker object to be edited.
            parent: Optional parent widget.
        """
        super().__init__(parent)
        self.setWindowTitle(f"Edit tracker: {tracker.get_name()}")
        self._tracker = tracker
        self._layout = QVBoxLayout()

        # -- Name field
        self._name_input = QLineEdit(self)
        self._name_input.setText(tracker.get_name())
        self._layout.addWidget(QLabel("Tracker name"))
        self._layout.addWidget(self._name_input)

        # -- Width input
        self._width_input = QLineEdit(self)
        self._width_input.setText(str(tracker._tracker_size[0]))
        self._layout.addWidget(QLabel("POI Width"))
        self._layout.addWidget(self._width_input)

        # -- Height input
        self._height_input = QLineEdit(self)
        self._height_input.setText(str(tracker._tracker_size[1]))
        self._layout.addWidget(QLabel("POI Height"))
        self._layout.addWidget(self._height_input)

        # -- Dialog buttons
        self._buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        self._buttons.accepted.connect(self.accept)
        self._buttons.rejected.connect(self.reject)
        self._layout.addWidget(self._buttons)

        self.setLayout(self._layout)

    def apply_changes(self):
        """
        Applies the modifications made in the dialog to the tracker:
        - Updates name and size
        - Recalculates the POI region based on the new size
        """
        self._tracker._name = self._name_input.text().strip()
        w = int(self._width_input.text())
        h = int(self._height_input.text())
        self._tracker._tracker_size = (w, h)

        center = self._tracker.get_found_poi_center()

        if center is not None:
            cx, cy = center
            new_poi = RegionOfInterest.new(
                self._tracker._base_frame,
                int(cx - w / 2), w,
                int(cy - h / 2), h
            )
            self._tracker.set_poi(new_poi)
        else:
            print("Cannot recenter: POI center not available.")