from enum import Enum
from dataclasses import dataclass

import moderngl as gl
from pyglm import glm

class RenderPass(Enum):
    ShadowPass = 0
    ForwardPass = 1

@dataclass
class RenderPassInfo:
    framebuffer: gl.Framebuffer
    viewportSize: glm.uvec2