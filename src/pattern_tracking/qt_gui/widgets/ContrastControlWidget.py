from PySide6.QtWidgets import QWidget, QLabel, QSlider, QHBoxLayout
from PySide6.QtCore import Qt, Signal


class ContrastControlWidget(QWidget):
    """
    A simple widget that provides a horizontal slider to adjust the contrast of an image.

    Emits:
        contrast_changed (int): Signal emitted whenever the contrast value changes.
    """

    contrast_changed = Signal(int)

    def __init__(self, parent=None):
        """
        Initializes the contrast slider widget with default value 100% and a label.

        Args:
            parent (QWidget, optional): Optional parent widget.
        """
        super().__init__(parent)

        self._label = QLabel("Contraste : 100%")
        self._slider = QSlider(Qt.Horizontal)
        self._slider.setRange(10, 300)   # Allowed contrast values: 10% to 300%
        self._slider.setValue(100)       # Default contrast: 100%

        layout = QHBoxLayout()
        layout.addWidget(self._label)
        layout.addWidget(self._slider)
        self.setLayout(layout)

        self._slider.valueChanged.connect(self._on_slider_changed)

    def _on_slider_changed(self, value: int):
        """
        Callback executed when the slider value changes.
        Updates the label and emits the new contrast value.

        Args:
            value (int): The new slider value.
        """
        self._label.setText(f"Contraste : {value}%")
        self.contrast_changed.emit(value)

    def get_contrast_factor(self) -> float:
        """
        Returns:
            float: The contrast multiplier (e.g., 1.0 = 100%, 2.0 = 200%).
        """
        return self._slider.value() / 100.0