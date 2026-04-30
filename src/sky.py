from pathlib import Path

from object import Object
from gltfLoader import GltfLoader

class Sky(Object):
    def __init__(self, path: Path):
        object = GltfLoader.loadFirstObject(path)
        super().__init__(object.mesh, object.transform, object.children, object.name)