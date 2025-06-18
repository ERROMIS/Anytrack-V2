from PySide6.QtWidgets import QMenu, QWidget

from src.pattern_tracking.logic.video.LiveFeedWrapper import LiveFeedWrapper
from src.pattern_tracking.qt_gui.top_menu_bar.video.SelectCameraAsLiveFeedAction import SelectCameraAsLiveFeedAction
from src.pattern_tracking.qt_gui.top_menu_bar.video.SelectFramesFromZMQSocketAction import SelectFramesFromZMQSocketAction
from src.pattern_tracking.qt_gui.top_menu_bar.video.SelectVideoAction import SelectVideoAction


class VideoMenu(QMenu):

    def __init__(self, live_feed: LiveFeedWrapper, parent: QWidget | None = None):
        super().__init__(parent)

        self._SELECT_VIDEO_ACTION = SelectVideoAction(live_feed, dialog_parent=parent, main_window=parent)
        self._SELECT_CAMERA_LIVE_FEED = SelectCameraAsLiveFeedAction(live_feed, main_window=parent)
        self._FROM_DISTANT_SERVER_ACTION = SelectFramesFromZMQSocketAction(live_feed, main_window=parent)

        self.addAction(self._SELECT_VIDEO_ACTION)
        self.addAction(self._SELECT_CAMERA_LIVE_FEED)
        self.addAction(self._FROM_DISTANT_SERVER_ACTION)
        self.setTitle("Video")


