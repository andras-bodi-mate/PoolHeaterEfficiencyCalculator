from pathlib import Path

from pyglm import glm

from transform import Transform
from core import Core
from object import Object
from gltfLoader import GltfLoader
from renderPass import RenderPass

class House(Object):
    def __init__(self, path: Path):
        loaded = GltfLoader.loadFirstObject(path)
        super().__init__(loaded.mesh, loaded.transform, loaded.children, loaded.name)
        self.transform = Transform(glm.vec3(0.0, 0.0, 0.0))

    def initialize(self):
        super().initialize()

    def render(self, renderPass: RenderPass, ancestorTransforms: list[glm.mat4x4] = None):
        super().render(renderPass, ancestorTransforms)

    def release(self):
        super().release()