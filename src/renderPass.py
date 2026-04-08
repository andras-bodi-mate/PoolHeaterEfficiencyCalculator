from enum import Enum
from dataclasses import dataclass, field

import moderngl as gl
from pyglm import glm

class RenderPass(Enum):
    ShadowPass = 0
    ForwardPass = 1

@dataclass
class RenderPassInfo:
    framebuffer: gl.Framebuffer
    viewportSize: glm.uvec2
    enableShadowPass: bool = field(default = True)
    enableForwardPass: bool = field(default = True)