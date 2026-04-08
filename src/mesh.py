from meshPrimitive import MeshPrimitive
from renderPass import RenderPass

class Mesh:
    def __init__(self, primitives: list[MeshPrimitive]):
        self.primitives = primitives

    def initialize(self):
        for primitive in self.primitives:
            primitive.initialize()

    def render(self, renderPass: RenderPass):
        for primitive in self.primitives:
            primitive.render(renderPass)

    def release(self):
        for primitive in self.primitives:
            primitive.release()