from meshPrimitive import MeshPrimitive

class Mesh:
    def __init__(self, primitives: list[MeshPrimitive]):
        self.primitives = primitives

    def initialize(self):
        for primitive in self.primitives:
            primitive.initialize()

    def render(self):
        for primitive in self.primitives:
            primitive.render()

    def release(self):
        for primitive in self.primitives:
            primitive.release()