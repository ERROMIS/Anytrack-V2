from PySide6.QtGui import QAction
from PySide6.QtWidgets import QFileDialog, QWidget, QApplication

from src.pattern_tracking.logic.video.LiveFeedWrapper import LiveFeedWrapper
from src.pattern_tracking.logic.video.VideoReader import VideoReader


class SelectVideoAction(QAction):

    def __init__(self, live_feed: LiveFeedWrapper, dialog_parent: QWidget | None = None, main_window=None):
        super().__init__()
        self.setText("Launch from video")
        self._live_feed = live_feed
        self._dialog_parent = dialog_parent
        self._main_window = main_window
        self.triggered.connect(self._select_video_dialog)

    def _select_video_dialog(self):
        file_name, _ = QFileDialog.getOpenFileName(
            self._dialog_parent, "Open video file", filter="Video files (*.avi *.jpg *.mp4)"
        )
        if len(file_name) != 0:
            self._live_feed.change_feed(
                VideoReader(file_name,
                            global_halt_event=self._live_feed.get_global_halt_event(),
                            is_video=True, loop_video=True)
            )
            if self._main_window:
                self._main_window.reset_for_new_feed()
                self._main_window.get_video_control_widget().setVisible(True)
                self._main_window.update_slider_range_if_video()