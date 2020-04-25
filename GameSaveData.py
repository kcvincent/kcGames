from datetime import datetime


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

    def __init__(self, layers, line_blocks, total_points, matrix):
        self._save_datetime = datetime.now()
        self._layers = layers
        self._line_blocks = line_blocks
        self._total_points = total_points
        self._tile_matrix = matrix

