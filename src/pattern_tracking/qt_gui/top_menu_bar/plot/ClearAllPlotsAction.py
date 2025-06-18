from PySide6.QtGui import QAction

from src.pattern_tracking.qt_gui.dock_widgets.LivePlotterDockWidget import LivePlotterDockWidget


class ClearAllPlotsAction(QAction):
    """
    QAction used to clear all existing plots from the live plotter dock widget.
    Typically used in a menu or toolbar.
    """

    def __init__(self, live_plotter_widget: LivePlotterDockWidget):
        """
        Initializes the action and binds it to the clear_all method
        of the LivePlotterDockWidget.

        Args:
            live_plotter_widget (LivePlotterDockWidget): The widget managing all plots.
        """
        super().__init__(text="Clear all plots")
        self.triggered.connect(live_plotter_widget.clear_all)