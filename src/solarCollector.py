from enum import Enum
from pathlib import Path

from pyglm import glm

from transform import Transform
from object import Object
from gltfLoader import GltfLoader
from renderPass import RenderPass

class SolarCollectorLocation(Enum):
    OnRoof = 1
    OnShed = 2
    NextToPool = 3

class SolarCollector(Object):
    def __init__(self, modelPath: Path):
        loaded = GltfLoader.loadFirstObject(modelPath)
        super().__init__(loaded.mesh, loaded.transform, loaded.children, loaded.name)

    def initialize(self):
        super().initialize()

    def render(self, renderPass: RenderPass, ancestorTransforms: list[glm.mat4x4] = None):
        super().render(renderPass, ancestorTransforms)

    def release(self):
        super().release()