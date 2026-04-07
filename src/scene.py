import moderngl as gl
import numpy as np
from pyglm import glm

from core import Core
from camera import Camera
from sunCamera import SunCamera
from material import Material
from house import House
from solarCollector import SolarCollector, SolarCollectorLocation

class Scene:
    def __init__(self):
        self.glContext: gl.Context = None
        self.camera = Camera()
        self.house = House()
        self.roofSolarCollector = SolarCollector(Core.getPath("res/models/solarCollectorOnRoof.gltf"))
        self.shedSolarCollector = SolarCollector(Core.getPath("res/models/solarCollectorOnShed.gltf"))
        self.sunCamera = SunCamera()
        self.sunPosition: glm.vec2 = glm.vec2(0)
        self.sunlightTransmission: float = glm.float32(0)

        self.activeCamera: Camera | SunCamera = self.camera
        self.selectedSolarCollector = SolarCollectorLocation.OnRoof

    def initialize(self):
        self.glContext = gl.get_context()
        self.house.initialize()
        self.roofSolarCollector.initialize()
        self.shedSolarCollector.initialize()

    def render(self):
        Material.setUniformOnMaterials("u_perspectiveProjection", self.activeCamera.perspectiveProjection)
        Material.setUniformOnMaterials("u_cameraProjection", self.activeCamera.cameraProjection)
        Material.setUniformOnMaterials("u_sunPosition", self.sunPosition)
        Material.setUniformOnMaterials("u_sunlightTransmission", self.sunlightTransmission)

        self.house.render()
        match self.selectedSolarCollector:
            case SolarCollectorLocation.OnRoof:
                self.roofSolarCollector.render()
            case SolarCollectorLocation.OnShed:
                self.shedSolarCollector.render()

    def release(self):
        self.house.release()
        self.roofSolarCollector.release()
        self.shedSolarCollector.release()