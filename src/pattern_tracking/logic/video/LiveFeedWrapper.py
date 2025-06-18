from threading import Lock
from src.pattern_tracking.logic.video.AbstractFrameProvider import AbstractFrameProvider


class LiveFeedWrapper:
    """
    A wrapper for an AbstractFrameProvider. This class manages thread-safe
    operations for starting, stopping, and switching video or live feeds.
    """

    def __init__(self, feed: AbstractFrameProvider):
        """
        Initializes the wrapper with a given frame provider.

        Args:
            feed (AbstractFrameProvider): The initial frame provider to use.
        """
        self._frame_provider = feed
        self._reset_feed_mutex = Lock()

    def start(self):
        """
        Starts the current frame provider.
        """
        self._frame_provider.start()

    def stop(self):
        """
        Stops the current frame provider.
        """
        self._frame_provider.stop()

    def grab_frame(self, block: bool = True, timeout: float = 0.5):
        """
        Grabs a frame from the current feed.

        Args:
            block (bool): Whether to block until a frame is available.
            timeout (float): How long to wait (in seconds) before timing out.

        Returns:
            tuple[int, np.ndarray] or None: The frame number and frame image,
            or None if not available.
        """
        return self._frame_provider.grab_frame(block, timeout)

    def get_global_halt_event(self):
        """
        Returns the global halt event used by the frame provider.

        Returns:
            threading.Event: The halt event.
        """
        return self._frame_provider.get_global_halt_event()

    def change_feed(self, feed: AbstractFrameProvider):
        """
        Replaces the current feed with a new one, ensuring the swap is thread-safe.

        Args:
            feed (AbstractFrameProvider): The new frame provider to use.
        """
        self._reset_feed_mutex.acquire()
        self._frame_provider.stop()
        self._frame_provider = feed
        self._frame_provider.start()
        while self._frame_provider.available_frames() == 0:
            continue  # wait until new feed has frames available
        self._reset_feed_mutex.release()

    def is_feed_resetting(self) -> bool:
        """
        Checks whether a feed change is in progress.

        Returns:
            bool: True if feed is currently being reset, False otherwise.
        """
        return self._reset_feed_mutex.locked()

    def is_video(self) -> bool:
        """
        Determines if the current feed is a video file.

        Returns:
            bool: True if it is a video, False if it's a live stream.
        """
        return getattr(self._frame_provider, "_is_video", False)

    def get_video_reader(self):
        """
        Returns the frame provider as a VideoReader instance if applicable.

        Returns:
            VideoReader or None: The current provider if it's a VideoReader, otherwise None.
        """
        from src.pattern_tracking.logic.video.VideoReader import VideoReader
        if isinstance(self._frame_provider, VideoReader):
            return self._frame_provider
        return None