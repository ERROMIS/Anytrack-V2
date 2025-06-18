from PySide6.QtGui import QAction

from src.pattern_tracking.qt_gui.top_menu_bar.video.NewZMQSocketFeedQDialog import NewZMQSocketFeedQDialog
from src.pattern_tracking.logic.video.LiveFeedWrapper import LiveFeedWrapper


class SelectFramesFromZMQSocketAction(QAction):

    def __init__(self, live_feed: LiveFeedWrapper, main_window=None):
        super().__init__()
        self._live_feed = live_feed
        self._main_window = main_window
        self.setText("From distant server (ZMQ)")
        self.triggered.connect(self._use_zmq_socket_feed)

    def _use_zmq_socket_feed(self):
        dlg = NewZMQSocketFeedQDialog(self._live_feed.get_global_halt_event())
        if dlg.exec():
            self._live_feed.change_feed(dlg.get_connection_result())
            if self._main_window:
                self._main_window.hide_video_controls_if_needed()