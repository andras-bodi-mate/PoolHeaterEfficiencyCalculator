from pathlib import Path
from urllib.parse import unquote

from pygltflib import GLTF2, Scene as GltfScene, Node as GltfNode, Mesh as GltfMesh, Material as GltfMaterial, Texture as GltfTexture, Image as GltfImage, Sampler as GltfSampler, BufferView as GltfBufferView, Accessor as GltfAccessor, Primitive as GltfPrimitive
import numpy as np
import moderngl as gl
from pyglm import glm

from core import Core
from transform import Transform
from meshPrimitive import MeshPrimitive
from mesh import Mesh
from material import Material
from object import Object
from renderPass import RenderPass

class GltfLoader:
    magnificationFilterMapping = {
        9728: gl.NEAREST,
        9729: gl.LINEAR
    }

    minificationFilterMapping = {
        9728: gl.NEAREST,
        9729: gl.LINEAR,
        9984: gl.NEAREST_MIPMAP_NEAREST,
        9985: gl.LINEAR_MIPMAP_NEAREST,
        9986: gl.NEAREST_MIPMAP_LINEAR,
        9987: gl.LINEAR_MIPMAP_LINEAR
    }

    repeatModeMapping = {
        33071: False,
        33648: True,
        10497: True
    }

    componentTypeMapping = {
        5120: np.int8,
        5121: np.uint8,
        5122: np.int16,
        5123: np.uint16,
        5125: np.uint32,
        5126: np.float32
    }

    numElementsMapping = {
        "SCALAR": 1,
        "VEC2": 2,
        "VEC3": 3,
        "VEC4": 4,
        "MAT2": 4,
        "MAT3": 9,
        "MAT4": 16
    }

    @staticmethod
    def getPathFromUri(uri: str):
        return Path(unquote(uri))
    
    @staticmethod
    def readBuffer(buffer: memoryview, bufferView: GltfBufferView, accessor: GltfAccessor):
        componentDataType = GltfLoader.componentTypeMapping[accessor.componentType]
        elementSize = np.dtype(componentDataType).itemsize * GltfLoader.numElementsMapping[accessor.type]

        viewedBuffer = buffer[bufferView.byteOffset : (bufferView.byteOffset + bufferView.byteLength)]

        if bufferView.byteStride and bufferView.byteStride != elementSize:
            viewedBuffer = buffer[bufferView.byteOffset : (bufferView.byteOffset + bufferView.byteLength)]
            viewedArray = np.frombuffer(viewedBuffer, dtype = np.uint8)

            numElements = (bufferView.byteLength - elementSize) // bufferView.byteStride + 1
            if numElements <= 0:
                raise ValueError("Cannot fit even one element within the buffer given the stride, element size and buffer length")

            stridedArray = np.lib.stride_tricks.as_strided(
                viewedArray,
                shape = (numElements, elementSize),
                strides = (bufferView.byteStride, 1),
                writeable = False
            )

            viewedBuffer = stridedArray.reshape(-1).tobytes()

        if accessor.byteOffset is not None:
            byteLength = elementSize * accessor.count
            return viewedBuffer[accessor.byteOffset : (accessor.byteOffset + byteLength)]
        else:
            return viewedBuffer
        
    @staticmethod
    def createArrayFromBytes(buffer: bytes, accessor: GltfAccessor):
        return np.frombuffer(buffer, dtype = GltfLoader.componentTypeMapping[accessor.componentType])
    
    @staticmethod
    def loadFirstObject(path: Path):
        gltfLoader = GltfLoader(path)
        return gltfLoader.loadRootObjects()[0]

    def __init__(self, path: Path):
        self.gltf = GLTF2().load(path)
        self.gltfDir = path.parent

        with open(self.gltfDir / self.getPathFromUri(self.gltf.buffers[0].uri), "rb") as bufferFile:
            self.buffer = memoryview(bufferFile.read())

        self.mainGltfScene: GltfScene = self.gltf.scenes[self.gltf.scene]

        self.defaultForwardPassMaterial = Material(
            vertexShaderPath = Core.getPath("shaders/forwardPassVertexShader.glsl"),
            fragmentShaderPath = Core.getPath("shaders/forwardPassFragmentShader.glsl")
        )
        self.defaultShadowPassMaterial = Material(
            vertexShaderPath = Core.getPath("shaders/shadowPassVertexShader.glsl"),
            fragmentShaderPath = Core.getPath("shaders/shadowPassFragmentShader.glsl")
        )

    def loadPrimitive(self, gltfPrimitive: GltfPrimitive):
        positionAccessor: GltfAccessor = self.gltf.accessors[gltfPrimitive.attributes.POSITION]
        normalAccessor: GltfAccessor = self.gltf.accessors[gltfPrimitive.attributes.NORMAL]
        uvAccessor: GltfAccessor = self.gltf.accessors[gltfPrimitive.attributes.TEXCOORD_0]
        #tangentAccessor: GltfAccessor = self.gltf.accessors[gltfPrimitive.attributes.TANGENT]
        indexAccessor: GltfAccessor = self.gltf.accessors[gltfPrimitive.indices]

        positionBufferView: GltfBufferView = self.gltf.bufferViews[positionAccessor.bufferView]
        normalBufferView: GltfBufferView = self.gltf.bufferViews[normalAccessor.bufferView]
        uvBufferView: GltfBufferView = self.gltf.bufferViews[uvAccessor.bufferView]
        #tangentBufferView: GltfBufferView = self.gltf.bufferViews[tangentAccessor.bufferView]
        indexBufferView: GltfBufferView = self.gltf.bufferViews[indexAccessor.bufferView]

        vertexDataBytes = GltfLoader.readBuffer(self.buffer, positionBufferView, positionAccessor)
        normalDataBytes = GltfLoader.readBuffer(self.buffer, normalBufferView, normalAccessor)
        uvDataBytes = GltfLoader.readBuffer(self.buffer, uvBufferView, uvAccessor)
        #tangentDataBytes = GltfLoader.readBuffer(self.buffer, tangentBufferView, tangentAccessor)
        indexDataBytes = GltfLoader.readBuffer(self.buffer, indexBufferView, indexAccessor)

        vertices = np.asarray(GltfLoader.createArrayFromBytes(vertexDataBytes, positionAccessor), dtype = np.float32)
        normals = np.asarray(GltfLoader.createArrayFromBytes(normalDataBytes, normalAccessor), dtype = np.float32)
        uvs = np.asarray(GltfLoader.createArrayFromBytes(uvDataBytes, uvAccessor), dtype = np.float32)
        #tangents = np.asarray(GltfLoader.createArrayFromBytes(tangentDataBytes, tangentAccessor), dtype = np.float32)
        indices = np.asarray(GltfLoader.createArrayFromBytes(indexDataBytes, indexAccessor), dtype = np.uint32)

        # material = self.materials[gltfPrimitive.material] if gltfPrimitive.material else self.defaultMaterial
        materials = {
            RenderPass.ForwardPass: self.defaultForwardPassMaterial,
            RenderPass.ShadowPass: self.defaultShadowPassMaterial
        }

        return MeshPrimitive(vertices, normals, uvs, indices, materials)

    def loadMesh(self, gltfMesh: GltfMesh):
        primitives = [self.loadPrimitive(primitive) for primitive in gltfMesh.primitives]
        return Mesh(primitives)
    
    def loadNode(self, gltfNode: GltfNode):
        mesh = self.loadMesh(self.gltf.meshes[gltfNode.mesh])
        transform = Transform(
            glm.vec3(*gltfNode.translation) if gltfNode.translation else glm.vec3(0),
            glm.quat(gltfNode.rotation[3], gltfNode.rotation[0], gltfNode.rotation[1], gltfNode.rotation[2]) if gltfNode.rotation else glm.quat(),
            glm.vec3(*gltfNode.scale) if gltfNode.scale else glm.vec3(1)
        )
        children = [self.loadNode(child) for childIndex in gltfNode.children if (child := self.gltf.nodes[childIndex]).mesh is not None] if gltfNode.children else None

        return Object(mesh, transform, children, gltfNode.name)

    def loadRootObjects(self):
        return [self.loadNode(node) for rootNodeIndex in self.mainGltfScene.nodes if (node := self.gltf.nodes[rootNodeIndex]).mesh is not None]