from PySide6.QtCore import Qt
from PySide6.QtWidgets import QMainWindow
from PySide6.QtWidgets import QWidget, QVBoxLayout


from src.pattern_tracking.qt_gui.widgets.ContrastControlWidget import ContrastControlWidget


from src.pattern_tracking.logic.video.LiveFeedWrapper import LiveFeedWrapper
from src.pattern_tracking.qt_gui.dock_widgets.LivePlotterDockWidget import LivePlotterDockWidget
from src.pattern_tracking.qt_gui.top_menu_bar.plot.PlotMenu import PlotMenu
from src.pattern_tracking.qt_gui.top_menu_bar.trackers.TrackersMenu import TrackersMenu
from src.pattern_tracking.logic.tracker import TrackerManager
from src.pattern_tracking.qt_gui.widgets.FrameDisplayWidget import FrameDisplayWidget
from src.pattern_tracking.qt_gui.top_menu_bar.video.VideoMenu import VideoMenu
from src.pattern_tracking.qt_gui.widgets.VideoControlWidget import VideoControlWidget


class AppMainWindow(QMainWindow):
    """
    Main display to the user. Initializes the application
    with the different menus, sidebar menus and buttons
    """

    def __init__(self, tracker_manager: TrackerManager, live_feed: LiveFeedWrapper):
        super().__init__()
        self.setWindowTitle("Anytrack")
        # -- Attributes
        self._TRACKER_MANAGER = tracker_manager
        self._LIVE_FEED = live_feed

        # -- Widgets
        self._FRAME_DISPLAY = FrameDisplayWidget(tracker_manager)
        self._PLOTS_CONTAINER_WIDGET = LivePlotterDockWidget(self)
        self._VIDEO_CONTROL_WIDGET = VideoControlWidget()
        self._VIDEO_CONTROL_WIDGET.setVisible(False)
        self._CONTRAST_WIDGET = ContrastControlWidget()
        self._CONTRAST_WIDGET.contrast_changed.connect(self._on_contrast_changed)
        self._contrast_level = 100  
        
        self._VIDEO_CONTROL_WIDGET.play_pause_clicked.connect(self._toggle_video_playback)
        self._VIDEO_CONTROL_WIDGET.slider_moved.connect(self._seek_video_frame)

        # -- Menus
        self._VIDEO_MENU = VideoMenu(live_feed, parent=self)
        self._TRACKERS_MENU = TrackersMenu(tracker_manager, parent=self)
        self._PLOTS_MENU = PlotMenu(tracker_manager, self._PLOTS_CONTAINER_WIDGET)

        # -- Assignments
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

    def get_frame_display_widget(self) -> FrameDisplayWidget:
        """:return: the current frame display widget"""
        return self._FRAME_DISPLAY

    def get_plot_container_widget(self):
        """:return: the current plots container"""
        return self._PLOTS_CONTAINER_WIDGET
    
    def get_video_control_widget(self):
        return self._VIDEO_CONTROL_WIDGET
    
    def _toggle_video_playback(self):
        from src.pattern_tracking.logic.video.VideoReader import VideoReader
        if not self._LIVE_FEED.is_video():
            return

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
            
    def hide_video_controls_if_needed(self):
        if not self._LIVE_FEED.is_video():
            self._VIDEO_CONTROL_WIDGET.setVisible(False)
            
    def update_slider_range_if_video(self):
        reader = self._LIVE_FEED.get_video_reader()
        if reader:
            total = reader.get_total_frames()
            self._VIDEO_CONTROL_WIDGET.set_slider_max(total)
    
    def _on_contrast_changed(self, percent: int):
        self._contrast_level = percent
        print(f"[DEBUG] Contraste réglé à {percent}%")
        
    def get_contrast_level(self) -> int:
        return getattr(self, "_contrast_level", 0)
    
    def set_video_controls_enabled(self, enabled: bool):
        self._VIDEO_CONTROL_WIDGET.setEnabled(enabled)
