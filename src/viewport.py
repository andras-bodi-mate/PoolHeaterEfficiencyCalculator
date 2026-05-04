from collections import deque

from PyQt6 import QtCore as qtc
from PyQt6 import QtGui as qtg
from PyQt6 import QtWidgets as qtw
from PyQt6 import QtOpenGL as qgl
from PyQt6 import QtOpenGLWidgets as qglw
import moderngl as gl
from pyglm import glm
from OpenGL import GL

from core import Core
from scene import Scene
from perspectiveCamera import PerspectiveCamera
from orthographicCamera import OrthographicCamera
from controller import Controllers
from orbitController import OrbitController
from freeFlyController import FreeFlyController
from zoomController import ZoomController
from sunLight import SunLight
from house import House
from gltfLoader import GltfLoader
from renderer import Renderer
from renderPass import RenderPassInfo
from widgets import Selector

class Viewport(qglw.QOpenGLWidget):
    def __init__(self):
        super().__init__()

        self.viewportLayout = qtw.QGridLayout()
        self.activeCameraCheckbox = qtw.QCheckBox("Switch to sun camera")
        self.activeCameraCheckbox.checkStateChanged.connect(self.activeCameraChanged)
        self.cameraControllerSelector = Selector([
            ("Orbit", Controllers.Orbit),
            ("Free fly", Controllers.FreeFly)
        ])
        self.cameraControllerSelector.selector.currentTextChanged.connect(self.cameraControllerChanged)
        self.viewportLayout.addWidget(self.activeCameraCheckbox, 0, 1, alignment = qtc.Qt.AlignmentFlag.AlignTop | qtc.Qt.AlignmentFlag.AlignRight)
        self.viewportLayout.addWidget(self.cameraControllerSelector, 1, 1, alignment = qtc.Qt.AlignmentFlag.AlignBottom | qtc.Qt.AlignmentFlag.AlignRight)

        qtc.QTimer.singleShot(0, self.cameraControllerChanged)

        self.setLayout(self.viewportLayout)

        self.setFocusPolicy(qtc.Qt.FocusPolicy.StrongFocus)
        qtw.QApplication.instance().aboutToQuit.connect(self.cleanup)
    
        self.glContext: gl.Context = None
        self.frameBuffer: gl.Framebuffer = None
        self.renderTimes = deque(maxlen = 100)
        self.renderTimeUpdateTimer = qtc.QTimer()
        self.prevMousePos: glm.vec2 = None
        self.aspectRatio = 1.0
        self.hasCleanedUp = True
        self.size: glm.uvec2 = None
        self.isFocused = False
        self.pressedKeys: set[qtc.Qt.Key] = set()
        self.pendingMouseDelta = glm.vec2(0.0, 0.0)
        self.inputTimer = qtc.QTimer()
        self.inputTimer.timeout.connect(self.checkInput)
        self.deltaTimeTimer = qtc.QElapsedTimer()
        self.inputRefreshRate = self.screen().refreshRate() or 60.0
        self.inputTimer.start(int(1000 / self.inputRefreshRate))
        self.deltaTimeTimer.start()

        self.scene = Scene()
        self.scene.rootObjects.append(House(Core.getPath("res/models/house.gltf")))
        self.scene.rootObjects.extend(GltfLoader(Core.getPath("res/models/solarCollectors.gltf")).loadRootObjects())

        self.scene.userCamera = PerspectiveCamera()
        self.scene.userCamera.position = glm.vec3(0.0, 0.0, -20.0)
        self.scene.sunCamera = OrthographicCamera()
        self.scene.sunCamera.controller = ZoomController.fromCamera(self.scene.sunCamera)
        self.scene.shadowCamera = OrthographicCamera(fixedAspectRatio = True)
        self.scene.measurementCamera = OrthographicCamera(fixedAspectRatio = True)
        self.scene.measurementCamera.scale = 30.0

        self.scene.cameras.append(self.scene.userCamera)
        self.scene.cameras.append(self.scene.sunCamera)
        self.scene.cameras.append(self.scene.shadowCamera)
        self.scene.cameras.append(self.scene.measurementCamera)
        self.scene.activeCamera = self.scene.userCamera

        self.scene.sunLight = SunLight()
        self.scene.lights.append(self.scene.sunLight)

        self.renderer = Renderer()

    def setupContextForRender(self):
        self.glContext.enable(gl.DEPTH_TEST)
        self.glContext.enable(gl.CULL_FACE)

    def restoreContextForQt(self):
        framebufferObject = self.defaultFramebufferObject()
        GL.glBindFramebuffer(GL.GL_FRAMEBUFFER, framebufferObject)
        GL.glBindFramebuffer(GL.GL_READ_FRAMEBUFFER, framebufferObject)
        GL.glBindFramebuffer(GL.GL_DRAW_FRAMEBUFFER, framebufferObject)

        GL.glPixelStorei(GL.GL_UNPACK_ALIGNMENT, 4)
        GL.glPixelStorei(GL.GL_PACK_ALIGNMENT, 4)

        self.glContext.disable(gl.DEPTH_TEST)
        self.glContext.disable(gl.CULL_FACE)
        self.glContext.disable(GL.GL_SCISSOR_TEST)
        self.glContext.disable(gl.BLEND)

    def initializeGL(self):
        super().initializeGL()
        self.glContext = gl.create_context()
        self.setupContextForRender()

        self.scene.initialize()
        self.renderer.initialize()

        self.hasCleanedUp = False
        self.restoreContextForQt()

    def cleanup(self):
        if self.hasCleanedUp:
            return

        self.makeCurrent()
        self.scene.release()
        self.doneCurrent()
        self.hasCleanedUp = True

    def getCenter(self):
        return self.mapToGlobal(self.rect().center())

    def grabFocus(self):
        self.grabKeyboard()
        self.grabMouse()
        self.setCursor(qtc.Qt.CursorShape.BlankCursor)
        self.setMouseTracking(True)
        qtg.QCursor.setPos(self.getCenter())
        self.pressedKeys.clear()
        self.isFocused = True

    def releaseFocus(self):
        self.releaseKeyboard()
        self.releaseMouse()
        self.unsetCursor()
        self.setMouseTracking(False)
        self.isFocused = False

    def checkInput(self):
        deltaTime = self.deltaTimeTimer.restart() / 1000
        if self.scene.activeCamera.controller is None:
            return

        wereKeysPressed = len(self.pressedKeys) != 0 and self.isFocused
        wasMouseMoved = glm.any(glm.epsilonNotEqual(self.pendingMouseDelta, glm.vec2(0.0), glm.epsilon()))
        if wereKeysPressed or wasMouseMoved:
            if wereKeysPressed:
                self.scene.activeCamera.controller.handlePressedKeys(self.pressedKeys, deltaTime)
            if wasMouseMoved:
                self.scene.activeCamera.controller.mouseMoved(self.pendingMouseDelta, deltaTime)
                self.pendingMouseDelta = glm.vec2(0.0)

            self.scene.activeCamera.updateViewMatrix()
            self.repaint()

    def paintGL(self):
        super().paintGL()    
        painter = qtg.QPainter(self)

        painter.beginNativePainting()
        if not self.frameBuffer:
            self.frameBuffer = self.glContext.detect_framebuffer(self.defaultFramebufferObject())

        self.frameBuffer.use()
        self.setupContextForRender()
        self.frameBuffer.clear(blue = 1.0)

        renderPassInfo = RenderPassInfo(
            framebuffer = self.frameBuffer,
            viewportSize = self.size
        )
        renderTime = self.renderer.render(self.scene, renderPassInfo)
        self.renderTimes.append(renderTime / 1_000_000)

        self.restoreContextForQt()
        painter.endNativePainting()

        painter.setPen(qtg.QColor(255, 255, 255))
        painter.setFont(qtg.QFont("Consolas", 10))
        painter.drawText(qtc.QPoint(5, 15), f"{(renderTime / 1_000_000):.2f} ms")

        lines = [qtc.QPointF(x + 65, y * 4) for x, y in zip(range(len(self.renderTimes)), self.renderTimes)]
        painter.drawLines(lines)

        painter.end()

    def resizeGL(self, w, h):
        super().resizeGL(w, h)
        devicePixelRatio = self.devicePixelRatioF()
        self.size = glm.uvec2(int(w * devicePixelRatio), int(h * devicePixelRatio))
        self.glContext.viewport = (0, 0, self.size.x, self.size.y)
        self.aspectRatio = self.width() / self.height()

        for camera in self.scene.cameras:
            if not camera.fixedAspectRatio:
                camera.updateProjectionMatrix(self.aspectRatio)

    def mousePressEvent(self, event: qtg.QMouseEvent):
        super().mousePressEvent(event)
        if self.scene.activeCamera.controller is None:
            return
        self.prevMousePos = Core.toVec2(event.globalPosition())
        if self.scene.activeCamera.controller.focusable:
            self.grabFocus()

    def mouseMoveEvent(self, event: qtg.QMouseEvent):
        super().mouseMoveEvent(event)
        if not self.scene.activeCamera.controller:
            return
        elif self.scene.activeCamera.controller.focusable and not self.isFocused:
            return
        
        currentPosition = Core.toVec2(event.globalPosition())
        if self.isFocused:
            centerPos = Core.toVec2(self.getCenter())
            mouseDelta = currentPosition - centerPos
            qtg.QCursor.setPos(self.getCenter())
        else:
            mouseDelta = currentPosition - self.prevMousePos
            self.prevMousePos = currentPosition

        self.pendingMouseDelta += mouseDelta
    
    def wheelEvent(self, event: qtg.QWheelEvent):
        super().wheelEvent(event)
        if not self.scene.activeCamera.controller:
            return

        angleDelta = Core.toVec2(event.angleDelta()).y
        self.scene.activeCamera.controller.wheelScrolled(angleDelta)
        if isinstance(self.scene.activeCamera.controller, ZoomController):
            self.scene.activeCamera.updateProjectionMatrix(self.aspectRatio)
        else:
            self.scene.activeCamera.updateViewMatrix()
        self.repaint()

    def keyPressEvent(self, event: qtg.QKeyEvent):
        super().keyPressEvent(event)
        self.pressedKeys.add(event.key())

        if event.key() == qtc.Qt.Key.Key_Escape:
            self.releaseFocus()

    def keyReleaseEvent(self, event: qtg.QKeyEvent):
        super().keyReleaseEvent(event)
        self.pressedKeys.discard(event.key())

    def focusOutEvent(self, event):
        super().focusOutEvent(event)
        self.releaseFocus()

    def activeCameraChanged(self):
        if self.activeCameraCheckbox.isChecked():
            self.scene.activeCamera = self.scene.sunCamera
            self.cameraControllerSelector.hide()
        else:
            self.scene.activeCamera = self.scene.userCamera
            self.cameraControllerSelector.show()
        self.repaint()

    def cameraControllerChanged(self):
        match self.cameraControllerSelector.selector.currentData():
            case Controllers.FreeFly:
                self.scene.userCamera.controller = FreeFlyController.fromCamera(self.scene.userCamera)
            case Controllers.Orbit:
                self.scene.userCamera.controller = OrbitController.fromCamera(self.scene.userCamera)
        self.scene.userCamera.updateViewMatrix()
        self.repaint()