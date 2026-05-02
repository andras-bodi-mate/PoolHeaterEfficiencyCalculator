import PyQt6.QtCore as qtc
import PyQt6.QtGui as qtg
import PyQt6.QtWidgets as qtw
import pyqtgraph as pg
from widgets import MultiLinePlot

class DataPanel(qtw.QWidget):
    def __init__(self):
        super().__init__()
        layout = qtw.QVBoxLayout()
        
        self.powerPlot = MultiLinePlot(
            lineColors = ((255, 255, 0), (0, 255, 255)),
            title = "Sun position",
            areaUnderCurveColors = ((255, 255, 0, 100), (0, 255, 255, 100))
        )
        self.timeMarker = pg.InfiniteLine(pos = 0, angle = 90, pen = pg.mkPen((255, 0, 0), width = 2))
        self.powerPlot.addItem(self.timeMarker)

        layout.addWidget(self.powerPlot)
        self.setLayout(layout)