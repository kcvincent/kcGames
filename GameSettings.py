# -*- coding: utf-8 -*-
from kcGameLib import *
import json


class GameSettings:
    GAME_SQUARE_2 = 0
    GAME_CUBE_3 = 1
    GAME_FIBONCCI = 2

    DEFAULT_GAME_STYLE = GAME_SQUARE_2
    DEFAULT_LAYERS = 1
    DEFAULT_LINE_BLOCKS = 4

    LAYER_SPACE = 30
    DEFAULT_BLOCK_WIDTH = 100
    HEADER_HEIGHT = 100
    BLOCK_PAD = 10
    SAVE_FILENAME = "SaveData.txt"
    BOARD_BG_COLOR = (187, 173, 160)
    BASE_BLOCK_BG_COLOR_DICT = [
        (205, 193, 180),
        (238, 228, 218),
        (237, 224, 200),
        (242, 177, 121),
        (245, 149, 99),
        (246, 124, 95),
        (246, 94, 59),
        (237, 207, 114),
        (237, 205, 98),
        (237, 200, 80),
        (237, 197, 64),
        (237, 194, 46),
        (235, 185, 20),
        (211, 166, 18),
        (188, 148, 16),
        (188, 148, 16),
        (188, 148, 16),
        (188, 148, 16),
        (188, 148, 16),
        (188, 148, 16),
        (188, 148, 16),
        (188, 148, 16)
    ]
    BLOCK_BG_COLOR_DICT = dict()

    BASE_BLOCK_TEXT_COLOR_DICT = [
         (205, 193, 180),
         (119, 110, 101),
         (119, 110, 101),
         (249, 246, 242),
         (249, 246, 242),
         (249, 246, 242),
         (249, 246, 242),
         (249, 246, 242),
         (249, 246, 242),
         (249, 246, 242),
         (249, 246, 242),
         (249, 246, 242),
         (249, 246, 242),
         (249, 246, 242),
         (249, 246, 242),
         (249, 246, 242),
         (249, 246, 242),
         (249, 246, 242),
         (249, 246, 242),
         (249, 246, 242),
         (249, 246, 242),
         (249, 246, 242)
    ]
    BLOCK_TEXT_COLOR_DICT = dict()

    def __init__(self, game_style, layers, line_blocks):
        #(self.screenWidth, self.screenHeight) = (800, 600)
        #if sys.platform == 'linux2':
        #    import subprocess
        #    output = subprocess.Popen(
        #        'xrandr | grep "\*" | cut -d" " -f4',
        #        shell=True,
        #        stdout=subprocess.PIPE).communicate()[0]
        #    self.screenWidth = int(output.replace('\n', '').split('x')[0])
        #    self.screenHeight = int(output.replace('\n', '').split('x')[1])
        #elif sys.platform == 'win32':
        #    from win32api import GetSystemMetrics
        #    self.screenWidth = GetSystemMetrics(0)
        #    self.screenHeight = GetSystemMetrics(1)
        #elif sys.platform == 'darwin':
        #    from AppKit import NSScreen
        #    frame_size = NSScreen.mainScreen().frame().size
        #    self.screenWidth = frame_size.width
        #    self.screenHeight = frame_size.height

        key_list_len = len(GameSettings.BASE_BLOCK_BG_COLOR_DICT)
        self._key_list = []
        if game_style in (GameSettings.GAME_SQUARE_2, GameSettings.GAME_FIBONCCI):
            self._game_style = game_style
            self._line_blocks = max(line_blocks, 2)
            if self._game_style == GameSettings.GAME_SQUARE_2:
                self._key_list.extend(self.Square2List(key_list_len))
            elif self._game_style == GameSettings.GAME_FIBONCCI:
                self._key_list.extend(self.FibonacciList(key_list_len))
            else:
                raise Exception("Logical Error")
        elif game_style == GameSettings.GAME_CUBE_3:
            self._game_style = game_style
            self._line_blocks = max(line_blocks, 3)
            self._key_list.extend(self.Cube3List(key_list_len))
        else:
            self._game_style = GameSettings.DEFAULT_GAME_STYLE
            self._line_blocks = GameSettings.DEFAULT_LINE_BLOCKS
            self._key_list.extend(self.Square2List(key_list_len))

        if layers in range(1, 5):
            self._layers = layers
        else:
            self._layers = GameSettings.DEFAULT_LAYER

        self.initColorDict()

        self._layer_space = GameSettings.LAYER_SPACE
        self._block_width = GameSettings.DEFAULT_BLOCK_WIDTH
        self._block_height = GameSettings.DEFAULT_BLOCK_WIDTH
        self._header_height = GameSettings.HEADER_HEIGHT
        self._block_pad = GameSettings.BLOCK_PAD
        self._save_filename = GameSettings.SAVE_FILENAME
        self._tile_matrix = []
        self._total_points = 0



    def initColorDict(self):
        key_list_len = len(GameSettings.BASE_BLOCK_BG_COLOR_DICT)
        for i in range(key_list_len):
            k = self._key_list[i]
            GameSettings.BLOCK_BG_COLOR_DICT.update({k: GameSettings.BASE_BLOCK_BG_COLOR_DICT[i]})
            GameSettings.BLOCK_TEXT_COLOR_DICT.update({k: GameSettings.BASE_BLOCK_TEXT_COLOR_DICT[i]})

    def Square2List(self, length=21):
        lst = [0, 2]
        for i in range(1, length-1):
            lst.append(lst[i] * 2)
        return lst

    def Cube3List(self, length=21):
        lst = [0, 3]
        for i in range(1, length-1):
            lst.append(lst[i] * 3)
        return lst

    def FibonacciList(self, length=21):
        lst = [0, 2, 3]
        for i in range(2, length-1):
            lst.append(lst[i - 1] + lst[i])
        return lst

    def LoadFromFile(self):
        with open(self._save_filename, "r") as f:
            json_data = f.readline()
        gsd = json.loads(json_data)
        self._game_style = gsd['_game_style']
        self._key_list = gsd['_key_list']

        self._layers = gsd['_layers']
        self._layer_space = gsd['_layer_space']

        self._line_blocks = gsd['_line_blocks']
        self._block_width = gsd['_block_width']
        self._block_height = gsd['_block_height']
        self._block_pad = gsd['_block_pad']

        self._total_points = gsd['_total_points']
        self._tile_matrix = gsd['_tile_matrix']

        self._header_height = gsd['_header_height']
        self.initColorDict()

    def SaveToFile(self, tile_matrix):
        self._tile_matrix = tile_matrix
        with open(self._save_filename, 'w') as f:
            f.write(json.dumps(self.__dict__))

    @property
    def GameStyle(self):
        return self._game_style

    @property
    def KeyList(self):
        return self._key_list

    @property
    def Layers(self):
        return self._layers

    @Layers.setter
    def Layers(self, value):
        self._layers = max(value, 1)

    @property
    def LayerSpace(self):
        return self._layer_space

    @LayerSpace.setter
    def LayerSpace(self, value):
        self._layer_space = max(value, 10)

    @property
    def LineBlocks(self):
        return self._line_blocks

    @LineBlocks.setter
    def LineBlocks(self, value):
        if self._game_style == GameSettings.GAME_CUBE_3:
            self._line_blocks = max(value, 3)
        else:
            self._line_blocks = max(value, 2)

    @property
    def BlockWidth(self):
        return self._block_width

    @BlockWidth.setter
    def BlockWidth(self, value):
        self._block_width = max(value, 80)

    @property
    def BlockHeight(self):
        return self._block_height

    @BlockHeight.setter
    def BlockHeight(self, value):
        self._block_height = max(value, 80)

    @property
    def HeaderHeight(self):
        return self._header_height

    @HeaderHeight.setter
    def HeaderHeight(self, value):
        self._header_height = max(value, 100)

    @property
    def BlockPad(self):
        return self._block_pad

    @BlockPad.setter
    def BlockPad(self, value):
        self._block_pad = max(value, 10)

    @property
    def SaveFileName(self):
        return self._save_filename

    @SaveFileName.setter
    def SaveFileName(self, value):
        self._save_filename = value

    @property
    def BlockBgColorDict(self):
        new_dict = dict()
        for key in GameSettings.BLOCK_BG_COLOR_DICT:
            new_dict.update({key: toKivyColor(GameSettings.BLOCK_BG_COLOR_DICT[key])})
        return new_dict

    @property
    def BlockTextColorDict(self):
        new_dict = dict()
        for key in GameSettings.BLOCK_TEXT_COLOR_DICT:
            new_dict.update({key: toKivyColor(GameSettings.BLOCK_TEXT_COLOR_DICT[key])})
        return new_dict

    @property
    def BoardBGColor(self):
        return toKivyColor(GameSettings.BOARD_BG_COLOR)

    @property
    def TileMatrix(self):
        return self._tile_matrix

    @property
    def TotalPoints(self):
        return self._total_points
