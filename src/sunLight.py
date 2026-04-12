from pyglm import glm
import moderngl as gl

from light import Light

class SunLight(Light):
    def __init__(self):
        super().__init__()
        self.position: glm.vec2 = glm.vec2(0)
        self.sunlightTransmission: float = glm.float32(0)
        self.framebufferResolution = 2048
        self.framebuffer: gl.Framebuffer = None
        self.shadowMap: gl.Texture = None

    def initialize(self):
        super().initialize()
        self.shadowMap = self.glContext.depth_texture((self.framebufferResolution, self.framebufferResolution))
        self.framebuffer = self.glContext.framebuffer(depth_attachment = self.shadowMap)

    def release(self):
        super().release()
        self.framebuffer.release()
        self.shadowMap.release()