import datetime
import math

import PyQt6.QtCore as qtc
import PyQt6.QtGui as qtg
import PyQt6.QtWidgets as qtw
import pyqtgraph as pg
import numpy as np
from pyglm import glm
from sun_position_calculator import SunPositionCalculator

from object import Object
from sidePanel import SidePanel
from dataPanel import DataPanel
from viewportPanel import ViewportPanel

class App:
    def __init__(self):
        self.dayResolution = 24 * 4
        self.utcPlus2 = datetime.timezone(datetime.timedelta(hours = 2))
        self.sunPositionCalculator = SunPositionCalculator()
        self.latitude, self.longitude = 48.117245, 20.663500
        self.areosolOpticalDepth = 0.15
        self.solarCollectors: list[Object]

    def getSunlightTransmission(self, time: datetime.datetime):
        altitude = self.sunPositionCalculator.pos(time.timestamp() * 1000, self.latitude, self.longitude).altitude
        if altitude <= 0:
            return 0.0

        airMass = 1 / (math.sin(altitude) + 0.50572 * (altitude + 6.07995)**-1.6364)
        transmission = math.exp(-self.areosolOpticalDepth * airMass)
        return transmission
    
    def getSunEucledeanPosition(self, sunAltitude: float, sunAzimuth: float):
        return -glm.euclidean(glm.vec2(sunAltitude, -sunAzimuth + glm.half_pi()))
    
    def getSunPolarPosition(self, time: datetime.datetime):
        return self.sunPositionCalculator.pos(time.timestamp() * 1000, self.latitude, self.longitude)

    def dateChanged(self, days: int):
        currentDate = datetime.date(2026, 1, 1) + datetime.timedelta(days = days)

        self.sidePanel.dateSlider.label.setText(f"Date: {currentDate.month:02}.{currentDate.day:02}")

        self.startTime = datetime.datetime.combine(currentDate, datetime.time.min, self.utcPlus2)
        startTimeUnix = self.startTime.timestamp()
        endTime = self.startTime + datetime.timedelta(hours = 24)
        endTimeUnix = endTime.timestamp()

        xValues = np.linspace(0, 24, self.dayResolution)
        timeValues = np.linspace(startTimeUnix, endTimeUnix, self.dayResolution)

        #self.viewportPanel.viewport.makeCurrent()
        #self.viewportPanel.viewport.setupContextForRender()

        azimuths = []
        altitudes = []
        for timeSeconds in timeValues:
            time = datetime.datetime.fromtimestamp(float(timeSeconds))
            sunPolarPosition = self.getSunPolarPosition(time)

            azimuths.append(math.degrees(sunPolarPosition.azimuth))
            altitudes.append(math.degrees(sunPolarPosition.altitude))

        #self.viewportPanel.viewport.restoreContextForQt()
        #self.viewportPanel.viewport.doneCurrent()

        self.dataPanel.positionPlot.update(xValues = xValues, lineValues = (azimuths, altitudes))
        self.dataPanel.powerPlot.update(xValues = xValues, yValues = np.sin(np.asarray(xValues)))

        self.timeChanged(self.viewportPanel.timeSlider.slider.value())

    def timeChanged(self, minutes: int):
        viewportTime = self.startTime + datetime.timedelta(minutes = minutes)
        sunPosition = self.getSunPolarPosition(viewportTime)
        sunlightTransmission = self.getSunlightTransmission(viewportTime)
        scene = self.viewportPanel.viewport.scene

        scene.sunLight.position = glm.vec2(sunPosition.azimuth, sunPosition.altitude)
        scene.sunLight.sunlightTransmission = glm.float32(sunlightTransmission)
        scene.sunCamera.forward = self.getSunEucledeanPosition(sunPosition.altitude, sunPosition.azimuth)
        scene.sunCamera.updateViewMatrix()
        scene.sunCamera.updateProjectionMatrix(self.viewportPanel.width() / self.viewportPanel.height())
        scene.shadowCamera.position = scene.sunCamera.position
        scene.shadowCamera.forward = scene.sunCamera.forward
        scene.shadowCamera.updateViewMatrix()

        self.dataPanel.timeMarker.setValue(glm.mix(0, 24, self.viewportPanel.timeSlider.slider.value() / (24 * 60)))

        self.viewportPanel.timeSlider.label.setText(f"Viewport time: {viewportTime.hour:02}:{viewportTime.minute:02}")

        self.viewportPanel.viewport.repaint()

    def calculateSolarCollectorPower(self):
        self.sidePanel.powerTable.clearContents()
        selectedSolarCollectors = self.sidePanel.solarCollectorSelector.list.getCheckedItemsData()
        self.sidePanel.powerTable.setRowCount(len(selectedSolarCollectors))

        for i, object in enumerate(selectedSolarCollectors):
            self.sidePanel.powerTable.setItem(i, 0, qtw.QTableWidgetItem(object.name))
            self.sidePanel.powerTable.setItem(i, 1, qtw.QTableWidgetItem("12.32 kWh"))

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

        self.window = qtw.QMainWindow()
        self.mainWidget = qtw.QWidget()
        self.mainLayout = qtw.QHBoxLayout()
        self.contentSideSplitter = qtw.QSplitter()

        self.sidePanel = SidePanel()

        self.viewportDataSplitter = qtw.QSplitter(qtc.Qt.Orientation.Vertical)
        
        self.viewportPanel = ViewportPanel()
        self.dataPanel = DataPanel()

        for object in self.viewportPanel.viewport.scene.rootObjects:
            self.sidePanel.solarCollectorSelector.list.addItem(object.name, object)

        self.sidePanel.dateChanged.connect(self.dateChanged)
        self.sidePanel.requestedCalculation.connect(self.calculateSolarCollectorPower)
        self.viewportPanel.timeChanged.connect(self.timeChanged)

        self.sidePanel.dateChanged.emit(self.sidePanel.dateSlider.slider.value())

        self.viewportDataSplitter.addWidget(self.viewportPanel)
        self.viewportDataSplitter.addWidget(self.dataPanel)
        self.viewportDataSplitter.setStretchFactor(0, 1)
        self.viewportDataSplitter.setStretchFactor(1, 1)
        self.viewportDataSplitter.setSizes([1, 1])

        self.contentSideSplitter.addWidget(self.viewportDataSplitter)
        self.contentSideSplitter.addWidget(self.sidePanel)
        self.contentSideSplitter.setStretchFactor(0, 3)
        self.contentSideSplitter.setStretchFactor(1, 1)
        self.mainLayout.addWidget(self.contentSideSplitter)

        self.mainWidget.setLayout(self.mainLayout)
        self.window.setCentralWidget(self.mainWidget)
        self.window.show()

        self.qtApp.exec()