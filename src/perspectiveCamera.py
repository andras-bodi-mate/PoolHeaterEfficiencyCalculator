from pyglm import glm

from camera import Camera
from controller import Controller

class PerspectiveCamera(Camera):
    def __init__(self, controller: Controller = None, fixedAspectRatio = False):
        super().__init__(controller, fixedAspectRatio)

        self.updateProjectionMatrix(1.0)
        self.updateViewMatrix()

    def updateProjectionMatrix(self, aspectRatio):
        self.projectionMatrix = glm.perspective(
            glm.radians(60.0),
            aspectRatio,
            0.1,
            1000.0
        )

    def updateViewMatrix(self):
        super().updateViewMatrix()
        self.viewMatrix = glm.lookAt(self.position, self.position + self.forward, glm.vec3(0, 1, 0))