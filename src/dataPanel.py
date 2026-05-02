import PyQt6.QtCore as qtc
import PyQt6.QtGui as qtg
import PyQt6.QtWidgets as qtw
import pyqtgraph as pg
from widgets import Plot, MultiLinePlot

class DataPanel(qtw.QTabWidget):
    def __init__(self):
        super().__init__()
        
        self.sunPositionWidget = qtw.QWidget()
        sunPositionLayout = qtw.QVBoxLayout(self.sunPositionWidget)
        self.positionPlot = MultiLinePlot(
            lineColors = ((255, 255, 0), (0, 255, 255)),
            title = "Sun position",
            areaUnderCurveColors = ((255, 255, 0, 100), (0, 255, 255, 100))
        )
        self.timeMarker = pg.InfiniteLine(pos = 0, angle = 90, pen = pg.mkPen((255, 0, 0), width = 2))
        self.positionPlot.addItem(self.timeMarker)
        sunPositionLayout.addWidget(self.positionPlot)

        self.sunPowerWidget = qtw.QWidget()
        sunPowerLayout = qtw.QVBoxLayout(self.sunPowerWidget)
        self.powerPlot = Plot(
            lineColor = (255, 0, 0),
            title = "Sun power"
        )
        self.powerPlot.addItem(self.timeMarker)
        sunPowerLayout.addWidget(self.powerPlot)

        self.addTab(self.sunPositionWidget, "Position")
        self.addTab(self.sunPowerWidget, "Power")