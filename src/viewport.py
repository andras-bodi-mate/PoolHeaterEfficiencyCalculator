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
from orbitController import OrbitController
from sunLight import SunLight
from house import House
from solarCollector import SolarCollector
from renderer import Renderer
from renderPass import RenderPassInfo

class Viewport(qglw.QOpenGLWidget):
    def __init__(self):
        super().__init__()

        self.viewportLayout = qtw.QHBoxLayout()
        self.activeCameraCheckbox = qtw.QCheckBox("Switch to sun camera")
        self.activeCameraCheckbox.checkStateChanged.connect(self.activeCameraChanged)
        self.viewportLayout.addWidget(self.activeCameraCheckbox, alignment = qtc.Qt.AlignmentFlag.AlignTop | qtc.Qt.AlignmentFlag.AlignRight)
        self.setLayout(self.viewportLayout)

        self.setFocusPolicy(qtc.Qt.FocusPolicy.StrongFocus)
        qtw.QApplication.instance().aboutToQuit.connect(self.cleanup)
    
        self.glContext: gl.Context = None
        self.frameBuffer: gl.Framebuffer = None
        self.frameIndex = 0
        self.frameRateTimer = qtc.QElapsedTimer()
        self.frameRateTimer.start()
        self.framesSinceLastFpsUpdate = 0
        self.frameRate = 0
        self.prevMousePos: glm.vec2 = None
        self.aspectRatio = 1.0
        self.hasCleanedUp = True

        self.scene = Scene()
        self.scene.rootObjects.append(House())
        self.scene.roofSolarCollector = SolarCollector(Core.getPath("res/models/solarCollectorOnRoof.gltf"))
        self.scene.shedSolarCollector = SolarCollector(Core.getPath("res/models/solarCollectorOnShed.gltf"))
        self.scene.rootObjects.append(self.scene.roofSolarCollector)
        self.scene.rootObjects.append(self.scene.shedSolarCollector)

        self.scene.userCamera = PerspectiveCamera(controller = OrbitController())
        self.scene.sunCamera = OrthographicCamera()
        self.scene.cameras.append(self.scene.userCamera)
        self.scene.cameras.append(self.scene.sunCamera)
        self.scene.activeCamera = self.scene.userCamera

        self.scene.sunLight = SunLight()
        self.scene.lights.append(self.scene.sunLight)

        self.renderer = Renderer()

    def setupContextForRender(self):
        self.glContext.enable(gl.DEPTH_TEST)

    def restoreContextForQt(self):
        GL.glBindFramebuffer(GL.GL_FRAMEBUFFER, self.defaultFramebufferObject())

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

        renderPassInfo = RenderPassInfo(
            framebuffer = self.frameBuffer,
            viewportSize = glm.uvec2(
                self.glContext.viewport[2],
                self.glContext.viewport[3]
            )
        )
        self.renderer.render(self.scene, renderPassInfo)

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

        for camera in self.scene.cameras:
            camera.updateProjectionMatrix(self.aspectRatio)

    def mousePressEvent(self, event: qtg.QMouseEvent):
        super().mousePressEvent(event)
        self.prevMousePos = Core.toVec2(event.globalPosition())

    def mouseMoveEvent(self, event: qtg.QMouseEvent):
        super().mouseMoveEvent(event)
        if not self.scene.activeCamera.controller:
            return
        
        currentPosition = Core.toVec2(event.globalPosition())
        mouseDelta = currentPosition - self.prevMousePos
        self.prevMousePos = currentPosition

        self.scene.activeCamera.controller.mouseDragged(mouseDelta)
        self.scene.activeCamera.updateViewMatrix()
        self.repaint()
    
    def wheelEvent(self, event: qtg.QWheelEvent):
        super().wheelEvent(event)
        if not self.scene.activeCamera.controller:
            return

        angleDelta = Core.toVec2(event.angleDelta()).y
        self.scene.activeCamera.controller.wheelScrolled(angleDelta)
        self.scene.activeCamera.updateViewMatrix()
        self.repaint()

    def keyPressEvent(self, event: qtg.QKeyEvent):
        super().keyPressEvent(event)
        if event.isAutoRepeat():
            return
        
        if event.key() == qtc.Qt.Key.Key_R and event.modifiers() & qtc.Qt.KeyboardModifier.ControlModifier:
            pass

    def activeCameraChanged(self):
        if self.activeCameraCheckbox.isChecked():
            self.scene.activeCamera = self.scene.sunCamera
        else:
            self.scene.activeCamera = self.scene.userCamera
        self.repaint()