# -*- coding: utf-8 -*-
from kcGameLib import *
import json
from datetime import datetime


class GameSettings:
    DEFAULT_GAME_STYLE = 2
    DEFAULT_LAYERS = 1
    DEFAULT_LINE_BLOCKS = 4

    LAYER_SPACE = 30
    DEFAULT_BLOCK_WIDTH = 100
    HEADER_HEIGHT = 100
    BLOCK_PAD = 10
    SAVE_FILENAME = "SaveData.txt"
    BOARD_BG_COLOR = (187, 173, 160)
    #BLOCK_BG_COLOR_DICT = {
    #    0: (205, 193, 180),
    #    2: (238, 228, 218),
    #    4: (237, 224, 200),
    #    8: (242, 177, 121),
    #    16: (245, 149, 99),
    #    32: (246, 124, 95),
    #    64: (246, 94, 59),
    #    128: (237, 207, 114),
    #    256: (237, 205, 98),
    #    512: (237, 200, 80),
    #    1024: (237, 197, 64),
    #    2048: (237, 194, 46),
    #    4096: (235, 185, 20),
    #    8192: (211, 166, 18),
    #    16384: (188, 148, 16),
    #    32768: (188, 148, 16),
    #    65536: (188, 148, 16),
    #    131072: (188, 148, 16),
    #    262144: (188, 148, 16),
    #    524288: (188, 148, 16),
    #    1048576: (188, 148, 16),
    #    2097152: (188, 148, 16)
    #}
    #
    #BLOCK_TEXT_COLOR_DICT = {
    #    0: (205, 193, 180),
    #    2: (119, 110, 101),
    #    4: (119, 110, 101),
    #    8: (249, 246, 242),
    #    16: (249, 246, 242),
    #    32: (249, 246, 242),
    #    64: (249, 246, 242),
    #    128: (249, 246, 242),
    #    256: (249, 246, 242),
    #    512: (249, 246, 242),
    #    1024: (249, 246, 242),
    #    2048: (249, 246, 242),
    #    4096: (249, 246, 242),
    #    8192: (249, 246, 242),
    #    16384: (249, 246, 242),
    #    32768: (249, 246, 242),
    #    65536: (249, 246, 242),
    #    131072: (249, 246, 242),
    #    262144: (249, 246, 242),
    #    524288: (249, 246, 242),
    #    1048576: (249, 246, 242),
    #    2097152: (249, 246, 242)
    #}
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

    def __init__(self):
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
        self._game_style = GameSettings.DEFAULT_GAME_STYLE
        self._key_list = []
        self.initColorDict()

        self._layers = GameSettings.DEFAULT_LAYERS
        self._layer_space = GameSettings.LAYER_SPACE
        self._line_blocks = GameSettings.DEFAULT_LINE_BLOCKS
        self._block_width = GameSettings.DEFAULT_BLOCK_WIDTH
        self._block_height = GameSettings.DEFAULT_BLOCK_WIDTH
        self._header_height = GameSettings.HEADER_HEIGHT
        self._block_pad = GameSettings.BLOCK_PAD
        self._save_filename = GameSettings.SAVE_FILENAME = "SaveData.txt"
        self._tile_matrix = []
        self._total_points = 0

    def initColorDict(self):
        keylistlen = len(GameSettings.BASE_BLOCK_BG_COLOR_DICT)
        if self._game_style == 0:
            self._key_list.extend(self.Power2List(keylistlen))
        elif self._game_style == 1:
            self._key_list.extend(self.Power3List(keylistlen))
        elif self._game_style == 2:
            self._key_list.extend(self.FibonacciList(keylistlen))
        else:
            self._key_list.extend(self.Power2List(keylistlen))
        for i in range(keylistlen):
            k = self._key_list[i]
            print (f" {k} : {GameSettings.BASE_BLOCK_BG_COLOR_DICT[i]} , {GameSettings.BASE_BLOCK_TEXT_COLOR_DICT[i]} ")
            GameSettings.BLOCK_BG_COLOR_DICT.update({ k : GameSettings.BASE_BLOCK_BG_COLOR_DICT[i]})
            GameSettings.BLOCK_TEXT_COLOR_DICT.update({ k : GameSettings.BASE_BLOCK_TEXT_COLOR_DICT[i]})

    def Power2List(self, length =21):
        lst = [0, 2]
        for i in range(1, length-1):
            lst.append(lst[i] * 2)
        return lst

    def Power3List(self, length=21):
        lst = [0, 3]
        for i in range(1, length-1):
            lst.append(lst[i] * 3)
        return lst

    def FibonacciList(self, length=21 ):
        lst = [0, 2, 3]
        for i in range(2, length-1):
            lst.append(lst[i - 1] + lst[i])
        return lst

    def LoadFromFile(self):
        with open(self._save_filename, "r") as f:
            jsondata = f.readline()
        gsd = json.loads(jsondata)
        self._game_style = gsd['_game_style']
        self._layers = gsd['_layers']
        self._layer_space = gsd['_layer_space']

        self._line_blocks = gsd['_line_blocks']
        self._block_width = gsd['_block_width']
        self._block_height = gsd['_block_height']
        self._block_pad = gsd['_block_pad']

        self._total_points = gsd['_total_points']
        self._tile_matrix = gsd['_tile_matrix']

        self._header_height = GameSettings.HEADER_HEIGHT

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
        kivy_block_bg_color_dict = dict()
        for key in GameSettings.BLOCK_BG_COLOR_DICT:
            kivy_block_bg_color_dict.update({key: toKivyColor(GameSettings.BLOCK_BG_COLOR_DICT[key])})
        return kivy_block_bg_color_dict

    @property
    def BlockTextColorDict(self):
        kivy_block_text_color_dict = dict()
        for key in GameSettings.BLOCK_TEXT_COLOR_DICT:
            kivy_block_text_color_dict.update({key: toKivyColor(GameSettings.BLOCK_TEXT_COLOR_DICT[key])})
        return kivy_block_text_color_dict

    @property
    def BoardBGColor(self):
        return toKivyColor(GameSettings.BOARD_BG_COLOR)

    @property
    def TileMatrix(self):
        return self._tile_matrix

    @property
    def TotalPoints(self):
        return self._total_points
