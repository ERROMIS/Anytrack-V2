from PySide6.QtGui import QAction
from PySide6.QtWidgets import QWidget

from src.pattern_tracking.logic.tracker.TrackerManager import TrackerManager
from src.pattern_tracking.qt_gui.dock_widgets.LivePlotterDockWidget import LivePlotterDockWidget
from src.pattern_tracking.qt_gui.generic.GenericAssets import GenericAssets
from src.pattern_tracking.qt_gui.top_menu_bar.plot.NewPlotQDialog import NewPlotQDialog


class CreatePlotAction(QAction):
    """
    Menu bar action that opens a dialog to create a new distance plot
    between two active trackers in the scene.
    """

    def __init__(self,
                 tracker_manager: TrackerManager,
                 plot_widget: LivePlotterDockWidget,
                 parent: QWidget = None):
        """
        Initializes the action and connects it to its trigger method.

        Args:
            tracker_manager (TrackerManager): The object managing active trackers.
            plot_widget (LivePlotterDockWidget): The widget where the new plot will be displayed.
            parent (QWidget, optional): Optional parent widget for this action.
        """
        super().__init__(parent=parent, text="Create plot")
        self._PLOTS_CONTAINER = plot_widget
        self._TRACKER_MANAGER = tracker_manager
        self.triggered.connect(self._new_plot_dialog)

    def _new_plot_dialog(self):
        """
        Opens the dialog to create a new distance plot.
        Ensures at least 2 trackers are active before proceeding.
        """
        available_trackers = list(self._TRACKER_MANAGER.alive_trackers().values())

        if len(available_trackers) < 2:
            GenericAssets.popup_message(
                title="Error: Not enough trackers",
                message=(
                    "You need at least 2 different trackers to start plotting distances.\n"
                    "Please create a new tracker using the top-left tabs."
                ),
                is_error=True
            )
            return

        # Open the dialog for selecting trackers and plot options
        dialog = NewPlotQDialog(available_trackers)

        if dialog.exec():
            self._PLOTS_CONTAINER.new_plot(
                dialog.get_resulting_dist_observer(),
                dialog.get_resulting_fps(),
                dialog.get_resulting_title()
            )