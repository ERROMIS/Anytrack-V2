import queue
from threading import Event, Thread
import cv2 as cv

from src.pattern_tracking.logic.tracker.TrackerManager import TrackerManager
from src.pattern_tracking.logic.video.LiveFeedWrapper import LiveFeedWrapper
from src.pattern_tracking.qt_gui.widgets.FrameDisplayWidget import FrameDisplayWidget
from src.pattern_tracking.qt_gui.dock_widgets.LivePlotterDockWidget import LivePlotterDockWidget


class BackgroundComputation:
    """
    Handles the real-time coordination between video feed, trackers,
    plotting system, and the main display UI. It continuously pulls frames
    in a separate thread, applies processing, and updates the GUI.
    """

    def __init__(self,
                 tracker_manager: TrackerManager,
                 live_feed: LiveFeedWrapper,
                 frame_display_widget: FrameDisplayWidget,
                 plots_container: LivePlotterDockWidget,
                 global_halt: Event,
                 app_window):
        """
        Initializes the computation handler.

        Args:
            tracker_manager (TrackerManager): The manager for all active trackers.
            live_feed (LiveFeedWrapper): The wrapper providing frames from camera or video.
            frame_display_widget (FrameDisplayWidget): UI component showing processed frames.
            plots_container (LivePlotterDockWidget): Widget handling live distance plotting.
            global_halt (Event): Shared event signaling application shutdown.
            app_window: Reference to the main window for accessing UI controls.
        """
        self._TRACKER_MANAGER = tracker_manager
        self._LIVE_FEED = live_feed
        self._FRAME_DISPLAY_WIDGET = frame_display_widget
        self._PLOTS_CONTAINER_WIDGET = plots_container
        self._global_halt = global_halt
        self._APP_WINDOW = app_window
        self._thread: Thread | None = None

    def _run(self):
        """
        The internal loop that performs background frame grabbing, processing,
        tracking updates, plotting, and display updates. This method should
        only be run in a dedicated thread.
        """
        while not self._global_halt.is_set():
            try:
                # Grab frame from video/camera
                frame_number, live_frame = self._LIVE_FEED.grab_frame(block=True, timeout=0.5)
                if live_frame is None or live_frame.size == 0:
                    print("[DEBUG] Empty or invalid frame. Skipping...")
                    continue
            except queue.Empty:
                # If the feed is being reset, wait until it becomes available
                while self._LIVE_FEED.is_feed_resetting():
                    continue

            # Resize and apply contrast
            try:
                resized_frame = cv.resize(live_frame, FrameDisplayWidget.WIDGET_SIZE)
            except Exception as e:
                print(f"[ERROR] Resize failed: {e}")
                continue

            contrast = self._APP_WINDOW.get_contrast_level()
            alpha = contrast / 100.0
            resized_frame = cv.convertScaleAbs(resized_frame, alpha=alpha, beta=0)

            # Apply tracking updates and plot data
            edited_frame = self._TRACKER_MANAGER.update_trackers(
                resized_frame,
                drawing_sheet=resized_frame.copy()
            )
            self._PLOTS_CONTAINER_WIDGET.update_plots(frame_number)
            self._FRAME_DISPLAY_WIDGET.change_frame_to_display(edited_frame, swap_rgb=True)

            # Update slider/time indicators if using video
            from src.pattern_tracking.logic.video.VideoReader import VideoReader
            reader = self._LIVE_FEED.get_video_reader()
            if reader:
                curr_frame = reader.get_current_frame_index()
                total = reader.get_total_frames()
                self._APP_WINDOW.get_video_control_widget().update_slider_position(curr_frame)
                self._APP_WINDOW.get_video_control_widget().update_time_display(curr_frame, total)

    def start(self):
        """
        Starts the background thread for continuous frame processing.
        """
        self._thread = Thread(target=self._run)
        self._thread.start()