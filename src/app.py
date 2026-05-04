import datetime
import math

import PyQt6.QtCore as qtc
import PyQt6.QtGui as qtg
import PyQt6.QtWidgets as qtw
import pyqtgraph as pg
import numpy as np
from numpy.typing import NDArray
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
        self.days = 0
        self.minutes = 0
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
    
    def iterateOverDay(self, days: int):
        currentDate = datetime.date(2026, 1, 1) + datetime.timedelta(days = days)

        self.sidePanel.dateSlider.label.setText(f"Date: {currentDate.month:02}.{currentDate.day:02}")

        self.startTime = datetime.datetime.combine(currentDate, datetime.time.min, self.utcPlus2)
        startTimeUnix = self.startTime.timestamp()
        endTime = self.startTime + datetime.timedelta(hours = 24)
        endTimeUnix = endTime.timestamp()

        xValues = np.linspace(0, 24, self.dayResolution)
        timeValues = np.linspace(startTimeUnix, endTimeUnix, self.dayResolution)
        return xValues, timeValues

    def dateChanged(self, days: int):
        self.days = days
        xValues, timeValues = self.iterateOverDay(self.days)

        azimuths = []
        altitudes = []
        for timeSeconds in timeValues:
            time = datetime.datetime.fromtimestamp(float(timeSeconds))
            sunPolarPosition = self.getSunPolarPosition(time)

            azimuths.append(math.degrees(sunPolarPosition.azimuth))
            altitudes.append(math.degrees(sunPolarPosition.altitude))

        self.dataPanel.positionPlot.update(xValues = xValues, lineValues = (azimuths, altitudes))

        self.timeChanged(self.viewportPanel.timeSlider.slider.value())

    def timeChanged(self, minutes: int):
        self.minutes = minutes
        viewportTime = self.startTime + datetime.timedelta(minutes = minutes)
        sunPosition = self.getSunPolarPosition(viewportTime)
        sunlightTransmission = self.getSunlightTransmission(viewportTime)
        scene = self.viewportPanel.viewport.scene

        scene.sunLight.position = glm.vec2(sunPosition.azimuth, sunPosition.altitude)
        scene.sunLight.sunlightTransmission = glm.float32(sunlightTransmission)
        scene.sunCamera.forward = self.getSunEucledeanPosition(sunPosition.altitude, sunPosition.azimuth)
        scene.sunCamera.updateViewMatrix()
        scene.sunCamera.updateProjectionMatrix(self.viewportPanel.viewport.width() / self.viewportPanel.viewport.height())
        scene.shadowCamera.position = scene.sunCamera.position
        scene.shadowCamera.forward = scene.sunCamera.forward
        scene.shadowCamera.updateViewMatrix()

        timeMarkerValue = glm.mix(0, 24, self.viewportPanel.timeSlider.slider.value() / (24 * 60))
        self.dataPanel.timeMarker1.setValue(timeMarkerValue)
        self.dataPanel.timeMarker2.setValue(timeMarkerValue)

        self.viewportPanel.timeSlider.label.setText(f"Viewport time: {viewportTime.hour:02}:{viewportTime.minute:02}")

        self.viewportPanel.viewport.repaint()

    def timeIntervalChanged(self, timeInterval: tuple[int, int]):
        start, end = timeInterval
        intervalStartTime = self.startTime + datetime.timedelta(minutes = start * 15)
        intervalEndTime = self.startTime + datetime.timedelta(minutes = end * 15)

        xValues, timeValues = self.iterateOverDay(self.days)

        self.sidePanel.exposureTimeIntervalSlider.label.setText(
            f"Time interval: {intervalStartTime.hour:02}:{intervalStartTime.minute:02} - {intervalEndTime.hour:02}:{intervalEndTime.minute:02}"
        )
        selectedSolarCollectors: list[Object] = self.sidePanel.solarCollectorSelector.list.getCheckedItemsData()
        for i, object in enumerate(selectedSolarCollectors):
            self.sidePanel.powerTable.setItem(i, 0, qtw.QTableWidgetItem(object.name))
            intervalPowerCurve = []
            for timeValue, power in zip(timeValues, self.powerCurves[i]):
                time = datetime.datetime.fromtimestamp(timeValue, tz = self.utcPlus2)
                if intervalStartTime <= time <= intervalEndTime:
                    intervalPowerCurve.append(power)
            energy = np.trapezoid(np.asarray(intervalPowerCurve))
            self.sidePanel.powerTable.setItem(i, 1, qtw.QTableWidgetItem(f"{energy / 1000:.2f} kWh"))

        self.dataPanel.intervalStartMarker.setPos(glm.mix(0, 24, start / (24 * 4)))
        self.dataPanel.intervalEndMarker.setPos(glm.mix(0, 24, end / (24 * 4)))

    def solarCollectorPowerCurve(self, solarCollector: Object, timeValues: NDArray[np.float64]):
        self.viewportPanel.viewport.makeCurrent()
        self.viewportPanel.viewport.setupContextForRender()

        powerCurve = []
        for timeValue in timeValues:
            time = datetime.datetime.fromtimestamp(timeValue, tz = self.utcPlus2)
            sunPolarPos = self.getSunPolarPosition(time)
            sunEucledeanPos = self.getSunEucledeanPosition(sunPolarPos.altitude, sunPolarPos.azimuth)
            sunlightTransmission = self.getSunlightTransmission(time)
            numVisibleFragments = self.viewportPanel.viewport.renderer.measurementPass(self.viewportPanel.viewport.scene, solarCollector, sunlightTransmission, sunEucledeanPos, sunEucledeanPos)
            powerCurve.append(numVisibleFragments)

        self.viewportPanel.viewport.restoreContextForQt()
        self.viewportPanel.viewport.doneCurrent()

        return powerCurve

    def calculateSolarCollectorPowers(self):
        self.sidePanel.powerTable.clearContents()

        selectedSolarCollectors: list[Object] = self.sidePanel.solarCollectorSelector.list.getCheckedItemsData()
        numSolarCollectors = len(selectedSolarCollectors)
        self.sidePanel.powerTable.setRowCount(numSolarCollectors)
        self.dataPanel.powerPlot.numLines = numSolarCollectors

        xValues, timeValues = self.iterateOverDay(self.days)

        self.powerCurves = []
        for object in selectedSolarCollectors:
            powerCurve = self.solarCollectorPowerCurve(object, timeValues)
            self.powerCurves.append(powerCurve)

        self.dataPanel.powerPlot.update(xValues = xValues, lineValues = self.powerCurves, labels = [object.name for object in selectedSolarCollectors])

        self.timeIntervalChanged(self.sidePanel.exposureTimeIntervalSlider.slider.value())

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
        self.sidePanel.requestedCalculation.connect(self.calculateSolarCollectorPowers)
        self.sidePanel.timeIntervalChanged.connect(self.timeIntervalChanged)
        self.viewportPanel.timeChanged.connect(self.timeChanged)

        self.sidePanel.dateChanged.emit(self.sidePanel.dateSlider.slider.value())
        self.sidePanel.timeIntervalChanged.emit(self.sidePanel.exposureTimeIntervalSlider.slider.value())

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