import moderngl as gl
from pyglm import glm
import numpy as np

from material import Material
from scene import Scene
from renderPass import RenderPass, RenderPassInfo
from graphicsResource import GraphicsResource
from sunLight import SunLight
from house import House
from camera import Camera
from solarCollector import SolarCollector

class Renderer(GraphicsResource):
    def __init__(self):
        super().__init__()

    def initialize(self):
        super().initialize()

    def useCamera(self, camera: Camera):
        Material.setUniformOnMaterials("u_perspectiveProjection", camera.projectionMatrix)
        Material.setUniformOnMaterials("u_cameraProjection", camera.viewMatrix)

    def render(self, scene: Scene, renderPassInfo: RenderPassInfo):
        Material.setUniformOnMaterials("u_sunPosition", scene.sunLight.position)
        Material.setUniformOnMaterials("u_sunlightTransmission", scene.sunLight.sunlightTransmission)

        self.useCamera(scene.shadowCamera)
        for light in scene.lights:
            if isinstance(light, SunLight):
                light.framebuffer.use()
                light.framebuffer.clear(depth = 1.0)
                self.glContext.viewport = (0, 0, light.framebufferResolution, light.framebufferResolution)

                for object in scene.rootObjects:
                    if isinstance(object, House):
                        objectId = 1
                    elif isinstance(object, SolarCollector):
                        objectId = 2
                    else:
                        objectId = 3

                    Material.setUniformOnMaterials("u_objectId", glm.uint32(objectId))
                    object.render(RenderPass.ShadowPass)
                objectTypeMapBytes = light.framebuffer.read(components = 1, dtype = "u4")
                objectTypeMap = np.frombuffer(objectTypeMapBytes, dtype = np.uint32).reshape((light.framebufferResolution, light.framebufferResolution))
                unique, counts = np.unique(objectTypeMap, return_counts = True)
                unique, counts = list(unique), list(counts)
                if 2 in unique:
                    print(counts[unique.index(2)])
                else:
                    print(0)

        self.useCamera(scene.activeCamera)
        renderPassInfo.framebuffer.use()
        self.glContext.viewport = (0, 0, renderPassInfo.viewportSize.x, renderPassInfo.viewportSize.y)
        for object in scene.rootObjects:
            object.render(RenderPass.ForwardPass)

    def release(self):
        super().release()