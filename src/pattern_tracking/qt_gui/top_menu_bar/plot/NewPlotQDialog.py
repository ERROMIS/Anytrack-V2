from PySide6.QtGui import QIntValidator
from PySide6.QtWidgets import (
    QDialog, QWidget, QComboBox, QVBoxLayout, QDialogButtonBox,
    QLabel, QHBoxLayout, QLineEdit, QApplication
)

from src.pattern_tracking.logic.DistanceComputer import DistanceComputer
from src.pattern_tracking.qt_gui.generic.GenericAssets import GenericAssets
from src.pattern_tracking.logic.tracker.AbstractTracker import AbstractTracker
from src.pattern_tracking.logic.tracker.PatternTracker import PatternTracker


class NewPlotQDialog(QDialog):
    """
    Dialog to create a new live distance plot between two trackers.
    FPS is pre-filled from the video reader when available.
    """

    def __init__(self,
                 available_trackers: list[AbstractTracker],
                 detected_fps: int | None = None,
                 parent: QWidget = None):
        super().__init__(parent)

        self._plot_title_result: str | None = None
        self._dist_observer_result: DistanceComputer | None = None
        self._feed_fps_result: int | None = None

        layout = QVBoxLayout()
        self._tracker_choice_one = QComboBox()
        self._tracker_choice_two = QComboBox()
        for tracker in available_trackers:
            self._tracker_choice_one.addItem(tracker.get_name(), tracker)
            self._tracker_choice_two.addItem(tracker.get_name(), tracker)

        # Plot name
        row_name = QHBoxLayout()
        row_name.addWidget(QLabel("Plot name"))
        self._plot_name_line_edit = QLineEdit()
        row_name.addWidget(self._plot_name_line_edit)
        layout.addLayout(row_name)

        # FPS — pre-filled if detected from video, editable as fallback
        row_fps = QHBoxLayout()
        fps_label = QLabel("FPS")
        if detected_fps is not None:
            fps_label.setToolTip("Auto-detected from the video file")
        row_fps.addWidget(fps_label)
        self._feed_fps_line_edit = QLineEdit()
        self._feed_fps_line_edit.setValidator(QIntValidator(1, 1000, self))
        if detected_fps is not None:
            self._feed_fps_line_edit.setText(str(detected_fps))
        row_fps.addWidget(self._feed_fps_line_edit)
        layout.addLayout(row_fps)

        # Tracker selections
        layout.addWidget(QLabel("Select the two trackers to compare"))
        row_one = QHBoxLayout()
        row_one.addWidget(QLabel("Tracker 1"))
        row_one.addWidget(self._tracker_choice_one)
        layout.addLayout(row_one)

        row_two = QHBoxLayout()
        row_two.addWidget(QLabel("Tracker 2"))
        row_two.addWidget(self._tracker_choice_two)
        layout.addLayout(row_two)

        # Buttons
        buttons = QDialogButtonBox(self)
        buttons.addButton(QDialogButtonBox.Ok)
        buttons.addButton(QDialogButtonBox.Cancel)
        buttons.button(QDialogButtonBox.Ok).clicked.connect(self.validate)
        buttons.button(QDialogButtonBox.Cancel).clicked.connect(self.reject)
        layout.addWidget(buttons)

        self.setLayout(layout)

    def validate(self):
        tracker_one = self._tracker_choice_one.currentData()
        tracker_two = self._tracker_choice_two.currentData()
        plot_name = self._plot_name_line_edit.text().strip()

        try:
            feed_fps = int(self._feed_fps_line_edit.text().strip())
            if feed_fps <= 0:
                raise ValueError("FPS must be strictly positive.")

            dist_observer = DistanceComputer(plot_name, tracker_one, tracker_two)

            self._plot_title_result = plot_name
            self._feed_fps_result = feed_fps
            self._dist_observer_result = dist_observer

            GenericAssets.popup_message("Success", "New plot created", is_error=False)
            self.accept()

        except ValueError as err:
            GenericAssets.popup_message("Invalid parameters", str(err), is_error=True)

    def get_resulting_dist_observer(self) -> DistanceComputer | None:
        return self._dist_observer_result

    def get_resulting_fps(self) -> int | None:
        return self._feed_fps_result

    def get_resulting_title(self) -> str | None:
        return self._plot_title_result


if __name__ == '__main__':
    app = QApplication()
    window = NewPlotQDialog([PatternTracker("a"), PatternTracker("g")])
    window.exec()
