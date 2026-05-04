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
from object import Object

class Renderer(GraphicsResource):
    def __init__(self):
        super().__init__()
        self.measurementResolution = 1024
        self.measurementDepthBuffer: gl.Renderbuffer = None
        self.measurementFramebuffer: gl.Framebuffer = None

    def initialize(self):
        super().initialize()
        self.measurementDepthBuffer = self.glContext.depth_renderbuffer((self.measurementResolution, self.measurementResolution))
        self.measurementFramebuffer = self.glContext.framebuffer(depth_attachment = self.measurementDepthBuffer)

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
                    object.render(RenderPass.ShadowPass)

    def forwardPass(self, scene: Scene):
        Material.setUniformOnMaterials("u_lightSpaceMatrix", scene.shadowCamera.projectionMatrix * scene.shadowCamera.viewMatrix)
        Material.setUniformOnMaterials("s_shadowMap", glm.uint32(0))
        scene.sunLight.shadowMap.use(0)

        for object in scene.rootObjects:
            object.render(RenderPass.ForwardPass)

    def measurementPass(self, scene: Scene, solarCollector: Object, sunlightTransmission: float, cameraPos: glm.vec3, cameraForward: glm.vec3):
        self.measurementFramebuffer.use()
        self.glContext.viewport = (0, 0, self.measurementResolution, self.measurementResolution)
        self.glContext.clear(depth = 1.0)
        scene.measurementCamera.position = cameraPos
        scene.measurementCamera.forward = cameraForward
        scene.measurementCamera.updateViewMatrix()
        self.useCamera(scene.measurementCamera)

        house = scene.rootObjects[0]
        house.render(RenderPass.ShadowPass)
        
        query = self.glContext.query(samples = True)
        with query:
            solarCollector.render(RenderPass.ShadowPass)

        totalArea = (2 * scene.measurementCamera.scale) ** 2
        pixelArea = totalArea / (self.measurementResolution ** 2)

        solarIrradiance = 1361 * sunlightTransmission
        power = solarIrradiance * query.samples * pixelArea

        return power

    def render(self, scene: Scene, renderPassInfo: RenderPassInfo):
        Material.setUniformOnMaterials("u_sunPosition", scene.sunLight.position)
        Material.setUniformOnMaterials("u_sunlightTransmission", scene.sunLight.sunlightTransmission)

        query = self.glContext.query(time = True)
        with query:
            if renderPassInfo.enableShadowPass:
                self.useCamera(scene.shadowCamera)
                self.shadowPass(scene)

            self.useCamera(scene.activeCamera)
            renderPassInfo.framebuffer.use()
            self.glContext.viewport = (0, 0, renderPassInfo.viewportSize.x, renderPassInfo.viewportSize.y)
            if renderPassInfo.enableForwardPass:
                self.forwardPass(scene)
        
        return query.elapsed

    def release(self):
        super().release()