from pyglm import glm

from controller import Controller
from camera import Camera

class OrbitController(Controller):
    def __init__(self):
        super().__init__()
        self.pitch = -0.4
        self.yaw = 0.0
        self.distance = 10
        self.turnSensitivity = 0.005
        self.zoomSensitivity = 0.005

    def update(self, camera: Camera):
        orbitPosition = self.getPosition()
        camera.position = orbitPosition
        camera.forward = -self.distance * glm.normalize(orbitPosition)

    def getPosition(self):
        return self.distance * (glm.quat(glm.vec3(self.pitch, self.yaw, 0)) * glm.vec3(0, 0, 1))
    
    def mouseMoved(self, mouseDelta: glm.vec2):
        self.pitch = glm.clamp(self.pitch - mouseDelta.y / 100, glm.radians(-89), glm.radians(89))
        self.yaw += -mouseDelta.x / 100
    
    def wheelScrolled(self, angleDelta: float):
        self.distance *= (1 - self.zoomSensitivity) ** angleDelta