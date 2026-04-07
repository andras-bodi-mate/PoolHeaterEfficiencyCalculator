from PyQt6 import QtCore as qtc
from PyQt6 import QtGui as qtg
from PyQt6 import QtWidgets as qtw
from PyQt6 import QtOpenGL as qgl
from PyQt6 import QtOpenGLWidgets as qglw
import moderngl as gl
from pyglm import glm
from math import pi

from core import Core
from scene import Scene
from material import Material

class Viewport(qglw.QOpenGLWidget):
    def __init__(self):
        super().__init__()

        self.viewportLayout = qtw.QHBoxLayout()
        self.activeCameraCheckbox = qtw.QCheckBox("Switch to sun camera")
        self.activeCameraCheckbox.checkStateChanged.connect(self.activeCameraChanged)
        self.viewportLayout.addWidget(self.activeCameraCheckbox, alignment = qtc.Qt.AlignmentFlag.AlignTop | qtc.Qt.AlignmentFlag.AlignRight)
        self.setLayout(self.viewportLayout)

        self.setFocusPolicy(qtc.Qt.FocusPolicy.StrongFocus)
    
        self.glContext: gl.Context = None
        self.frameBuffer: gl.Framebuffer = None
        self.frameIndex = 0
        self.frameRateTimer = qtc.QElapsedTimer()
        self.frameRateTimer.start()
        self.framesSinceLastFpsUpdate = 0
        self.frameRate = 0
        self.prevMousePos: glm.vec2 = None
        self.aspectRatio = 1.0

        self.scene = Scene()

    def setupContextForRender(self):
        self.glContext.enable(gl.DEPTH_TEST)

    def restoreContextForQt(self):
        self.glContext.disable(gl.DEPTH_TEST)

    def initializeGL(self):
        super().initializeGL()
        self.glContext = gl.create_context()
        self.setupContextForRender()

        self.scene.initialize()

    def paintGL(self):
        super().paintGL()
        if self.frameRateTimer.elapsed() > 250:
            self.frameRate = self.framesSinceLastFpsUpdate / self.frameRateTimer.restart() * 1000
            self.framesSinceLastFpsUpdate = 0
            
        painter = qtg.QPainter(self)

        painter.beginNativePainting()
        if not self.frameBuffer:
            self.frameBuffer = self.glContext.detect_framebuffer(self.defaultFramebufferObject())

        self.frameBuffer.use()
        self.setupContextForRender()
        self.frameBuffer.clear(blue = 1.0)

        self.scene.render()

        self.restoreContextForQt()
        painter.endNativePainting()

        painter.setPen(qtg.QColor(255, 255, 255))
        painter.setFont(qtg.QFont("Consolas", 10))
        painter.drawText(qtc.QPoint(5, 15), f"FPS: {self.frameRate:.2f}")

        painter.end()

        self.frameIndex += 1
        self.framesSinceLastFpsUpdate += 1

    def resizeGL(self, w, h):
        super().resizeGL(w, h)
        devicePixelRatio = self.devicePixelRatioF()
        self.glContext.viewport = (0, 0, int(w * devicePixelRatio), int(h * devicePixelRatio))
        self.aspectRatio = self.width() / self.height()
        self.scene.camera.updatePerspectiveProjection(self.aspectRatio)
        self.scene.sunCamera.updatePerspectiveProjection(self.aspectRatio)

    def mousePressEvent(self, event: qtg.QMouseEvent):
        super().mousePressEvent(event)
        self.prevMousePos = Core.toVec2(event.globalPosition())

    def mouseMoveEvent(self, event: qtg.QMouseEvent):
        super().mouseMoveEvent(event)
        if self.activeCameraCheckbox.isChecked():
            return
        
        currentPosition = Core.toVec2(event.globalPosition())
        mouseDelta = currentPosition - self.prevMousePos
        self.prevMousePos = currentPosition
        self.scene.camera.rotate(mouseDelta)
        self.scene.camera.updateCameraProjection()
        self.repaint()
    
    def wheelEvent(self, event: qtg.QWheelEvent):
        super().wheelEvent(event)
        if self.activeCameraCheckbox.isChecked():
            return

        angleDelta = Core.toVec2(event.angleDelta()).y
        self.scene.camera.zoom(angleDelta)
        self.scene.camera.updateCameraProjection()
        self.repaint()

    def keyPressEvent(self, event: qtg.QKeyEvent):
        super().keyPressEvent(event)
        if event.isAutoRepeat():
            return
        
        if event.key() == qtc.Qt.Key.Key_R and event.modifiers() & qtc.Qt.KeyboardModifier.ControlModifier:
            self.makeCurrent()
            prevCamera = self.scene.camera
            self.scene.release()
            Material.invalidateShaderCaches()

            self.scene = Scene()
            self.scene.initialize()
            self.scene.camera = prevCamera
            self.doneCurrent()

            self.repaint()

    def activeCameraChanged(self):
        if self.activeCameraCheckbox.isChecked():
            self.scene.activeCamera = self.scene.sunCamera
        else:
            self.scene.activeCamera = self.scene.camera
        self.repaint()