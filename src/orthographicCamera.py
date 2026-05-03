from pyglm import glm

from camera import Camera
from controller import Controller

class OrthographicCamera(Camera):
    def __init__(self, controller: Controller = None, fixedAspectRatio = False):
        super().__init__(controller, fixedAspectRatio)
        self.distance = 50.0

        self.updateProjectionMatrix(1.0)
        self.updateViewMatrix()

    def updateProjectionMatrix(self, aspectRatio):
        if self.controller is not None:
            self.controller.update(self)

        self.projectionMatrix = glm.ortho(
            -self.scale * aspectRatio, self.scale * aspectRatio,
            -self.scale, self.scale,
            1.0, 100.0
        )
    
    def updateViewMatrix(self):
        super().updateViewMatrix()
        eye = -self.forward * self.distance
        target = glm.vec3(0, 0, 0)
        up = glm.vec3(0, 1, 0)

        self.viewMatrix = glm.lookAt(eye, target, up)