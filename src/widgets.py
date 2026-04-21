import PyQt6.QtCore as qtc
import PyQt6.QtGui as qtg
import PyQt6.QtWidgets as qtw
import pyqtgraph as pg
import numpy as np

from solarCollector import SolarCollectorLocation

class Plot(pg.PlotWidget):
    def __init__(self, title, lineColor, areaUnderCurveColor=None):
        super().__init__(title=title)

        self.plotItem.showGrid(y=True)

        # filled area (drawn underneath)
        self.fillCurve = self.plotItem.plot(pen = None, fillLevel = 0, brush = areaUnderCurveColor)

        # main line (drawn on top)
        self.curve = self.plotItem.plot(pen = pg.mkPen(lineColor, width = 2))

    def update(self, xValues, yValues):
        positiveY = np.maximum(yValues, 0)

        self.fillCurve.setData(x=xValues, y=positiveY)
        self.curve.setData(x=xValues, y=yValues)

class Slider(qtw.QWidget):
    def __init__(self, label: str, minimum: int, maximum: int, default: int = 0, parent = None):
        super().__init__(parent)
        self.setSizePolicy(
            qtw.QSizePolicy.Policy.Preferred,
            qtw.QSizePolicy.Policy.Fixed
        )
        self.contentLayout = qtw.QVBoxLayout()
        self.label = qtw.QLabel(label)
        self.slider = qtw.QSlider(qtc.Qt.Orientation.Horizontal)
        self.slider.setRange(minimum, maximum)
        self.slider.setValue(default)
        self.contentLayout.addWidget(self.label)
        self.contentLayout.addWidget(self.slider)
        self.setLayout(self.contentLayout)

class Selector(qtw.QWidget):
    def __init__(self, items: list[tuple[str, int]], label: str = None, parent = None):
        super().__init__(parent)
        self.contentLayout = qtw.QVBoxLayout()

        if label is not None:
            self.label = qtw.QLabel(label)

        self.selector = qtw.QComboBox()
        for text, value in items:
            self.selector.addItem(text, value)

        if label is not None:
            self.contentLayout.addWidget(self.label)
        self.contentLayout.addWidget(self.selector)
        self.setLayout(self.contentLayout)