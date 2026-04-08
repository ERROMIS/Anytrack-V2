from threading import Lock

from PySide6.QtCore import Qt, Signal, Slot
from PySide6.QtWidgets import (
    QDockWidget, QWidget, QLabel, QHBoxLayout, QVBoxLayout,
    QPushButton, QScrollArea, QMessageBox, QFileDialog
)

from src.pattern_tracking.logic.DistanceComputer import DistanceComputer
from src.pattern_tracking.logic.video.LiveFeedWrapper import LiveFeedWrapper
from src.pattern_tracking.qt_gui.widgets.DistancePlotWidget import DistancePlotWidget


class LivePlotterDockWidget(QDockWidget):
    """
    Dockable widget displaying a live distance plot between two trackers.
    Supports one plot at a time — creating a new one replaces the previous.

    Communicates playback intent to the parent via signals.
    update_plots() is a Qt Slot so it can be safely called from the main thread
    via a queued signal connection from BackgroundComputation.
    """

    WIDGET_SIZE = 800, 240

    playback_play_requested = Signal()
    playback_pause_requested = Signal()
    video_controls_enabled_changed = Signal(bool)
    """Emitted with True to enable video controls, False to disable them."""

    def __init__(self, live_feed: LiveFeedWrapper, parent: QWidget | None = None):
        super().__init__(parent)
        self._live_feed = live_feed
        self._mutex = Lock()
        self._active_plot: DistancePlotWidget | None = None
        self._distance_computer: DistanceComputer | None = None
        self._plot_started = False
        self._last_frame_number = -1

        self._build_layout()
        self.setMinimumSize(*LivePlotterDockWidget.WIDGET_SIZE)
        self.show()

    # ------------------------------------------------------------------
    # Layout (built once, updated in-place)
    # ------------------------------------------------------------------

    @staticmethod
    def _make_empty_label() -> QLabel:
        """Create a fresh placeholder label. Must be recreated each time — Qt takes
        ownership when passed to setWidget() and deletes it when replaced."""
        label = QLabel("No plot defined !")
        label.setAlignment(Qt.AlignmentFlag.AlignCenter)
        return label

    def _build_layout(self):
        self._scroll_area = QScrollArea()
        self._scroll_area.setWidgetResizable(True)
        self._scroll_area.setWidget(self._make_empty_label())

        self._button_start = QPushButton("Start")
        self._button_resume = QPushButton("Resume")
        self._button_pause = QPushButton("Pause")
        self._button_clear = QPushButton("Clear")
        self._button_save = QPushButton("Save")

        self._button_start.clicked.connect(self._start_current_plot)
        self._button_resume.clicked.connect(self._resume_current_plot)
        self._button_pause.clicked.connect(self._pause_current_plot)
        self._button_clear.clicked.connect(self.clear_active_plot)
        self._button_save.clicked.connect(self._save_active_plot)

        controls = QHBoxLayout()
        controls.addWidget(self._button_start)
        controls.addWidget(self._button_resume)
        controls.addWidget(self._button_pause)
        controls.addWidget(self._button_clear)
        controls.addWidget(self._button_save)
        self._controls_widget = QWidget()
        self._controls_widget.setLayout(controls)
        self._controls_widget.setVisible(False)

        outer_layout = QVBoxLayout()
        outer_layout.addWidget(self._scroll_area)
        outer_layout.addWidget(self._controls_widget)
        outer = QWidget()
        outer.setLayout(outer_layout)
        self.setWidget(outer)

        self._update_buttons_state()

    # ------------------------------------------------------------------
    # Public API
    # ------------------------------------------------------------------

    def new_plot(self, dist_computer: DistanceComputer, feed_fps: int, title: str):
        """Create a new plot, replacing the previous one."""
        if self._active_plot is not None:
            self._active_plot.clear_data()

        self._distance_computer = dist_computer
        self._active_plot = DistancePlotWidget(feed_fps, plot_title=title)
        self._plot_started = False
        self._last_frame_number = -1

        self._scroll_area.setWidget(self._active_plot)
        self._controls_widget.setVisible(True)
        self._update_buttons_state()

    @Slot(int)
    def update_plots(self, frame_number: int):
        """
        Update the active plot with the current frame number.
        Called via a queued Qt signal from BackgroundComputation — always runs on main thread.
        """
        if not self._plot_started or self._active_plot is None or self._distance_computer is None:
            return

        if self._last_frame_number != -1 and frame_number < self._last_frame_number:
            self._plot_started = False
            self._active_plot.stop_plotting()
            self.playback_pause_requested.emit()
            self.video_controls_enabled_changed.emit(True)   # re-enable controls
            self._update_buttons_state(force_end=True)
            return

        with self._mutex:
            distance = self._distance_computer.distance()
            if distance != DistanceComputer.ERR_DIST:
                stopped = self._active_plot.plot_new_point(
                    self._active_plot.get_feed_fps(), distance, frame_number
                )
                if stopped:
                    self._plot_started = False
                    self._active_plot.stop_plotting()
                    self.playback_pause_requested.emit()
                    self.video_controls_enabled_changed.emit(True)   # re-enable controls
                    self._update_buttons_state(force_end=True)
                    return

        self._last_frame_number = frame_number

    def clear_active_plot(self):
        if self._active_plot is None:
            return
        self._active_plot.clear_data()
        self._plot_started = False
        self._last_frame_number = -1
        self.video_controls_enabled_changed.emit(True)   # re-enable controls
        self._update_buttons_state()

    def clear_all(self):
        """Remove the plot and reset the dock widget."""
        if self._active_plot is not None:
            self._active_plot.clear_data()
        self._active_plot = None
        self._distance_computer = None
        self._plot_started = False
        self._last_frame_number = -1
        self._scroll_area.setWidget(self._make_empty_label())
        self._controls_widget.setVisible(False)
        self.video_controls_enabled_changed.emit(True)   # re-enable controls

    # ------------------------------------------------------------------
    # Private — plot controls
    # ------------------------------------------------------------------

    def _start_current_plot(self):
        if self._active_plot is None:
            return
        self._active_plot.clear_data()
        self._active_plot.set_time_origin(0)
        self._active_plot.resume_plotting()
        self._plot_started = True
        self._last_frame_number = -1
        self.playback_play_requested.emit()
        self.video_controls_enabled_changed.emit(False)  # disable controls while recording
        self._update_buttons_state()

    def _pause_current_plot(self):
        if self._active_plot is None:
            return
        self._active_plot.stop_plotting()
        self.playback_pause_requested.emit()
        self._update_buttons_state()

    def _resume_current_plot(self):
        if self._active_plot is None:
            return
        self._active_plot.resume_plotting()
        self.playback_play_requested.emit()
        self._update_buttons_state()

    def _save_active_plot(self):
        if self._active_plot is None:
            return

        file_path, _ = QFileDialog.getSaveFileName(self, "Save graph data", filter="CSV Files (*.csv)")
        if not file_path:
            return

        try:
            data_item = self._active_plot.plotItem.listDataItems()[0]
            x_data, y_data = data_item.getData()
            with open(file_path, "w") as f:
                f.write("time_seconds,distance_px\n")
                for x, y in zip(x_data, y_data):
                    f.write(f"{x},{y}\n")

            image_path = file_path.rsplit('.', 1)[0] + ".png"
            self._active_plot.grab().save(image_path)

            QMessageBox.information(self, "Saved", f"CSV: {file_path}\nImage: {image_path}")

        except Exception as e:
            QMessageBox.critical(self, "Save Error", f"Failed to save graph:\n{e}")

    def _update_buttons_state(self, force_end: bool = False):
        has_plot = self._active_plot is not None
        if not has_plot:
            for btn in (self._button_start, self._button_resume, self._button_pause,
                        self._button_clear, self._button_save):
                btn.setEnabled(False)
            return

        is_plotting = self._active_plot.is_plotting()
        reader = self._live_feed.get_video_reader()
        is_paused = reader.is_paused() if reader else False

        if force_end:
            self._button_start.setEnabled(False)
            self._button_resume.setEnabled(False)
            self._button_pause.setEnabled(False)
            self._button_clear.setEnabled(True)
            self._button_save.setEnabled(True)
            return

        self._button_start.setEnabled(not self._plot_started)
        self._button_resume.setEnabled(not is_plotting and self._plot_started)
        self._button_pause.setEnabled(is_plotting and self._plot_started)
        self._button_clear.setEnabled(self._plot_started and is_paused)
        self._button_save.setEnabled(not is_plotting and self._plot_started)
