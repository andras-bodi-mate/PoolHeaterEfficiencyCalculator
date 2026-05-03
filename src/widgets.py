import PyQt6.QtCore as qtc
import PyQt6.QtGui as qtg
import PyQt6.QtWidgets as qtw
import superqt as qts
import pyqtgraph as pg
import numpy as np

class PlotBase(pg.PlotWidget):
    def __init__(self, title = None, showXAxis = True, showYAxis = True, showXValues = True, showYValues = True):
        super().__init__(title = title)
        self.plotItem.showGrid(x = showXAxis, y = showYAxis)
        if not showXValues:
            self.plotItem.getAxis("bottom").setStyle(showValues = False, tickLength = 0)
        if not showYValues:
            self.plotItem.getAxis("left").setStyle(showValues = False, tickLength = 0)

class Plot(PlotBase):
    def __init__(self, lineColor, title = None, areaUnderCurveColor = None, showXAxis = True, showYAxis = True, showXValues = True, showYValues = True):
        super().__init__(title, showXAxis, showYAxis, showXValues, showYValues)
        
        self.fillCurve = self.plotItem.plot(pen = None, fillLevel = 0, brush = areaUnderCurveColor) if areaUnderCurveColor else None
        self.curve = self.plotItem.plot(pen = pg.mkPen(lineColor, width = 2))

    def update(self, yValues, xValues = None):
        if xValues is None:
            xValues = list(range(len(yValues)))
        if self.fillCurve:
            positiveY = np.maximum(yValues, 0)
            self.fillCurve.setData(x = xValues, y = positiveY)
        self.curve.setData(x = xValues, y = yValues)

class MultiLinePlot(PlotBase):
    def __init__(self, lineColors: tuple, title = None, areaUnderCurveColors: tuple = None, showXAxis = True, showYAxis = True, showXValues = True, showYValues = True):
        super().__init__(title, showXAxis, showYAxis, showXValues, showYValues)

        self.legend = self.plotItem.addLegend()
        self.numLines = len(lineColors)

        self.curves: list[pg.PlotCurveItem] = []
        self.fillCurves = [] if areaUnderCurveColors else None

        for i, color in enumerate(lineColors):
            curve = self.plotItem.plot(pen = pg.mkPen(color, width = 2))
            self.curves.append(curve)

            if areaUnderCurveColors:
                fillColor = areaUnderCurveColors[i]
                fill = self.plotItem.plot(
                    pen = None,
                    fillLevel = 0,
                    brush = fillColor
                ) if fillColor else None
                self.fillCurves.append(fill)

    def update(self, lineValues: list[list[float]], xValues: list[float] = None, labels: list[str] = None):
        if xValues is None:
            xValues = range(len(lineValues[0]))

        self.legend.clear()
        for i, values in enumerate(lineValues):
            self.curves[i].clear()
            if self.fillCurves:
                self.fillCurves[i].clear()

        for i, values in enumerate(lineValues):
            self.curves[i].setData(x = xValues, y = values)
            
            if labels is not None:
                name = labels[i]
                self.curves[i].opts['name'] = name
                self.legend.addItem(self.curves[i], name)

            if self.fillCurves and self.fillCurves[i] is not None:
                self.fillCurves[i].setData(x = xValues, y = np.maximum(values, 0))

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

class RangeSlider(qtw.QWidget):
    def __init__(self, label: str, minimum: int, maximum: int, parent = None):
        super().__init__(parent)
        self.setSizePolicy(
            qtw.QSizePolicy.Policy.Preferred,
            qtw.QSizePolicy.Policy.Fixed
        )
        self.contentLayout = qtw.QVBoxLayout()
        self.label = qtw.QLabel(label)
        self.slider = qts.QRangeSlider(qtc.Qt.Orientation.Horizontal)
        self.slider.setRange(minimum, maximum)
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

class CheckableComboBox(qtw.QComboBox):
    def addItem(self, text, userData=None):
        super().addItem(text, userData)
        item = self.model().item(self.count() - 1, 0)
        item.setFlags(qtc.Qt.ItemFlag.ItemIsUserCheckable | qtc.Qt.ItemFlag.ItemIsEnabled)
        item.setCheckState(qtc.Qt.CheckState.Unchecked)

    def itemChecked(self, index):
        item = self.model().item(index, 0)
        return item.checkState() == qtc.Qt.CheckState.Checked
    
    def getCheckedItemsData(self):
        checked = []
        for i in range(self.count()):
            item = self.model().item(i, 0)
            if item.checkState() == qtc.Qt.CheckState.Checked:
                checked.append(self.itemData(i))
        return checked
    
class LabeledCheckableComboBox(qtw.QWidget):
    def __init__(self, label: str, parent = None):
        super().__init__(parent)

        layout = qtw.QVBoxLayout()
        self.label = qtw.QLabel(label)
        self.list = CheckableComboBox()
        layout.addWidget(self.label)
        layout.addWidget(self.list)
        self.setLayout(layout)