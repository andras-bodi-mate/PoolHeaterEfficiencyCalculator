from graphicsResource import GraphicsResource

class Light(GraphicsResource):
    def __init__(self):
        super().__init__()
        self.framebufferResolution: int

    def initialize(self):
        return super().initialize()
    
    def release(self):
        return super().release()