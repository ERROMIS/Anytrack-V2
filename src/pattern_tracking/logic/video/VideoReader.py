import time
from threading import Thread, Event, Lock
import cv2 as cv

from src.pattern_tracking.logic.video.AbstractFrameProvider import AbstractFrameProvider


class VideoReader(AbstractFrameProvider):
    """
    Reads frames from a video file or live camera stream continuously and stores them
    in a thread-safe queue. Supports pause/resume and video looping.
    """

    def __init__(self,
                 feed_origin: str | int,
                 is_video: bool,
                 global_halt_event: Event,
                 max_frames_in_queue: int = 30,
                 loop_video: bool = False):
        """
        Initializes the video reader with the given video or camera feed.

        Args:
            feed_origin (str | int): Path to the video file or index of the camera device.
            is_video (bool): True if the feed is from a video file.
            global_halt_event (Event): Shared threading event to halt reading.
            max_frames_in_queue (int): Max number of frames to hold in the queue.
            loop_video (bool): Whether to loop the video once it reaches the end.
        """
        super().__init__(global_halt_event, is_video, max_frames_in_queue)

        self._seek_lock = Lock()
        self._paused = False
        self._video_feed: cv.VideoCapture = None
        self._initialized = False
        self._feed_origin = feed_origin
        self._loop = loop_video and is_video
        self._thread: Thread | None = None

        self._initialize_reader()
        success, first_frame = self._video_feed.read()
        if not success or first_frame is None:
            raise IOError("Couldn't read first frame from video")
        self._frames_shape = first_frame.shape
        self._fps = self._video_feed.get(cv.CAP_PROP_FPS)
        self._video_feed.set(cv.CAP_PROP_POS_FRAMES, 0)

    def start(self):
        """Starts the background thread that reads frames from the feed."""
        self._thread = Thread(target=self._run)
        self._thread.start()

    def stop(self):
        """Signals the thread to stop reading frames."""
        self._stop_working.set()

    def _run(self):
        """Internal thread method to continuously read and enqueue frames."""
        while (
            self._video_feed.isOpened()
            and not self._global_halt.is_set()
            and not self._stop_working.is_set()
        ):
            while self._paused:
                time.sleep(0.1)
                if self._global_halt.is_set():
                    return

            with self._seek_lock:
                ret, frame = self._video_feed.read()
                frame_id = int(self._video_feed.get(cv.CAP_PROP_POS_FRAMES))

            # Fin de vidéo
            if not ret or frame is None:
                if self._loop:
                    with self._seek_lock:
                        self._video_feed.set(cv.CAP_PROP_POS_FRAMES, 0)
                    continue
                else:
                    self.pause()  # <- CRUCIAL
                    return

            self._frames_queue.put((frame_id, frame.copy()))  # Defensive copy

            if self._is_video:
                time.sleep(0.05)

        self._video_feed.release()

    def _initialize_reader(self):
        """Initializes the OpenCV video feed."""
        self._video_feed = cv.VideoCapture(self._feed_origin)
        self._initialized = self._video_feed.isOpened()
        if not self._initialized:
            raise IOError("Couldn't open video feed!")

    def get_shape(self) -> tuple[int, int, int]:
        """
        Returns the resolution and channel count of the video.

        Returns:
            tuple: Shape of the video frames (height, width, channels).
        """
        return self._frames_shape

    def get_fps(self) -> float:
        """
        Returns the frames per second (FPS) of the video source.

        Returns:
            float: The FPS of the video feed.
        """
        return self._fps

    def pause(self):
        """Pauses the video reading thread."""
        self._paused = True

    def resume(self):
        """Resumes the video reading thread."""
        self._paused = False

    def is_paused(self) -> bool:
        """
        Checks whether the video reading is paused.

        Returns:
            bool: True if paused, False otherwise.
        """
        return self._paused

    def restart(self):
        """Seeks to the beginning of the video."""
        with self._seek_lock:
            self._video_feed.set(cv.CAP_PROP_POS_FRAMES, 0)

    def seek(self, frame_number: int):
        """
        Seeks to a specific frame number.

        Args:
            frame_number (int): The target frame index.
        """
        with self._seek_lock:
            self._video_feed.set(cv.CAP_PROP_POS_FRAMES, frame_number)

    def get_total_frames(self) -> int:
        """
        Gets the total number of frames in the video.

        Returns:
            int: Total frame count.
        """
        return int(self._video_feed.get(cv.CAP_PROP_FRAME_COUNT))

    def get_current_frame_index(self) -> int:
        """
        Returns the index of the current frame being read.

        Returns:
            int: Current frame position.
        """
        return int(self._video_feed.get(cv.CAP_PROP_POS_FRAMES))