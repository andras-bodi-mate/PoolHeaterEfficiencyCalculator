from material import Material
from scene import Scene

class Renderer:
    def __init__(self):
        pass

    def initialize(self):
        pass

    def render(self, scene: Scene):
        Material.setUniformOnMaterials("u_perspectiveProjection", self.activeCamera.perspectiveProjection)
        Material.setUniformOnMaterials("u_cameraProjection", self.activeCamera.cameraProjection)
        Material.setUniformOnMaterials("u_sunPosition", self.sunPosition)
        Material.setUniformOnMaterials("u_sunlightTransmission", self.sunlightTransmission)

        for object in scene.rootObjects:
            object.render()

    def release(self):
        pass