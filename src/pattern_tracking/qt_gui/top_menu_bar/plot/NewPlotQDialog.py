from PySide6.QtGui import QIntValidator
from PySide6.QtWidgets import (
    QDialog, QWidget, QComboBox, QVBoxLayout, QDialogButtonBox,
    QLabel, QHBoxLayout, QLineEdit, QApplication
)

from src.pattern_tracking.logic.DistanceComputer import DistanceComputer
from src.pattern_tracking.qt_gui.generic.GenericAssets import GenericAssets
from src.pattern_tracking.logic.tracker.AbstractTracker import AbstractTracker
from src.pattern_tracking.logic.tracker.TemplateTracker import TemplateTracker


class NewPlotQDialog(QDialog):
    """
    Dialog window to create a new live distance plot by selecting two trackers.

    Attributes:
        _plot_title_result (str | None): Name of the plot window provided by the user.
        _dist_observer_result (DistanceComputer | None): Created DistanceComputer object if input is valid.
        _tracker_one (AbstractTracker | None): First selected tracker.
        _tracker_two (AbstractTracker | None): Second selected tracker.
        _feed_fps_result (int | None): FPS entered by the user.
    """

    def __init__(self, available_trackers: list[AbstractTracker], parent: QWidget = None):
        """
        Initializes the dialog with a list of available trackers to choose from.

        Args:
            available_trackers (list[AbstractTracker]): Trackers available in the scene.
            parent (QWidget, optional): Parent widget for the dialog.
        """
        super().__init__(parent)

        self._plot_title_result: str | None = None
        self._dist_observer_result: DistanceComputer | None = None
        self._feed_fps_result: int | None = None

        self._layout = QVBoxLayout()
        self._tracker_choice_one = QComboBox()
        self._tracker_choice_two = QComboBox()
        for tracker in available_trackers:
            self._tracker_choice_one.addItem(tracker.get_name(), tracker)
            self._tracker_choice_two.addItem(tracker.get_name(), tracker)

        # Plot name input
        layout_plot_name = QHBoxLayout()
        layout_plot_name.addWidget(QLabel("Name of the plot window"))
        self._plot_name_line_edit = QLineEdit()
        layout_plot_name.addWidget(self._plot_name_line_edit)
        self._layout.addLayout(layout_plot_name)

        # FPS input
        layout_feed_fps = QHBoxLayout()
        layout_feed_fps.addWidget(QLabel("FPS (Frames Per Second) of the camera"))
        self._feed_fps_line_edit = QLineEdit()
        self._feed_fps_line_edit.setValidator(QIntValidator(1, 1000, self))
        layout_feed_fps.addWidget(self._feed_fps_line_edit)
        self._layout.addLayout(layout_feed_fps)

        # Tracker selections
        self._layout.addWidget(QLabel("Select the two trackers to link"))
        layout_choice_one = QHBoxLayout()
        layout_choice_one.addWidget(QLabel("Tracker one"))
        layout_choice_one.addWidget(self._tracker_choice_one)
        self._layout.addLayout(layout_choice_one)

        layout_choice_two = QHBoxLayout()
        layout_choice_two.addWidget(QLabel("Tracker two"))
        layout_choice_two.addWidget(self._tracker_choice_two)
        self._layout.addLayout(layout_choice_two)

        # OK / Cancel buttons
        self._buttons_box = QDialogButtonBox(self)
        self._buttons_box.addButton(QDialogButtonBox.Ok)
        self._buttons_box.addButton(QDialogButtonBox.Cancel)
        self._buttons_box.button(QDialogButtonBox.Ok).clicked.connect(self.validate)
        self._buttons_box.button(QDialogButtonBox.Cancel).clicked.connect(self.reject)
        self._layout.addWidget(self._buttons_box)

        self.setLayout(self._layout)

    def validate(self):
        """
        Validates the form and creates the DistanceComputer object if inputs are correct.
        Displays an error message if validation fails.
        """
        tracker_one = self._tracker_choice_one.currentData()
        tracker_two = self._tracker_choice_two.currentData()
        plot_name = self._plot_name_line_edit.text().strip()

        try:
            feed_fps = int(self._feed_fps_line_edit.text().strip())
            if feed_fps <= 0:
                raise ValueError("FPS must be strictly positive.")

            dist_observer = DistanceComputer(
                plot_name, tracker_one, tracker_two
            )

            self._plot_title_result = plot_name
            self._feed_fps_result = feed_fps
            self._dist_observer_result = dist_observer

            GenericAssets.popup_message("Success", "A new plot has been created", is_error=False)
            self.accept()

        except ValueError as err:
            GenericAssets.popup_message("Error: Invalid parameters", str(err), is_error=True)

    def get_resulting_dist_observer(self) -> DistanceComputer | None:
        """
        Returns:
            DistanceComputer | None: The resulting observer object.
        """
        return self._dist_observer_result

    def get_resulting_fps(self) -> int | None:
        """
        Returns:
            int | None: The feed FPS provided by the user.
        """
        return self._feed_fps_result

    def get_resulting_title(self) -> str | None:
        """
        Returns:
            str | None: The title of the plot window.
        """
        return self._plot_title_result


if __name__ == '__main__':
    app = QApplication()
    window = NewPlotQDialog([TemplateTracker("a"), TemplateTracker("g")])
    window.exec()