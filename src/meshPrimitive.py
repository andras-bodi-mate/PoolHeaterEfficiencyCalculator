import numpy as np
from numpy.typing import NDArray
import moderngl as gl

from material import Material
from renderPass import RenderPass

class MeshPrimitive:
    def __init__(self, vertices: NDArray[np.float32], normals: NDArray[np.float32],
                 uvs: NDArray[np.float32], indices: NDArray[np.uint32], materials: dict[RenderPass, Material]):
        self.vertices = vertices
        self.normals = normals
        self.uvs = uvs
        self.indices = indices
        self.materials = materials

        self.glContext: gl.Context = None
        self.vertexBuffer: gl.Buffer = None
        self.normalBuffer: gl.Buffer = None
        self.uvBuffer: gl.Buffer = None
        self.indexBuffer: gl.Buffer = None
        self.vertexArrays: dict[RenderPass, gl.VertexArray] = None

    def initialize(self):
        self.glContext = gl.get_context()
        self.vertexBuffer = self.glContext.buffer(self.vertices.tobytes())
        self.normalBuffer = self.glContext.buffer(self.normals.tobytes())
        self.uvBuffer = self.glContext.buffer(self.uvs.tobytes())
        self.indexBuffer = self.glContext.buffer(self.indices.tobytes())

        for material in self.materials.values():
            material.initialize()

        self.vertexArrays = {
            RenderPass.ForwardPass: self.glContext.vertex_array(
                self.materials[RenderPass.ForwardPass].program,
                [
                    (self.vertexBuffer, "3f", "in_position"),
                    (self.normalBuffer, "3f", "in_normal")
                ],
                index_buffer = self.indexBuffer
            ),
            RenderPass.ShadowPass: self.glContext.vertex_array(
                self.materials[RenderPass.ShadowPass].program,
                [
                    (self.vertexBuffer, "3f", "in_position")
                ],
                index_buffer = self.indexBuffer
            )
        }

    def render(self, renderPass: RenderPass):
        self.materials[renderPass].use()
        self.vertexArrays[renderPass].render()

    def release(self):
        for material in self.materials.values():
            material.release()
        for vertexArray in self.vertexArrays.values():
            vertexArray.release()

        self.indexBuffer.release()
        self.uvBuffer.release()
        self.normalBuffer.release()
        self.vertexBuffer.release()