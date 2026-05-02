import PyQt6.QtCore as qtc
import PyQt6.QtGui as qtg
import PyQt6.QtWidgets as qtw
from widgets import Slider
from viewport import Viewport

class ViewportPanel(qtw.QWidget):
    timeChanged = qtc.pyqtSignal(int)

    def __init__(self):
        super().__init__()
        layout = qtw.QVBoxLayout(self)

        self.timeSlider = Slider("Viewport time", 0, 24 * 60 - 1, 14 * 60)
        self.viewport = Viewport()

        self.timeSlider.slider.valueChanged.connect(self.timeChanged.emit)

        layout.addWidget(self.timeSlider)
        layout.addWidget(self.viewport)