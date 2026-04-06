import datetime
import math

import PyQt6.QtCore as qtc
import PyQt6.QtGui as qtg
import PyQt6.QtWidgets as qtw
import pyqtgraph as pg
import numpy as np
from pyglm import glm
from sun_position_calculator import SunPositionCalculator

from viewport import Viewport
from widgets import Slider, Plot

class App:
    def __init__(self):
        self.dayResolution = 24 * 4
        self.utcPlus2 = datetime.timezone(datetime.timedelta(hours=2))
        self.sunPositionCalculator = SunPositionCalculator()
        self.latitude, self.longitude = 48.117245, 20.663500

    def getSunlightTransmission(self, time: datetime.datetime):
        altitude = self.sunPositionCalculator.pos(time.timestamp() * 1000, self.latitude, self.longitude).altitude
        airMass = 1 / math.sin(altitude)
        transmission = 0.75 ** airMass
        return transmission

    def dateChanged(self):
        numDays = self.dateSlider.slider.value()
        currentDate = datetime.date(2026, 1, 1) + datetime.timedelta(days = numDays)

        self.dateSlider.label.setText(f"Date: {currentDate.month:02}.{currentDate.day:02}")

        self.startTime = datetime.datetime.combine(currentDate, datetime.time.min, self.utcPlus2)
        startTimeUnix = self.startTime.timestamp() * 1000
        endTime = self.startTime + datetime.timedelta(hours = 24)
        endTimeUnix = endTime.timestamp() * 1000

        xValues = np.linspace(0, 24, self.dayResolution)
        timeValues = np.linspace(startTimeUnix, endTimeUnix, self.dayResolution)

        yValues = [math.degrees(self.sunPositionCalculator.pos(unixTime, self.latitude, self.longitude).altitude) for unixTime in timeValues]
        self.powerPlot.update(xValues, yValues)

        self.timeChanged()

    def timeChanged(self):
        viewportTime = self.startTime + datetime.timedelta(minutes = self.viewportTimeSlider.slider.value())
        viewportTimeUnix = viewportTime.timestamp() * 1000
        sunPosition = self.sunPositionCalculator.pos(viewportTimeUnix, self.latitude, self.longitude)
        sunlightTransmission = self.getSunlightTransmission(viewportTime)

        self.viewport.scene.sunPosition = glm.vec2(sunPosition.azimuth, sunPosition.altitude)
        self.viewport.scene.sunlightTransmission = glm.float32(sunlightTransmission)

        self.timeMarker.setValue(glm.mix(0, 24, self.viewportTimeSlider.slider.value() / (24 * 60)))

        self.viewport.repaint()

    def start(self):
        self.qtApp = qtw.QApplication([])

        qtc.QTimer.singleShot(0, self.dateChanged)
        qtc.QTimer.singleShot(0, self.timeChanged)

        self.window = qtw.QMainWindow()
        self.mainWidget = qtw.QWidget()
        self.mainLayout = qtw.QHBoxLayout()
        self.mainLayoutSplitter = qtw.QSplitter()

        self.sidePanel = qtw.QWidget()
        self.sidePanel.setMinimumWidth(200)
        self.sidePanelLayout = qtw.QVBoxLayout()

        self.dateSlider = Slider("Date", 0, 364)

        self.dateSlider.slider.valueChanged.connect(self.dateChanged)

        self.sidePanelLayout.addWidget(self.dateSlider)

        self.sidePanelLayout.addStretch()
        self.sidePanel.setLayout(self.sidePanelLayout)

        self.contentPanel = qtw.QWidget()
        self.contentPanelLayout = qtw.QVBoxLayout()
        self.viewportPlotSplitter = qtw.QSplitter(qtc.Qt.Orientation.Vertical)
        
        self.viewport = Viewport()
        self.powerPlot = Plot("Power efficiency", (255, 255, 0), (255, 255, 0, 100))
        self.timeMarker = pg.InfiniteLine(pos = 0, angle = 90, pen = pg.mkPen((255, 0, 0), width = 2))
        self.powerPlot.addItem(self.timeMarker)
        self.viewportPlotSplitter.addWidget(self.viewport)
        self.viewportPlotSplitter.addWidget(self.powerPlot)
        self.viewportPlotSplitter.setStretchFactor(0, 1)
        self.viewportPlotSplitter.setStretchFactor(1, 1)

        self.viewportTimeSlider = Slider("Viewport time", 0, 24 * 60)
        self.viewportTimeSlider.slider.valueChanged.connect(self.timeChanged)

        self.contentPanelLayout.addWidget(self.viewportTimeSlider)
        self.contentPanelLayout.addWidget(self.viewportPlotSplitter)
        self.contentPanel.setLayout(self.contentPanelLayout)

        self.mainLayoutSplitter.addWidget(self.contentPanel)
        self.mainLayoutSplitter.addWidget(self.sidePanel)
        self.mainLayoutSplitter.setStretchFactor(0, 3)
        self.mainLayoutSplitter.setStretchFactor(1, 1)
        self.mainLayout.addWidget(self.mainLayoutSplitter)

        self.mainWidget.setLayout(self.mainLayout)
        self.window.setCentralWidget(self.mainWidget)
        self.window.show()

        self.qtApp.exec()