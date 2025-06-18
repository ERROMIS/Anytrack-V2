from PySide6.QtGui import QAction
from src.pattern_tracking.qt_gui.top_menu_bar.trackers.EditActiveTrackerDialog import EditActiveTrackerDialog


class EditActiveTrackerAction(QAction):
    """
    Action used to open a dialog window for editing the currently selected tracker.
    Allows modification of the tracker's name and POI size.
    """

    def __init__(self, tracker_manager, parent=None):
        """
        Initializes the QAction for editing the active tracker.

        Args:
            tracker_manager: The manager that provides access to current trackers.
            parent: Optional parent widget.
        """
        super().__init__("Edit active tracker", parent)
        self._tracker_manager = tracker_manager
        self.triggered.connect(self._edit)

    def _edit(self):
        """
        Slot triggered when the action is activated.
        Opens a dialog to edit the currently selected tracker if available.
        """
        try:
            tracker = self._tracker_manager.get_active_selected_tracker()
        except ValueError:
            print("No active tracker selected.")
            return

        dlg = EditActiveTrackerDialog(tracker)
        if dlg.exec():
            dlg.apply_changes()