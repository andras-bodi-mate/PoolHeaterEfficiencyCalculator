from functools import reduce

from pyglm import glm

from mesh import Mesh
from transform import Transform
from material import Material

class Object:
    def __init__(self, mesh: Mesh, transform: Transform, children: list["Object"] = None, name = None):
        self.mesh = mesh
        self.transform = transform
        self.children: list["Object"] = children if children else []
        self.name = name
        self.isVisible = True

    def initialize(self):
        self.mesh.initialize()
        for child in self.children:
            child.initialize()

    def render(self, ancestorTransforms: list[glm.mat4x4] = None):
        if not self.isVisible:
            return

        transform = self.transform.getMatrix()
        ancestorTransforms = ancestorTransforms + [transform] if ancestorTransforms else [transform]
        finalTransform = reduce(lambda a, b: b * a, reversed(ancestorTransforms))
        normalTransform = glm.transpose(glm.inverse(glm.mat3(finalTransform)));
        Material.setUniformOnMaterials("u_modelTransform", finalTransform)
        Material.setUniformOnMaterials("u_modelNormalTransform", normalTransform)
        self.mesh.render()
        for child in self.children:
            child.render(ancestorTransforms)

    def release(self):
        self.mesh.release()
        for child in self.children:
            child.release()