from PySide6.QtWidgets import QMenu

from src.pattern_tracking.logic.tracker.TrackerManager import TrackerManager
from src.pattern_tracking.qt_gui.dock_widgets.LivePlotterDockWidget import LivePlotterDockWidget
from src.pattern_tracking.qt_gui.top_menu_bar.plot.ClearActivePlotAction import ClearActivePlotAction
from src.pattern_tracking.qt_gui.top_menu_bar.plot.ClearAllPlotsAction import ClearAllPlotsAction
from src.pattern_tracking.qt_gui.top_menu_bar.plot.CreatePlotAction import CreatePlotAction


class PlotMenu(QMenu):
    """
    Custom QMenu that groups actions related to live plotting:
    creating new plots, clearing the active plot, or clearing all plots.
    """

    def __init__(self,
                 tracker_manager: TrackerManager,
                 plot_docker_widget: LivePlotterDockWidget):
        """
        Initializes the plot menu and adds all related actions.

        Args:
            tracker_manager (TrackerManager): The manager holding all active trackers.
            plot_docker_widget (LivePlotterDockWidget): The widget displaying the plots.
        """
        super().__init__(title="Plots")

        # Create and store the plotting-related actions
        self._CREATE_PLOT_ACTION = CreatePlotAction(tracker_manager, plot_docker_widget)
        self._CLEAR_ACTIVE_PLOT_ACTION = ClearActivePlotAction(plot_docker_widget)
        self._CLEAR_ALL_PLOTS_ACTION = ClearAllPlotsAction(plot_docker_widget)

        # Add actions to the menu
        self.addAction(self._CREATE_PLOT_ACTION)
        self.addAction(self._CLEAR_ALL_PLOTS_ACTION)
        self.addAction(self._CLEAR_ACTIVE_PLOT_ACTION)