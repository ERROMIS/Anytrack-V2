from threading import Lock
import numpy as np
from PySide6.QtCore import Qt
from PySide6.QtWidgets import (
    QDockWidget, QWidget, QLabel, QHBoxLayout, QVBoxLayout,
    QPushButton, QScrollArea, QMessageBox, QFileDialog
)

from src.pattern_tracking.logic.DistanceComputer import DistanceComputer
from src.pattern_tracking.qt_gui.widgets.DistancePlotWidget import DistancePlotWidget


class LivePlotterDockWidget(QDockWidget):
    """
    A dockable widget that displays a live distance graph between two trackers.

    Provides controls for plotting, pausing, resuming, clearing, and saving the graph.
    Automatically synchronizes the plot with the video feed.
    """

    WIDGET_SIZE = 800, 240

    def __init__(self, parent: QWidget | None = None):
        """
        Initialize the plot dock widget and set up layout.

        :param parent: The parent QWidget.
        """
        super().__init__(parent)
        self._mutex = Lock()
        self._plot_started = False
        self._active_plot: DistancePlotWidget | None = None
        self._distance_computer: DistanceComputer | None = None
        self._current_frame_number = 0
        self._last_frame_number = -1  

        self._init_empty_widget()
        self.setMinimumSize(*LivePlotterDockWidget.WIDGET_SIZE)
        self.show()

    def _init_empty_widget(self):
        """Display placeholder widget when no plot is active."""
        tmp_widget = QWidget()
        tmp_layout = QHBoxLayout()
        tmp_layout.addWidget(QLabel("No plot defined !"))
        tmp_layout.setAlignment(Qt.AlignmentFlag.AlignCenter)
        tmp_widget.setLayout(tmp_layout)
        self.setWidget(tmp_widget)

    def new_plot(self, dist_computer: DistanceComputer, feed_fps: int, title: str):
        """
        Create a new distance plot for the specified trackers.

        :param dist_computer: DistanceComputer instance for the trackers.
        :param feed_fps: Frames per second of the video feed.
        :param title: Title of the plot.
        """
        if self._active_plot:
            self._active_plot.deleteLater()
        self._distance_computer = dist_computer
        self._active_plot = DistancePlotWidget(feed_fps, plot_title=title)
        self._plot_started = False
        self._set_plot_widget()
        self._update_buttons_state()

    def _set_plot_widget(self):
        """Attach the active plot widget and control buttons to the layout."""
        scroll_area = QScrollArea()
        scroll_area.setWidgetResizable(True)
        scroll_area.setWidget(self._active_plot)

        button_start = QPushButton("Start graph")
        button_resume = QPushButton("Resume plotting")
        button_pause = QPushButton("Pause plotting")
        button_clear = QPushButton("Clear graph")
        button_save = QPushButton("Save graph")

        button_start.clicked.connect(self._start_current_plot)
        button_resume.clicked.connect(self._resume_current_plot)
        button_pause.clicked.connect(self._pause_current_plot)
        button_clear.clicked.connect(self.clear_active_plot)
        button_save.clicked.connect(self._save_active_plot)

        self._button_start = button_start
        self._button_resume = button_resume
        self._button_pause = button_pause
        self._button_clear = button_clear
        self._button_save = button_save

        control_layout = QHBoxLayout()
        control_layout.addWidget(button_start)
        control_layout.addWidget(button_resume)
        control_layout.addWidget(button_pause)
        control_layout.addWidget(button_clear)
        control_layout.addWidget(button_save)

        container = QWidget()
        layout = QVBoxLayout()
        layout.addWidget(scroll_area)
        layout.addLayout(control_layout)
        container.setLayout(layout)

        self.setWidget(container)

    def update_plots(self, frame_number: int):
        """
        Update the plot with a new frame.

        :param frame_number: The current frame number.
        """
        if not self._plot_started or not self._active_plot or not self._distance_computer:
            return

        # Detect loop: if frame_number decreases, the video has restarted
        if hasattr(self, "_last_frame_number") and self._last_frame_number != -1:
            if frame_number < self._last_frame_number:
                print("⛔ Loop detected! Forcing pause.")
                self._plot_started = False
                self._active_plot.stop_plotting()

                reader = self.parent()._LIVE_FEED.get_video_reader()
                if reader:
                    reader.pause()
                    self.parent().get_video_control_widget().set_playing(False)
                    self.parent().set_video_controls_enabled(True)

                self._update_buttons_state(force_end=True)
                return
        else:
            self._last_frame_number = -1  # initialize if missing

        with self._mutex:
            self._current_frame_number = frame_number
            distance = self._distance_computer.distance()
            if distance != DistanceComputer.ERR_DIST:
                stopped = self._active_plot.plot_new_point(
                    self._active_plot.get_feed_fps(), distance, frame_number
                )
                if stopped:
                    print("📉 Plotting stopped (timestamp regression)")
                    self._plot_started = False
                    self._active_plot.stop_plotting()

                    reader = self.parent()._LIVE_FEED.get_video_reader()
                    if reader:
                        reader.pause()
                        self.parent().get_video_control_widget().set_playing(False)
                        self.parent().set_video_controls_enabled(True)

                    self._update_buttons_state(force_end=True)

        self._last_frame_number = frame_number
        self._update_buttons_state()

    def clear_active_plot(self):
        """Clear the current plot and reset the state."""
        if self._active_plot:
            self._active_plot.clear_data()
            self._plot_started = False
            self._last_frame_number = -1 
            self.parent().set_video_controls_enabled(True)
        self._update_buttons_state()

    def _start_current_plot(self):
        """Start plotting from the current position of the video."""
        reader = self.parent()._LIVE_FEED.get_video_reader()
        is_video = reader and getattr(reader, "_is_video", False)

        if self._active_plot:
            self._active_plot.clear_data()
            self._active_plot.set_time_origin(0)
            self._active_plot.resume_plotting()

        if is_video:
            reader.resume()
            self.parent().get_video_control_widget().set_playing(True)

        self._plot_started = True
        self.parent().set_video_controls_enabled(False)
        self._update_buttons_state()

    def _pause_current_plot(self):
        """Pause the current plot and video."""
        if self._active_plot:
            self._active_plot.stop_plotting()
        reader = self.parent()._LIVE_FEED.get_video_reader()
        if reader and getattr(reader, "_is_video", False):
            reader.pause()
            self.parent().get_video_control_widget().set_playing(False)
        self._plot_started = True
        self._update_buttons_state()

    def _resume_current_plot(self):
        """Resume plotting and video playback."""
        if self._active_plot:
            self._active_plot.resume_plotting()
        reader = self.parent()._LIVE_FEED.get_video_reader()
        if reader and getattr(reader, "_is_video", False):
            reader.resume()
            self.parent().get_video_control_widget().set_playing(True)
        self._plot_started = True
        self._update_buttons_state()

    def _save_active_plot(self):
        """Save the currently visible portion of the graph (as PNG) and export data to CSV."""
        if not self._active_plot:
            return

        file_path, _ = QFileDialog.getSaveFileName(self, "Save graph data", filter="CSV Files (*.csv)")
        if not file_path:
            return

        try:
            # --- Save CSV
            data_item = self._active_plot.plotItem.listDataItems()[0]
            x_data, y_data = data_item.getData()
            with open(file_path, "w") as f:
                f.write("time_seconds,distance_px\n")
                for x, y in zip(x_data, y_data):
                    f.write(f"{x},{y}\n")

            # --- Save currently visible graph area as PNG
            image_path = file_path.rsplit('.', 1)[0] + ".png"
            self._active_plot.grab().save(image_path)

            QMessageBox.information(self, "Success", f"Graph saved:\nCSV: {file_path}\nImage: {image_path}")

        except Exception as e:
            QMessageBox.critical(self, "Save Error", f"Failed to save graph:\n{e}")

    def _update_buttons_state(self, force_end: bool = False):
        has_plot = self._active_plot is not None
        is_plotting = self._active_plot.is_plotting() if has_plot else False
        reader = self.parent()._LIVE_FEED.get_video_reader()
        is_video = reader and getattr(reader, "_is_video", False)
        is_paused = reader.is_paused() if is_video else False

        if force_end:
            # End of video reached — only allow save and clear
            self._button_start.setEnabled(False)
            self._button_resume.setEnabled(False)
            self._button_pause.setEnabled(False)
            self._button_clear.setEnabled(True)
            self._button_save.setEnabled(True)
            return

        self._button_start.setEnabled(has_plot and not self._plot_started)
        self._button_resume.setEnabled(has_plot and not is_plotting and self._plot_started)
        self._button_pause.setEnabled(has_plot and is_plotting and self._plot_started)
        self._button_clear.setEnabled(has_plot and self._plot_started and is_paused)
        self._button_save.setEnabled(has_plot and not is_plotting and self._plot_started)

    def clear_all(self):
        """Completely clear the active plot and reset the dock widget state."""
        if self._active_plot:
            self._active_plot.clear_data()
        self._plot_started = False
        self._distance_computer = None
        self._init_empty_widget()
        self._last_frame_number = -1 
        self._update_buttons_state()
        self.parent().set_video_controls_enabled(True)
        self._active_plot = None
        self._current_frame_number = 0
        self._mutex = Lock()
