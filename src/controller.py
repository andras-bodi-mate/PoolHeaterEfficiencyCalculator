from abc import ABC, abstractmethod

from pyglm import glm

class Controller(ABC):
    def __init__(self):
        super().__init__()

    @abstractmethod
    def update(camera):
        pass

    @abstractmethod
    def mouseDragged(self, mouseDelta: glm.vec2):
        pass

    @abstractmethod
    def wheelScrolled(self, angleDelta: float):
        pass