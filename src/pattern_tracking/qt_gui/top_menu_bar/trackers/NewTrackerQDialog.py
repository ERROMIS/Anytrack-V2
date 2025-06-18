from PySide6.QtCore import QSize
from PySide6.QtWidgets import (
    QDialog, QWidget, QLineEdit, QApplication, QVBoxLayout, QLabel, QComboBox,
    QDialogButtonBox
)

from src.pattern_tracking.logic.tracker.AbstractTracker import AbstractTracker
from src.pattern_tracking.logic.tracker.TrackerManager import TrackerManager
from src.pattern_tracking.qt_gui.generic.GenericAssets import GenericAssets


class NewTrackerQDialog(QDialog):
    """
    Dialog window used to configure and create a new tracker object.

    This class provides the user with a form to select the type, name,
    and size of the tracker. Upon confirmation, it attempts to create
    the tracker and attach it to a TrackerManager.

    Attributes:
        dialog_size (QSize): Fixed size of the dialog window.
        window_title (str): Title displayed on the dialog window.
        _created_tracker (AbstractTracker | None): The tracker created and returned after success.
    """

    dialog_size = QSize(300, 260)
    window_title = "Create a new tracker"

    def __init__(self, tracker_manager: TrackerManager, parent_widget: QWidget = None):
        """
        Initializes the dialog and sets up the UI layout.

        Args:
            tracker_manager (TrackerManager): Manager responsible for creating trackers.
            parent_widget (QWidget, optional): Parent widget.
        """
        super().__init__(parent_widget)
        self._TRACKER_MANAGER = tracker_manager
        self._created_tracker: AbstractTracker | None = None

        self.setModal(True)
        self.setWindowTitle(NewTrackerQDialog.window_title)

        self._init_layout()
        self.setFixedSize(NewTrackerQDialog.dialog_size)

    def _init_layout(self):
        """Initializes and arranges all widgets in the layout."""
        self.layout = QVBoxLayout()
        self.layout.setSpacing(10)
        self.layout.setContentsMargins(10, 10, 10, 10)

        # Tracker name input
        self.layout.addWidget(QLabel("Tracker name"))
        self._input_name = QLineEdit(self)
        self.layout.addWidget(self._input_name)

        # Tracker type selection
        self.layout.addWidget(QLabel("Type of the tracker"))
        self._trackers_combobox = QComboBox(self)
        for t in TrackerManager.available_tracker_types():
            self._trackers_combobox.addItem(t.value.name, t)
        self.layout.addWidget(self._trackers_combobox)

        # Tracker size inputs
        self.layout.addWidget(QLabel("Width of the POI"))
        self._width_input = QLineEdit(self)
        self._width_input.setText("50")
        self.layout.addWidget(self._width_input)

        self.layout.addWidget(QLabel("Height of the POI"))
        self._height_input = QLineEdit(self)
        self._height_input.setText("50")
        self.layout.addWidget(self._height_input)

        # Dialog buttons
        self._buttons_box = QDialogButtonBox(self)
        self._buttons_box.addButton(QDialogButtonBox.Ok)
        self._buttons_box.button(QDialogButtonBox.Ok).clicked.connect(self.validate)
        self._buttons_box.addButton(QDialogButtonBox.Cancel)
        self._buttons_box.button(QDialogButtonBox.Cancel).clicked.connect(self.reject)

        self.layout.addWidget(self._buttons_box)
        self.setLayout(self.layout)

    def validate(self):
        """
        Attempts to create a tracker based on user input.
        Displays feedback and closes the dialog on success.
        """
        new_tracker_name = self._input_name.displayText().strip()
        new_tracker_type = self._trackers_combobox.currentData()
        width = int(self._width_input.text())
        height = int(self._height_input.text())

        valid = False
        title = "Success"
        message = f"New tracker '{new_tracker_name}' created successfully"

        try:
            new_tracker = self._TRACKER_MANAGER.create_tracker(
                new_tracker_name,
                new_tracker_type,
                size=(width, height)
            )
            valid = new_tracker is not None
        except ValueError as err:
            title = "Invalid tracker name"
            message = str(err)
        except KeyError as err:
            title = "Tracker name already exists"
            message = str(err)
        except NotImplementedError as err:
            title = "Tracker not implemented"
            message = str(err)

        GenericAssets.popup_message(title, message, is_error=not valid)

        if valid:
            self._created_tracker = new_tracker
            self.accept()

    def get_created_tracker(self) -> AbstractTracker | None:
        """
        Returns the tracker created by this dialog.

        Returns:
            AbstractTracker | None: The created tracker, or None if creation failed.
        """
        return self._created_tracker


if __name__ == '__main__':
    app = QApplication()
    window = NewTrackerQDialog(TrackerManager())
    window.show()
    app.exec()