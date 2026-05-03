from graphicsResource import GraphicsResource
from camera import Camera
from perspectiveCamera import PerspectiveCamera
from orthographicCamera import OrthographicCamera
from object import Object
from light import Light
from sunLight import SunLight

class Scene(GraphicsResource):
    def __init__(self):
        super().__init__()

        self.rootObjects: list[Object] = []
        self.cameras: list[Camera] = []
        self.lights: list[Light] = []

        self.activeCamera: Camera = None

        self.userCamera: PerspectiveCamera = None
        self.sunCamera: OrthographicCamera = None
        self.shadowCamera: OrthographicCamera = None
        self.measurementCamera: OrthographicCamera = None
        self.sunLight: SunLight = None

    def initialize(self):
        super().initialize()
        for object in self.rootObjects:
            object.initialize()
        for light in self.lights:
            light.initialize()

    def release(self):
        super().release()
        for object in self.rootObjects:
            object.release()
        for light in self.lights:
            light.release()