from material import Material
from scene import Scene

class Renderer:
    def __init__(self):
        pass

    def initialize(self):
        pass

    def render(self, scene: Scene):
        Material.setUniformOnMaterials("u_perspectiveProjection", scene.activeCamera.projectionMatrix)
        Material.setUniformOnMaterials("u_cameraProjection", scene.activeCamera.viewMatrix)
        Material.setUniformOnMaterials("u_sunPosition", scene.sunLight.position)
        Material.setUniformOnMaterials("u_sunlightTransmission", scene.sunLight.sunlightTransmission)

        for object in scene.rootObjects:
            object.render()

    def release(self):
        pass