from typing import Optional

import moderngl as gl

from camera import Camera
from perspectiveCamera import PerspectiveCamera
from orthographicCamera import OrthographicCamera
from object import Object
from solarCollector import SolarCollector
from light import Light
from sunLight import SunLight

class Scene:
    def __init__(self):
        self.glContext: gl.Context = None

        self.rootObjects: list[Object] = []
        self.cameras: list[Camera] = []
        self.lights: list[Light] = []

        self.activeCamera: Camera = None

        self.userCamera: Optional[PerspectiveCamera] = None
        self.sunCamera: Optional[OrthographicCamera] = None
        self.sunLight: Optional[SunLight] = None
        self.roofSolarCollector: Optional[SolarCollector] = None
        self.shedSolarCollector: Optional[SolarCollector] = None

    def initialize(self):
        self.glContext = gl.get_context()
        for object in self.rootObjects:
            object.initialize()
        for light in self.lights:
            light.initialize()

    def release(self):
        for object in self.rootObjects:
            object.release()
        for light in self.lights:
            light.initialize()