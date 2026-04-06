import moderngl as gl
import numpy as np
from pyglm import glm

from camera import Camera
from material import Material
from object import Object
from house import House

class Scene:
    def __init__(self):
        self.glContext: gl.Context = None
        self.camera = Camera()
        self.house = House()
        self.sunPosition: glm.vec2 = glm.vec2(0)
        self.sunlightTransmission: float = glm.float32(0)

        self.camera.updatePerspectiveProjection(1.0)
        self.camera.updateCameraProjection()

    def initialize(self):
        self.glContext = gl.get_context()
        self.house.initialize()

    def render(self):
        Material.setUniformOnMaterials("u_perspectiveProjection", self.camera.perspectiveProjection)
        Material.setUniformOnMaterials("u_cameraProjection", self.camera.cameraProjection)
        Material.setUniformOnMaterials("u_sunPosition", self.sunPosition)
        Material.setUniformOnMaterials("u_sunlightTransmission", self.sunlightTransmission)

        self.house.render()

    def release(self):
        self.house.release()