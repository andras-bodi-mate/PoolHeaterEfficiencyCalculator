import moderngl as gl

from material import Material
from scene import Scene
from renderPass import RenderPass
from graphicsResource import GraphicsResource

class Renderer(GraphicsResource):
    def __init__(self):
        super().__init__()

    def initialize(self):
        super().initialize()

    def render(self, scene: Scene):
        Material.setUniformOnMaterials("u_perspectiveProjection", scene.activeCamera.projectionMatrix)
        Material.setUniformOnMaterials("u_cameraProjection", scene.activeCamera.viewMatrix)
        Material.setUniformOnMaterials("u_sunPosition", scene.sunLight.position)
        Material.setUniformOnMaterials("u_sunlightTransmission", scene.sunLight.sunlightTransmission)

        # for light in scene.lights:
        #     prevViewport = self.glContext.viewport
        #     self.glContext.viewport = (0, 0, light.framebufferResolution, light.framebufferResolution)

        #     for object in scene.rootObjects:
        #         object.render(RenderPass.ShadowPass)

        #     self.glContext.viewport = prevViewport

        for object in scene.rootObjects:
            object.render(RenderPass.ForwardPass)

    def release(self):
        super().release()