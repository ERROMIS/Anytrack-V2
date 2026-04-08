from typing import Any
from pyqtgraph import PlotWidget
import numpy as np


class DistancePlotWidget(PlotWidget):
    """
    A custom PyQtGraph PlotWidget that displays a live-updated distance graph
    between two trackers over time.

    Time is automatically calculated from the video frame number and the video FPS.
    """

    def __init__(self,
                 feed_fps: int,
                 plot_title: str,
                 parent: Any = None,
                 background: str = 'default',
                 plotItem: Any = None,
                 **kargs: Any) -> None:
        """
        Initialize the distance plot widget.

        Args:
            feed_fps (int): FPS (frames per second) of the video source.
            plot_title (str): Title of the graph.
            parent (Any): Parent widget, if any.
            background (str): Background color of the plot area.
            plotItem (Any): Custom plotItem to use, if provided.
            **kargs (Any): Additional arguments passed to PlotWidget.
        """
        super().__init__(parent, background, plotItem, **kargs)
        self.plotItem.setTitle(plot_title)
        self.plotItem.setLabel("bottom", "Time", units="s")
        self.plotItem.setLabel("left", "Distance", units="px")

        self._feed_fps = feed_fps
        self._start_time: int | None = None
        self._stop_plotting = False
        self._is_plotting = False

    def get_feed_fps(self) -> int:
        """Return the feed's frames per second."""
        return self._feed_fps

    def plot_new_point(self, feed_fps: int, distance: float, current_frame_number: int) -> bool:
        """
        Add a new point to the plot.

        Args:
            feed_fps (int): Video FPS.
            distance (float): Distance to plot (in pixels).
            current_frame_number (int): The frame index of the current sample.

        Returns:
            bool: True if plotting is stopped due to timestamp regression, False otherwise.
        """
        if self._stop_plotting:
            return False

        if self._start_time is None:
            self._start_time = current_frame_number

        new_x = (current_frame_number - self._start_time) / self._feed_fps
        new_y = distance

        if not isinstance(new_x, (int, float)) or not isinstance(new_y, (int, float)):
            return False

        if self.plotItem.listDataItems():
            item = self.plotItem.listDataItems()[0]
            x_data, y_data = item.getData()

            if len(x_data) > 0 and new_x < x_data[-1]:
                self._stop_plotting = True
                self._is_plotting = False
                return True

            x_data = np.append(x_data, new_x).astype(float)
            y_data = np.append(y_data, new_y).astype(float)
            item.setData(x_data, y_data)

            # Scroll the X range with the data (keep 10s window)
            self.plotItem.setXRange(new_x - 10, new_x, padding=0)
        else:
            self.plotItem.plot([new_x], [new_y])

        self._is_plotting = True
        return False

    def clear_data(self) -> None:
        """
        Clear all existing data and reset plot state.
        """
        self.plotItem.clear()
        self._start_time = None
        self._is_plotting = False
        self._stop_plotting = False

    def resume_plotting(self) -> None:
        """Resume plotting after a pause."""
        self._stop_plotting = False
        self._is_plotting = True

    def stop_plotting(self) -> None:
        """Pause live plotting."""
        self._stop_plotting = True
        self._is_plotting = False

    def is_plotting(self) -> bool:
        """
        Check if plotting is active.

        Returns:
            bool: True if plotting is currently active.
        """
        return self._is_plotting

    def set_time_origin(self, origin: float = 0.0) -> None:
        """
        Set the X range of the plot to begin at a specific origin time.

        Args:
            origin (float): Starting point of the X-axis (in seconds).
        """
        self.plotItem.setXRange(origin, origin + 10, padding=0)