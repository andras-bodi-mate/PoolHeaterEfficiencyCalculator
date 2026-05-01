from abc import ABC, abstractmethod
from typing import Optional

from pyglm import glm

from controller import Controller

class Camera(ABC):
    def __init__(self, controller: Optional[Controller] = None, fixedAspectRatio = False):
        self.fixedAspectRatio = fixedAspectRatio
        self.position = glm.vec3(0.0)
        self.forward = glm.vec3(0.0, 0.0, -1.0)
        self.scale = 1500.0

        self.projectionMatrix: glm.mat4x4 = None
        self.viewMatrix: glm.mat4x4 = None

        self.controller = controller

    @abstractmethod
    def updateProjectionMatrix(self, aspectRatio: float):
        pass

    @abstractmethod
    def updateViewMatrix(self):
        if self.controller is not None:
            self.controller.update(self)