from pyglm import glm

from controller import Controller
from camera import Camera

class ZoomController(Controller):
    def fromCamera(camera: Camera):
        controller = ZoomController()
        controller.scale = camera.scale
        return controller

    def __init__(self):
        super().__init__()
        self.scale = 1.0
        self.zoomSensitivity = 0.005

    def update(self, camera: Camera):
        camera.scale = self.scale

    def wheelScrolled(self, angleDelta: float):
        self.scale *= (1 - self.zoomSensitivity) ** angleDelta