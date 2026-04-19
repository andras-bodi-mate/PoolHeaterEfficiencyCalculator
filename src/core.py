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
    def toVec2(vec: qtc.QPoint | qtc.QPointF | glm.ivec2 | glm.vec2):
        if isinstance(vec, (qtc.QPoint, qtc.QPointF)):
            return glm.vec2(vec.x(), vec.y())
        else:
            return glm.vec2(vec)
    
    @staticmethod
    def toIVec2(vec: qtc.QPoint | qtc.QPointF | glm.ivec2 | glm.vec2):
        if isinstance(vec, (qtc.QPoint, qtc.QPointF)):
            return glm.ivec2(vec.x(), vec.y())
        else:
            return glm.ivec2(vec)
    
    @staticmethod
    def toQPoint(vec: qtc.QPoint | qtc.QPointF | glm.ivec2 | glm.vec2):
        if isinstance(vec, (qtc.QPoint, qtc.QPointF)):
            return qtc.QPoint(int(vec.x()), int(vec.y()))
        else:
            return qtc.QPoint(int(vec.x), int(vec.y))
    
    @staticmethod
    def toQPointF(vec: qtc.QPoint | qtc.QPointF | glm.ivec2 | glm.vec2):
        if isinstance(vec, (qtc.QPoint, qtc.QPointF)):
            return qtc.QPointF(int(vec.x()), int(vec.y()))
        else:
            return qtc.QPointF(int(vec.x), int(vec.y))