from PySide6.QtCore import Qt
from PySide6.QtWidgets import QMainWindow, QWidget, QVBoxLayout

from src.pattern_tracking.logic.video.LiveFeedWrapper import LiveFeedWrapper
from src.pattern_tracking.qt_gui.dock_widgets.LivePlotterDockWidget import LivePlotterDockWidget
from src.pattern_tracking.qt_gui.top_menu_bar.plot.PlotMenu import PlotMenu
from src.pattern_tracking.qt_gui.top_menu_bar.trackers.TrackersMenu import TrackersMenu
from src.pattern_tracking.logic.tracker import TrackerManager
from src.pattern_tracking.qt_gui.widgets.FrameDisplayWidget import FrameDisplayWidget
from src.pattern_tracking.qt_gui.top_menu_bar.video.VideoMenu import VideoMenu
from src.pattern_tracking.qt_gui.widgets.VideoControlWidget import VideoControlWidget
from src.pattern_tracking.qt_gui.widgets.ContrastControlWidget import ContrastControlWidget


class AppMainWindow(QMainWindow):
    """
    Main application window. Wires together the video feed, trackers,
    plot widget, and media controls via Qt signals.
    """

    def __init__(self, tracker_manager: TrackerManager, live_feed: LiveFeedWrapper):
        super().__init__()
        self.setWindowTitle("Anytrack")
        self._TRACKER_MANAGER = tracker_manager
        self._LIVE_FEED = live_feed

        # -- Widgets
        self._FRAME_DISPLAY = FrameDisplayWidget(tracker_manager)
        self._PLOTS_CONTAINER_WIDGET = LivePlotterDockWidget(live_feed, parent=self)
        self._VIDEO_CONTROL_WIDGET = VideoControlWidget()
        self._VIDEO_CONTROL_WIDGET.setVisible(False)
        self._CONTRAST_WIDGET = ContrastControlWidget()
        self._contrast_level = 100

        # -- Signal connections
        self._CONTRAST_WIDGET.contrast_changed.connect(self._on_contrast_changed)
        self._VIDEO_CONTROL_WIDGET.play_pause_clicked.connect(self._toggle_video_playback)
        self._VIDEO_CONTROL_WIDGET.slider_moved.connect(self._seek_video_frame)

        self._PLOTS_CONTAINER_WIDGET.playback_play_requested.connect(self._on_plot_play)
        self._PLOTS_CONTAINER_WIDGET.playback_pause_requested.connect(self._on_plot_pause)
        self._PLOTS_CONTAINER_WIDGET.video_controls_enabled_changed.connect(self.set_video_controls_enabled)

        # -- Menus
        self._VIDEO_MENU = VideoMenu(live_feed, parent=self)
        self._TRACKERS_MENU = TrackersMenu(tracker_manager, parent=self)
        self._PLOTS_MENU = PlotMenu(tracker_manager, self._PLOTS_CONTAINER_WIDGET, live_feed)

        self.menuBar().addMenu(self._VIDEO_MENU)
        self.menuBar().addMenu(self._TRACKERS_MENU)
        self.menuBar().addMenu(self._PLOTS_MENU)
        self.addDockWidget(Qt.RightDockWidgetArea, self._PLOTS_CONTAINER_WIDGET)

        central = QWidget()
        layout = QVBoxLayout()
        layout.addWidget(self._FRAME_DISPLAY)
        layout.addWidget(self._VIDEO_CONTROL_WIDGET)
        layout.addWidget(self._CONTRAST_WIDGET)
        central.setLayout(layout)
        self.setCentralWidget(central)

    # -- Accessors

    def get_frame_display_widget(self) -> FrameDisplayWidget:
        return self._FRAME_DISPLAY

    def get_plot_container_widget(self) -> LivePlotterDockWidget:
        return self._PLOTS_CONTAINER_WIDGET

    def get_video_control_widget(self) -> VideoControlWidget:
        return self._VIDEO_CONTROL_WIDGET

    def get_contrast_level(self) -> int:
        return self._contrast_level

    # -- Video playback handlers

    def _toggle_video_playback(self):
        reader = self._LIVE_FEED.get_video_reader()
        if reader is None:
            return
        if reader.is_paused():
            reader.resume()
            self._VIDEO_CONTROL_WIDGET.set_playing(True)
        else:
            reader.pause()
            self._VIDEO_CONTROL_WIDGET.set_playing(False)

    def _seek_video_frame(self, frame_number: int):
        reader = self._LIVE_FEED.get_video_reader()
        if reader is not None:
            reader.seek(frame_number)
            self._VIDEO_CONTROL_WIDGET.update_slider_position(frame_number)

    def _on_plot_play(self):
        """Resume video when the plot requests playback."""
        reader = self._LIVE_FEED.get_video_reader()
        if reader:
            reader.resume()
            self._VIDEO_CONTROL_WIDGET.set_playing(True)

    def _on_plot_pause(self):
        """Pause video when the plot requests it."""
        reader = self._LIVE_FEED.get_video_reader()
        if reader:
            reader.pause()
            self._VIDEO_CONTROL_WIDGET.set_playing(False)

    # -- UI state helpers

    def set_video_controls_enabled(self, enabled: bool):
        self._VIDEO_CONTROL_WIDGET.setEnabled(enabled)

    def reset_for_new_feed(self):
        """Reset tracker positions and plot when loading a new video or feed.
        Tracker definitions (names, types) are kept — only placed POIs are cleared."""
        self._VIDEO_CONTROL_WIDGET.set_playing(True)  # new feed always starts playing
        self._VIDEO_CONTROL_WIDGET.setEnabled(True)
        self._TRACKER_MANAGER.reset_all_positions()
        self._PLOTS_CONTAINER_WIDGET.clear_all()

    def hide_video_controls_if_needed(self):
        if not self._LIVE_FEED.is_video():
            self._VIDEO_CONTROL_WIDGET.setVisible(False)

    def update_slider_range_if_video(self):
        reader = self._LIVE_FEED.get_video_reader()
        if reader:
            self._VIDEO_CONTROL_WIDGET.set_slider_max(reader.get_total_frames())

    def _on_contrast_changed(self, percent: int):
        self._contrast_level = percent
