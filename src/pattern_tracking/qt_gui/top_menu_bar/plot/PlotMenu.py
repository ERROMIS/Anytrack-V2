from PySide6.QtWidgets import QMenu

from src.pattern_tracking.logic.tracker.TrackerManager import TrackerManager
from src.pattern_tracking.logic.video.LiveFeedWrapper import LiveFeedWrapper
from src.pattern_tracking.qt_gui.dock_widgets.LivePlotterDockWidget import LivePlotterDockWidget
from src.pattern_tracking.qt_gui.top_menu_bar.plot.ClearActivePlotAction import ClearActivePlotAction
from src.pattern_tracking.qt_gui.top_menu_bar.plot.ClearAllPlotsAction import ClearAllPlotsAction
from src.pattern_tracking.qt_gui.top_menu_bar.plot.CreatePlotAction import CreatePlotAction


class PlotMenu(QMenu):
    """Menu grouping plot actions: create, clear active, clear all."""

    def __init__(self,
                 tracker_manager: TrackerManager,
                 plot_docker_widget: LivePlotterDockWidget,
                 live_feed: LiveFeedWrapper):
        super().__init__(title="Plots")
        self._create_plot = CreatePlotAction(tracker_manager, plot_docker_widget, live_feed, parent=self)
        self._clear_all = ClearAllPlotsAction(plot_docker_widget)
        self._clear_active = ClearActivePlotAction(plot_docker_widget)
        self.addAction(self._create_plot)
        self.addAction(self._clear_all)
        self.addAction(self._clear_active)
