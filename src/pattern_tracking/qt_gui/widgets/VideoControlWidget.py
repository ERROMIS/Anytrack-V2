from PySide6.QtWidgets import QWidget, QPushButton, QSlider, QHBoxLayout, QLabel
from PySide6.QtCore import Qt, Signal


class VideoControlWidget(QWidget):
    """
    A widget providing playback controls for a video, including play/pause,
    slider for seeking, and a time display.

    Signals:
        play_pause_clicked (): Emitted when the play/pause button is clicked.
        slider_moved (int): Emitted when the slider is moved (seek requested).
    """

    play_pause_clicked = Signal()
    slider_moved = Signal(int)

    def __init__(self, parent=None):
        """
        Initializes the video control widget.

        Args:
            parent (QWidget, optional): Parent widget.
        """
        super().__init__(parent)

        self._play_pause_button = QPushButton("⏸️")
        self._slider = QSlider(Qt.Horizontal)
        self._slider.setRange(0, 100)

        self._time_label = QLabel("00:00 / 00:00")

        self._is_user_dragging = False

        layout = QHBoxLayout()
        layout.addWidget(self._play_pause_button)
        layout.addWidget(self._slider)
        layout.addWidget(self._time_label)
        self.setLayout(layout)

        # Signal connections
        self._play_pause_button.clicked.connect(self.play_pause_clicked.emit)
        self._slider.sliderMoved.connect(self.slider_moved.emit)
        self._slider.sliderPressed.connect(self._on_slider_pressed)
        self._slider.sliderReleased.connect(self._on_slider_released)

    def set_playing(self, playing: bool):
        """
        Updates the play/pause button icon based on playback state.

        Args:
            playing (bool): True if video is playing, False if paused.
        """
        self._play_pause_button.setText("⏸️" if playing else "▶️")

    def set_slider_max(self, max_value: int):
        """
        Sets the maximum value for the slider.

        Args:
            max_value (int): Maximum frame number.
        """
        self._slider.setMaximum(max_value)

    def update_slider_position(self, current_frame: int):
        """
        Updates the slider to reflect the current frame,
        unless the user is actively dragging it.

        Args:
            current_frame (int): Current frame index.
        """
        if self._is_user_dragging:
            return
        self._slider.blockSignals(True)
        self._slider.setValue(current_frame)
        self._slider.blockSignals(False)

    def update_time_display(self, current_frame: int, total_frames: int, fps: int = 20):
        """
        Updates the time label showing elapsed and total video time.

        Args:
            current_frame (int): Current frame index.
            total_frames (int): Total number of frames in the video.
            fps (int): Frames per second for time calculation (default = 20).
        """

        def format_time(frame, fps):
            total_seconds = int(frame / fps)
            minutes = total_seconds // 60
            seconds = total_seconds % 60
            return f"{minutes:02}:{seconds:02}"

        current = format_time(current_frame, fps)
        total = format_time(total_frames, fps)
        self._time_label.setText(f"{current} / {total}")

    def _on_slider_pressed(self):
        """Marks that the user has started dragging the slider."""
        self._is_user_dragging = True

    def _on_slider_released(self):
        """
        Marks the end of slider drag, and emits the slider_moved signal
        with the new desired frame position.
        """
        self._is_user_dragging = False
        self.slider_moved.emit(self._slider.value())