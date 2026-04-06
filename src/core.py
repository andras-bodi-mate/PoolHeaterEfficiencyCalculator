from pathlib import Path

from PyQt6 import QtCore as qtc
from pyglm import glm

class Core:
    projectDir = Path(__file__).resolve().parent.parent

    @staticmethod
    def getPath(path: str | Path):
        if isinstance(path, Path) and path.exists():
            return path
        else:
            return Core.projectDir / path
        
    @staticmethod
    def toVec2(qPoint: qtc.QPoint | qtc.QPointF):
        return glm.vec2(qPoint.x(), qPoint.y())
    
    @staticmethod
    def toIVec2(qPoint: qtc.QPoint | qtc.QPointF):
        return glm.ivec2(int(qPoint.x()), int(qPoint.y()))
    
    @staticmethod
    def toQPoint(vec2: glm.vec2 | glm.ivec2):
        return qtc.QPoint(int(vec2.x), int(vec2.y))
    
    @staticmethod
    def toQPointF(vec2: glm.vec2 | glm.ivec2):
        return qtc.QPointF(vec2.x, vec2.y)