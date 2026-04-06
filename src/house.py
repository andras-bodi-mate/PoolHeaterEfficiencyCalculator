from pyglm import glm

from transform import Transform
from core import Core
from gltfLoader import GltfLoader

class House:
    def __init__(self):
        gltfLoader = GltfLoader(Core.getPath("res/models/house.gltf"))
        rootObjects = gltfLoader.loadRootObjects()
        self.object = rootObjects[0]
        self.transform = Transform(glm.vec3(0.0, 0.0, 0.0))

    def initialize(self):
        self.object.initialize()

    def render(self):
        self.object.render([self.transform.getMatrix()])

    def release(self):
        self.object.release()