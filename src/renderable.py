from abc import ABC, abstractmethod

import moderngl as gl

class Renderable(ABC):
    def __init__(self):
        super().__init__()
        self.glContext: gl.Context = None
    
    @abstractmethod
    def initialize(self):
        self.glContext = gl.get_context()

    @abstractmethod
    def render(self):
        pass

    @abstractmethod
    def release(self):
        pass