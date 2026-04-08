import queue
from threading import Event, Thread

import cv2 as cv
import numpy as np
from PySide6.QtCore import QObject, Signal

from src.pattern_tracking.logic.tracker.TrackerManager import TrackerManager
from src.pattern_tracking.logic.video.LiveFeedWrapper import LiveFeedWrapper
from src.pattern_tracking.qt_gui.widgets.FrameDisplayWidget import FrameDisplayWidget


class BackgroundComputation(QObject):
    """
    Runs continuously in a background thread: grabs frames, applies contrast,
    updates trackers, and refreshes the display.

    Inherits QObject so it can emit Qt signals safely across threads.
    plot_update_requested is emitted each frame and connected to the plot widget
    on the main thread — Qt queues the call automatically.
    """

    plot_update_requested = Signal(int)
    """Emitted with the current frame number. Connected to LivePlotterDockWidget.update_plots()."""

    def __init__(self,
                 tracker_manager: TrackerManager,
                 live_feed: LiveFeedWrapper,
                 frame_display_widget: FrameDisplayWidget,
                 global_halt: Event,
                 app_window):
        super().__init__()
        self._TRACKER_MANAGER = tracker_manager
        self._LIVE_FEED = live_feed
        self._FRAME_DISPLAY_WIDGET = frame_display_widget
        self._global_halt = global_halt
        self._APP_WINDOW = app_window
        self._thread: Thread | None = None
        self._last_frame: np.ndarray | None = None
        self._last_frame_number: int = 0

    def _run(self):
        while not self._global_halt.is_set():
            try:
                frame_number, live_frame = self._LIVE_FEED.grab_frame(block=True, timeout=0.1)
                if live_frame is None or live_frame.size == 0:
                    continue
                self._last_frame = live_frame
                self._last_frame_number = frame_number
            except queue.Empty:
                if self._LIVE_FEED.is_feed_resetting():
                    continue
                if self._last_frame is None:
                    continue
                live_frame = self._last_frame
                frame_number = self._last_frame_number

            self._render(live_frame, frame_number)

    def _render(self, live_frame: np.ndarray, frame_number: int):
        try:
            resized_frame = cv.resize(live_frame, FrameDisplayWidget.WIDGET_SIZE)
        except Exception as e:
            print(f"[ERROR] Resize failed: {e}")
            return

        alpha = self._APP_WINDOW.get_contrast_level() / 100.0
        resized_frame = cv.convertScaleAbs(resized_frame, alpha=alpha, beta=0)

        edited_frame = self._TRACKER_MANAGER.update_trackers(
            resized_frame,
            drawing_sheet=resized_frame.copy()
        )

        # Emit signal → update_plots() runs on the Qt main thread (queued connection)
        self.plot_update_requested.emit(frame_number)

        self._FRAME_DISPLAY_WIDGET.change_frame_to_display(edited_frame, swap_rgb=True)

        reader = self._LIVE_FEED.get_video_reader()
        if reader:
            curr_frame = reader.get_current_frame_index()
            total = reader.get_total_frames()
            fps = max(1, round(reader.get_fps()))
            self._APP_WINDOW.get_video_control_widget().update_slider_position(curr_frame)
            self._APP_WINDOW.get_video_control_widget().update_time_display(curr_frame, total, fps)

    def start(self):
        self._thread = Thread(target=self._run, daemon=True)
        self._thread.start()
