from pathlib import Path

from object import Object
from gltfLoader import GltfLoader

class SolarCollector(Object):
    def __init__(self, modelPath: Path):
        loaded = GltfLoader.loadFirstObject(modelPath)
        super().__init__(loaded.mesh, loaded.transform, loaded.children, loaded.name)