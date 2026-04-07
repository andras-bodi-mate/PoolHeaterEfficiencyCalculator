from pyglm import glm

from light import Light

class SunLight(Light):
    def __init__(self):
        super().__init__()
        self.position: glm.vec2 = glm.vec2(0)
        self.sunlightTransmission: float = glm.float32(0)

    def initialize(self):
        return super().initialize()
    
    def release(self):
        return super().release()