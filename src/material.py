from pathlib import Path
from dataclasses import dataclass, field

import moderngl as gl

from core import Core
from graphicsResource import GraphicsResource

@dataclass(frozen = True)
class ShaderProgramIdentifier:
    vertexShaderPath: Path = field(hash = True)
    fragmentShaderPath: Path | None = field(default = None, hash = True)
    capturedVaryings: tuple[str] = field(default = (), hash = True)

class Material(GraphicsResource):
    materials: list["Material"] = []
    shaderSourceCache: dict[Path, str] = {}
    shaderProgramCache: dict[ShaderProgramIdentifier, gl.Program] = {}
    shaderReferences: dict[ShaderProgramIdentifier, int] = {}

    @staticmethod
    def invalidateShaderCaches():
        Material.shaderSourceCache.clear()
        Material.shaderProgramCache.clear()

    @staticmethod
    def setUniformOnMaterials(uniformName: str, value):
        for material in Material.materials:
            uniform = material.program.get(uniformName, None)
            if uniform is not None:
                uniform.write(value)

    @staticmethod
    def readShaderSource(path: Path, isBeingIncluded = False):
        if path in Material.shaderSourceCache:
            return Material.shaderSourceCache[path]
    
        lines = path.read_text().splitlines(True)
        if isBeingIncluded and lines[0].startswith("#version"):
            lines = lines[1:]
        processedSource = ""
        for line in lines:
            if line.startswith("#include"):
                processedSource += Material.readShaderSource(path.parent / line[9:].strip())
            else:
                processedSource += line
        Material.shaderSourceCache[path] = processedSource
        return processedSource

    def __init__(self, vertexShaderPath: Path, fragmentShaderPath: Path = None, capturedVaryings: tuple[str] = ()):
        super().__init__()
        self.vertexShaderPath = vertexShaderPath
        self.fragmentShaderPath = fragmentShaderPath
        self.capturedVaryings = capturedVaryings
        self.shaderProgramIdentifier = ShaderProgramIdentifier(
            self.vertexShaderPath,
            self.fragmentShaderPath,
            self.capturedVaryings
        )
        if self.shaderProgramIdentifier in Material.shaderProgramCache:
            self.isProgramCached = True
        else:
            self.isProgramCached = False
            self.vertexShaderSource = Material.readShaderSource(self.vertexShaderPath)
            self.fragmentShaderSource = Material.readShaderSource(self.fragmentShaderPath) if self.fragmentShaderPath else None
            Material.shaderProgramCache[self.shaderProgramIdentifier] = None

        Material.materials.append(self)
        
    def initialize(self):
        super().initialize()
        cachedProgram = Material.shaderProgramCache.get(self.shaderProgramIdentifier)
        if cachedProgram is not None:
            self.program = cachedProgram
        else:
            self.program = self.glContext.program(
                vertex_shader = self.vertexShaderSource,
                fragment_shader = self.fragmentShaderSource,
                varyings = self.capturedVaryings,
                varyings_capture_mode = "separate"
            )
            Material.shaderProgramCache[self.shaderProgramIdentifier] = self.program

        if self.shaderProgramIdentifier in Material.shaderReferences:
            Material.shaderReferences[self.shaderProgramIdentifier] += 1
        else:
            Material.shaderReferences[self.shaderProgramIdentifier] = 1

    def setUniform(self, uniformName, value):
        self.program[uniformName].write(value)

    def use(self):
        pass

    def release(self):
        super().release()
        Material.shaderReferences[self.shaderProgramIdentifier] -= 1

        if Material.shaderReferences[self.shaderProgramIdentifier] == 0:
            Material.shaderReferences.pop(self.shaderProgramIdentifier)
            Material.shaderProgramCache.pop(self.shaderProgramIdentifier)
            self.program.release()