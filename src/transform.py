from pyglm import glm

class Transform:
    def __init__(self, position = glm.vec3(0.0), rotation = glm.quat(), scale = glm.vec3(1.0)):
        self.position = position
        self.rotation = rotation
        self.scale = scale

    def getMatrix(self) -> glm.mat4x4:
        translation = glm.translate(self.position)
        rotation = glm.mat4_cast(self.rotation)
        scale = glm.scale(self.scale)
        return translation * rotation * scale