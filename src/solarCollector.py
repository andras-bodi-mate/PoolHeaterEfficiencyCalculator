from enum import Enum

from pyglm import glm

from transform import Transform
from core import Core
from gltfLoader import GltfLoader

class SolarCollectorLocation(Enum):
    OnRoof = 1
    OnShed = 2
    NextToPool = 3

class SolarCollector:
    def __init__(self, modelPath):
        gltfLoader = GltfLoader(modelPath)
        self.object = gltfLoader.loadRootObjects()[0]
        self.transform = Transform(glm.vec3(0.0, 0.0, 0.0))

    def initialize(self):
        self.object.initialize()

    def render(self):
        self.object.render([self.transform.getMatrix()])

    def release(self):
        self.object.release()