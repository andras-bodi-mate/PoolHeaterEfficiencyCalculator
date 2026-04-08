import moderngl as gl

from material import Material
from scene import Scene
from renderPass import RenderPass, RenderPassInfo
from graphicsResource import GraphicsResource
from sunLight import SunLight

class Renderer(GraphicsResource):
    def __init__(self):
        super().__init__()

    def initialize(self):
        super().initialize()

    def render(self, scene: Scene, renderPassInfo: RenderPassInfo):
        Material.setUniformOnMaterials("u_perspectiveProjection", scene.activeCamera.projectionMatrix)
        Material.setUniformOnMaterials("u_cameraProjection", scene.activeCamera.viewMatrix)
        Material.setUniformOnMaterials("u_sunPosition", scene.sunLight.position)
        Material.setUniformOnMaterials("u_sunlightTransmission", scene.sunLight.sunlightTransmission)

        for light in scene.lights:
            if isinstance(light, SunLight):
                light.framebuffer.use()
                self.glContext.viewport = (0, 0, light.framebufferResolution, light.framebufferResolution)

                for object in scene.rootObjects:
                    object.render(RenderPass.ShadowPass)

        renderPassInfo.framebuffer.use()
        self.glContext.viewport = (0, 0, renderPassInfo.viewportSize.x, renderPassInfo.viewportSize.y)
        for object in scene.rootObjects:
            object.render(RenderPass.ForwardPass)

    def release(self):
        super().release()