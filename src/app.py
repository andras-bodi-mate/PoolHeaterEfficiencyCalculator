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
from widgets import Slider, Plot, SolarCollectorLocationSelector
from solarCollector import SolarCollectorLocation

class App:
    def __init__(self):
        self.dayResolution = 24 * 4
        self.utcPlus2 = datetime.timezone(datetime.timedelta(hours=2))
        self.sunPositionCalculator = SunPositionCalculator()
        self.latitude, self.longitude = 48.117245, 20.663500
        self.areosolOpticalDepth = 0.15

    def getSunlightTransmission(self, time: datetime.datetime):
        altitude = self.sunPositionCalculator.pos(time.timestamp() * 1000, self.latitude, self.longitude).altitude
        if altitude <= 0:
            return 0.0

        airMass = 1 / (math.sin(altitude) + 0.50572 * (altitude + 6.07995)**-1.6364)
        transmission = math.exp(-self.areosolOpticalDepth * airMass)
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
        self.viewport.scene.sunCamera.direction = -glm.euclidean(glm.vec2(self.viewport.scene.sunPosition.y, -self.viewport.scene.sunPosition.x + glm.half_pi()))
        self.viewport.scene.sunCamera.updateCameraProjection()
        self.viewport.scene.sunCamera.updatePerspectiveProjection(self.viewport.width() / self.viewport.height())

        self.timeMarker.setValue(glm.mix(0, 24, self.viewportTimeSlider.slider.value() / (24 * 60)))

        self.viewportTimeSlider.label.setText(f"Viewport time: {viewportTime.hour:02}:{viewportTime.minute:02}")

        self.viewport.repaint()

    def selectedSolarCollectorChanged(self):
        self.viewport.scene.selectedSolarCollector = self.solarCollectorLocationSelector.selector.currentData()
        self.viewport.repaint()

    def initializeQt(self):
        surfaceFormat = qtg.QSurfaceFormat()
        surfaceFormat.setVersion(3, 3)
        surfaceFormat.setProfile(qtg.QSurfaceFormat.OpenGLContextProfile.CoreProfile)
        surfaceFormat.setDepthBufferSize(24)
        surfaceFormat.setStencilBufferSize(8)
        surfaceFormat.setSwapInterval(1) # Enables vertical sync (vsync)
        surfaceFormat.setSwapBehavior(qtg.QSurfaceFormat.SwapBehavior.DoubleBuffer)
        samples = 1
        if samples > 1:
            surfaceFormat.setSamples(samples)
        qtg.QSurfaceFormat.setDefaultFormat(surfaceFormat)

    def start(self):
        self.initializeQt()
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
        self.solarCollectorLocationSelector = SolarCollectorLocationSelector([
            ("On roof", SolarCollectorLocation.OnRoof),
            ("On shed", SolarCollectorLocation.OnShed),
            ("Next to pool", SolarCollectorLocation.NextToPool)
        ])
        self.solarCollectorLocationSelector.selector.currentIndexChanged.connect(self.selectedSolarCollectorChanged)

        self.sidePanelLayout.addWidget(self.dateSlider)
        self.sidePanelLayout.addWidget(self.solarCollectorLocationSelector)

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
        self.viewportPlotSplitter.setSizes([1, 1])

        self.viewportTimeSlider = Slider("Viewport time", 0, 24 * 60 - 1)
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