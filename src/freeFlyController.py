import PyQt6.QtCore as qtc
from pyglm import glm

from controller import Controller
from camera import Camera

class FreeFlyController(Controller):
    def fromCamera(camera: Camera):
        controller = FreeFlyController()
        controller.position = camera.position
        direction = glm.polar(camera.forward)
        controller.pitch, controller.yaw = direction.xy
        return controller

    def __init__(self):
        super().__init__(focusable = True)
        self.position = glm.vec3(0.0)
        self.pitch = 0.0
        self.yaw = 0.0
        self.up = glm.vec3(0.0, 1.0, 0.0)
        self.flySpeed = 500.0
        self.turnSensitivity = 0.2

    def getForward(self):
        return glm.euclidean(glm.vec2(self.pitch, self.yaw))

    def update(self, camera: Camera):
        camera.position = self.position
        camera.forward = self.getForward()

    def mouseMoved(self, mouseDelta: glm.vec2, deltaTime: float):
        delta = self.turnSensitivity * deltaTime
        self.yaw -= mouseDelta.x * delta
        self.pitch = glm.clamp(self.pitch - mouseDelta.y * delta, glm.radians(-89), glm.radians(89))

    def handlePressedKeys(self, pressedKeys: set[qtc.Qt.Key], deltaTime: float):
        delta = self.flySpeed * deltaTime
        if qtc.Qt.Key.Key_Shift in pressedKeys:
            delta *= 2 

        forward = self.getForward()
        deltaForward = forward * delta
        deltaRight = glm.normalize(glm.cross(forward, self.up)) * delta
        deltaUp = self.up * delta

        if qtc.Qt.Key.Key_W in pressedKeys:
            self.position += deltaForward
        if qtc.Qt.Key.Key_S in pressedKeys:
            self.position -= deltaForward
        if qtc.Qt.Key.Key_A in pressedKeys:
            self.position -= deltaRight
        if qtc.Qt.Key.Key_D in pressedKeys:
            self.position += deltaRight
        if qtc.Qt.Key.Key_Q in pressedKeys or qtc.Qt.Key.Key_Control in pressedKeys:
            self.position -= deltaUp
        if qtc.Qt.Key.Key_E in pressedKeys or qtc.Qt.Key.Key_Space in pressedKeys:
            self.position += deltaUp