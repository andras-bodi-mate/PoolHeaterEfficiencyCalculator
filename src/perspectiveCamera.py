from pyglm import glm

from camera import Camera

class PerspectiveCamera(Camera):
    def __init__(self):
        super().__init__()
        self.pitch = -0.4
        self.yaw = 0.0
        self.distance = 10
        self.turnSensitivity = 0.005
        self.zoomSensitivity = 0.005

    def updateProjectionMatrix(self, aspectRatio):
        self.projectionMatrix = glm.perspective(
            glm.radians(60.0),
            aspectRatio,
            0.1,
            1000.0
        )

    def updateViewMatrix(self):
        orbitPosition = self.getPosition()
        position = orbitPosition
        forward = -self.distance * glm.normalize(orbitPosition)
        self.viewMatrix = glm.lookAt(position, position + forward, glm.vec3(0, 1, 0))

    def getPosition(self):
        return self.distance * (glm.quat(glm.vec3(self.pitch, self.yaw, 0)) * glm.vec3(0, 0, 1))
    
    def rotate(self, mouseDelta: glm.vec2):
        self.pitch = glm.clamp(self.pitch - mouseDelta.y / 100, glm.radians(-89), glm.radians(89))
        self.yaw += -mouseDelta.x / 100

    def zoom(self, angleDelta: float):
        self.distance *= (1 - self.zoomSensitivity) ** angleDelta