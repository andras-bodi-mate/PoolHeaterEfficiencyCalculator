from abc import ABC, abstractmethod
from enum import Enum

import PyQt6.QtCore as qtc
from pyglm import glm

class Controller(ABC):
    @staticmethod
    @abstractmethod
    def fromCamera(camera) -> "Controller":
        pass

    def __init__(self, focusable = False):
        super().__init__()
        self.focusable = focusable

    @abstractmethod
    def update(self, camera):
        pass

    def mouseReleased(self, mousePos: glm.vec2):
        pass

    def mouseMoved(self, mouseDelta: glm.vec2, deltaTime: float):
        pass

    def wheelScrolled(self, angleDelta: float):
        pass

    def handlePressedKeys(self, pressedKeys: set[qtc.Qt.Key], deltaTime: float):
        pass

class Controllers(Enum):
    FreeFly = 1
    Orbit = 2