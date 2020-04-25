from datetime import datetime
import json


class GameSaveData:
    @property
    def Layers(self):
        return self._layers

    @Layers.setter
    def Layers(self, value):
        self._layers = value

    @property
    def LineBlocks(self):
        return self._line_blocks

    @LineBlocks.setter
    def LineBlocks(self, value):
        self._line_blocks = value

    @property
    def TotalPoints(self):
        return self._total_points

    @TotalPoints.setter
    def TotalPoints(self, value):
        self._total_points = value

    @property
    def TileMatrix(self):
        return self._tile_matrix

    @TileMatrix.setter
    def TileMatrix(self, value):
        self._tile_matrix = value

    def __init__(self, layers=None, line_blocks=None, total_points=None, matrix=None):
        self._save_datetime = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self._layers = layers
        self._line_blocks = line_blocks
        self._total_points = total_points
        self._tile_matrix = matrix

    def LoadFromFile(self, filename):
        with open(filename, "r") as f:
            jsondata = f.readline()
        gsd = json.loads(jsondata)
        self._layers = gsd['_layers']
        self._line_blocks = gsd['_line_blocks']
        self._total_points = gsd['_total_points']
        self._tile_matrix = gsd['_tile_matrix']

    def SaveToFile(self, filename):
        with open(filename, 'w') as f:
            f.write(json.dumps(self.__dict__))