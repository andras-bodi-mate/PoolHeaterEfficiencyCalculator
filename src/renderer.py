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
        Material.setUniformOnMaterials("u_projectionTransform", camera.projectionMatrix)
        Material.setUniformOnMaterials("u_viewTransform", camera.viewMatrix)

    def shadowPass(self, scene: Scene):
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

    def forwardPass(self, scene: Scene):
        Material.setUniformOnMaterials("u_lightSpaceMatrix", scene.shadowCamera.projectionMatrix * scene.shadowCamera.viewMatrix)
        Material.setUniformOnMaterials("s_shadowMap", glm.uint32(0))
        scene.sunLight.shadowMap.use(0)

        for object in scene.rootObjects:
            object.render(RenderPass.ForwardPass)

    def render(self, scene: Scene, renderPassInfo: RenderPassInfo):
        Material.setUniformOnMaterials("u_sunPosition", scene.sunLight.position)
        Material.setUniformOnMaterials("u_sunlightTransmission", scene.sunLight.sunlightTransmission)

        if renderPassInfo.enableShadowPass:
            self.useCamera(scene.shadowCamera)
            self.shadowPass(scene)

        self.useCamera(scene.activeCamera)
        renderPassInfo.framebuffer.use()
        self.glContext.viewport = (0, 0, renderPassInfo.viewportSize.x, renderPassInfo.viewportSize.y)
        if renderPassInfo.enableForwardPass:
            self.forwardPass(scene)

    def release(self):
        super().release()