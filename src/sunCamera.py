from pyglm import glm

class SunCamera:
    def __init__(self):
        self.perspectiveProjection: glm.mat4x4 = None
        self.cameraProjection: glm.mat4x4 = None
        self.direction = glm.vec3(0)
        self.distance = 50.0

        self.updatePerspectiveProjection(1.0)
        self.updateCameraProjection()

    def updatePerspectiveProjection(self, aspectRatio):
        size = 20.0
        self.perspectiveProjection = glm.ortho(
            -size * aspectRatio, size * aspectRatio,
            -size, size,
            0.1, 200.0
        )

    def updateCameraProjection(self):
        eye = -self.direction * self.distance
        target = glm.vec3(0, 0, 0)
        up = glm.vec3(0, 1, 0)

        self.cameraProjection = glm.lookAt(eye, target, up)