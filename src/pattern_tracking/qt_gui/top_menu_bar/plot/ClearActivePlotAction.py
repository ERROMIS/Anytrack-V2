from PySide6.QtGui import QAction

from src.pattern_tracking.qt_gui.dock_widgets.LivePlotterDockWidget import LivePlotterDockWidget


class ClearActivePlotAction(QAction):
    """
    QAction for clearing the currently displayed active plot in the plot widget dock.
    This action is typically added to a menu or toolbar.
    """

    def __init__(self, plot_widget_dock: LivePlotterDockWidget):
        """
        Initializes the action and connects it to the clear_active_plot method
        of the LivePlotterDockWidget.

        Args:
            plot_widget_dock (LivePlotterDockWidget): The widget managing plot display.
        """
        super().__init__(text="Clear active plot")
        self.triggered.connect(plot_widget_dock.clear_active_plot)