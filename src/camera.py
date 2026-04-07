from pyglm import glm
from abc import ABC, abstractmethod

class Camera(ABC):
    def __init__(self):
        self.projectionMatrix: glm.mat4x4 = None
        self.viewMatrix: glm.mat4x4 = None

        self.updateProjectionMatrix(1.0)
        self.updateViewMatrix()

    @abstractmethod
    def updateProjectionMatrix(self, aspectRatio: float):
        pass

    @abstractmethod
    def updateViewMatrix(self):
        pass