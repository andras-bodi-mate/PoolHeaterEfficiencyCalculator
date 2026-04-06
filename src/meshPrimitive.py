import numpy as np
from numpy.typing import NDArray
import moderngl as gl

from material import Material

class MeshPrimitive:
    def __init__(self, vertices: NDArray[np.float32], normals: NDArray[np.float32],
                 uvs: NDArray[np.float32], indices: NDArray[np.uint32], material: Material):
        self.vertices = vertices
        self.normals = normals
        self.uvs = uvs
        self.indices = indices
        self.material = material

        self.glContext: gl.Context = None
        self.vertexBuffer: gl.Buffer = None
        self.normalBuffer: gl.Buffer = None
        self.uvBuffer: gl.Buffer = None
        self.indexBuffer: gl.Buffer = None
        self.vertexArray: gl.VertexArray = None

    def initialize(self):
        self.glContext = gl.get_context()
        self.vertexBuffer = self.glContext.buffer(self.vertices.tobytes())
        self.normalBuffer = self.glContext.buffer(self.normals.tobytes())
        self.uvBuffer = self.glContext.buffer(self.uvs.tobytes())
        self.indexBuffer = self.glContext.buffer(self.indices.tobytes())
        self.material.initialize()
        self.vertexArray = self.glContext.vertex_array(
            self.material.program, [
                (self.vertexBuffer, "3f", "in_position"),
                (self.normalBuffer, "3f", "in_normal")
            ],
            index_buffer = self.indexBuffer
        )

    def render(self):
        self.material.use()
        self.vertexArray.render()

    def release(self):
        self.vertexArray.release()
        self.indexBuffer.release()
        self.uvBuffer.release()
        self.normalBuffer.release()
        self.vertexBuffer.release()