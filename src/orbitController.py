from pyglm import glm

from controller import Controller
from camera import Camera

class OrbitController(Controller):
    def fromCamera(camera: Camera):
        controller = OrbitController()
        controller.distance = glm.length(camera.position)
        direction = glm.polar(camera.position)
        controller.pitch = direction.x
        controller.yaw = direction.y
        return controller

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
        return self.distance * glm.euclidean(glm.vec2(self.pitch, self.yaw))
    
    def mouseMoved(self, mouseDelta: glm.vec2):
        self.pitch = glm.clamp(self.pitch + mouseDelta.y / 100, glm.radians(-89), glm.radians(89))
        self.yaw -= mouseDelta.x / 100
    
    def wheelScrolled(self, angleDelta: float):
        self.distance *= (1 - self.zoomSensitivity) ** angleDelta