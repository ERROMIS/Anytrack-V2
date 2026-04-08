from PySide6.QtGui import QAction
from PySide6.QtWidgets import QWidget

from src.pattern_tracking.logic.tracker.TrackerManager import TrackerManager
from src.pattern_tracking.logic.video.LiveFeedWrapper import LiveFeedWrapper
from src.pattern_tracking.qt_gui.dock_widgets.LivePlotterDockWidget import LivePlotterDockWidget
from src.pattern_tracking.qt_gui.generic.GenericAssets import GenericAssets
from src.pattern_tracking.qt_gui.top_menu_bar.plot.NewPlotQDialog import NewPlotQDialog


class CreatePlotAction(QAction):
    """Menu action that opens the dialog to create a new distance plot."""

    def __init__(self,
                 tracker_manager: TrackerManager,
                 plot_widget: LivePlotterDockWidget,
                 live_feed: LiveFeedWrapper,
                 parent: QWidget = None):
        super().__init__(parent=parent, text="Create plot")
        self._PLOTS_CONTAINER = plot_widget
        self._TRACKER_MANAGER = tracker_manager
        self._live_feed = live_feed
        self.triggered.connect(self._new_plot_dialog)

    def _new_plot_dialog(self):
        available_trackers = list(self._TRACKER_MANAGER.alive_trackers().values())

        if len(available_trackers) < 2:
            GenericAssets.popup_message(
                title="Not enough trackers",
                message="You need at least 2 trackers to plot distances.",
                is_error=True
            )
            return

        # Auto-detect FPS from the video reader if available
        detected_fps: int | None = None
        reader = self._live_feed.get_video_reader()
        if reader:
            fps = reader.get_fps()
            if fps > 0:
                detected_fps = round(fps)

        dialog = NewPlotQDialog(available_trackers, detected_fps=detected_fps)
        if dialog.exec():
            self._PLOTS_CONTAINER.new_plot(
                dialog.get_resulting_dist_observer(),
                dialog.get_resulting_fps(),
                dialog.get_resulting_title()
            )
