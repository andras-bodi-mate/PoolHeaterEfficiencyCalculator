from pyglm import glm

from transform import Transform

class Camera:
    def __init__(self):
        self.perspectiveProjection: glm.mat4x4 = None
        self.cameraProjection: glm.mat4x4 = None
        self.pitch = -0.4
        self.yaw = 0.0
        self.distance = 10
        self.turnSensitivity = 0.005
        self.zoomSensitivity = 0.005

        self.updatePerspectiveProjection(1.0)
        self.updateCameraProjection()

    def updatePerspectiveProjection(self, aspectRatio):
        self.perspectiveProjection = glm.perspective(
            glm.radians(60.0),
            aspectRatio,
            0.1,
            1000.0
        )

    def updateCameraProjection(self):
        orbitPosition = self.getPosition()
        position = orbitPosition
        forward = -self.distance * glm.normalize(orbitPosition)
        self.cameraProjection = glm.lookAt(position, position + forward, glm.vec3(0, 1, 0))

    def getPosition(self):
        return self.distance * (glm.quat(glm.vec3(self.pitch, self.yaw, 0)) * glm.vec3(0, 0, 1))
    
    def rotate(self, mouseDelta: glm.vec2):
        self.pitch = glm.clamp(self.pitch - mouseDelta.y / 100, glm.radians(-89), glm.radians(89))
        self.yaw += -mouseDelta.x / 100

    def zoom(self, angleDelta: float):
        self.distance *= (1 - self.zoomSensitivity) ** angleDelta