from kcGameLib import *

class Game2048Settings:
    DEFAULT_LAYERS = 1
    LAYER_SPACE = 30
    DEFAULT_LINE_BLOCKS = 2
    DEFAULT_BLOCK_WIDTH = 120
    HEADER_HEIGHT = 100
    BLOCK_PAD = 10
    SAVE_FILENAME = "SaveData.txt"
    BOARD_BG_COLOR = (187, 173, 160)
    BLOCK_BG_COLOR_DICT = {
        0: (205, 193, 180),
        2: (238, 228, 218),
        4: (237, 224, 200),
        8: (242, 177, 121),
        16: (245, 149, 99),
        32: (246, 124, 95),
        64: (246, 94, 59),
        128: (237, 207, 114),
        256: (237, 205, 98),
        512: (237, 200, 80),
        1024: (237, 197, 64),
        2048: (237, 194, 46),
        4096: (235, 185, 20),
        8192: (211, 166, 18),
        16384: (188, 148, 16),
        32768: (188, 148, 16),
        65536: (188, 148, 16),
        131072: (188, 148, 16),
        262144: (188, 148, 16),
        524288: (188, 148, 16),
        1048576: (188, 148, 16),
        2097152: (188, 148, 16)
    }

    BLOCK_TEXT_COLOR_DICT = {
        0: (205, 193, 180),
        2: (119, 110, 101),
        4: (119, 110, 101),
        8: (249, 246, 242),
        16: (249, 246, 242),
        32: (249, 246, 242),
        64: (249, 246, 242),
        128: (249, 246, 242),
        256: (249, 246, 242),
        512: (249, 246, 242),
        1024: (249, 246, 242),
        2048: (249, 246, 242),
        4096: (249, 246, 242),
        8192: (249, 246, 242),
        16384: (249, 246, 242),
        32768: (249, 246, 242),
        65536: (249, 246, 242),
        131072: (249, 246, 242),
        262144: (249, 246, 242),
        524288: (249, 246, 242),
        1048576: (249, 246, 242),
        2097152: (249, 246, 242)
    }

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

        self._layers = Game2048Settings.DEFAULT_LAYERS
        self._layer_space = Game2048Settings.LAYER_SPACE
        self._line_blocks = Game2048Settings.DEFAULT_LINE_BLOCKS
        self._block_width = Game2048Settings.DEFAULT_BLOCK_WIDTH
        self._header_height = Game2048Settings.HEADER_HEIGHT
        self._block_pad = Game2048Settings.BLOCK_PAD
        self._save_filename = Game2048Settings.SAVE_FILENAME = "SaveData.txt"

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
    def HeaderHeight(self):
        return self._header_height
    @HeaderHeight.setter
    def HeaderHeight(self, value ):
        self._header_height = max(value,100)

    @property
    def BlockPad(self):
        return self._block_pad
    @BlockPad.setter
    def BlockPad(self, value):
        self._block_pad = max(value ,10)

    @property
    def SaveFileName(self):
        return self._save_filename
    @SaveFileName.setter
    def SaveFileName(self, value):
        self._save_filename = value

    @property
    def BlockBgColorDict(self):
        kivy_block_bg_color_dict = dict()
        for key in Game2048Settings.BLOCK_BG_COLOR_DICT:
            kivy_block_bg_color_dict.update({key: toKivyColor(Game2048Settings.BLOCK_BG_COLOR_DICT[key])})
        return kivy_block_bg_color_dict

    @property
    def BlockTextColorDict(self):
        kivy_block_text_color_dict = dict()
        for key in Game2048Settings.BLOCK_TEXT_COLOR_DICT:
            kivy_block_text_color_dict.update({key: toKivyColor(Game2048Settings.BLOCK_TEXT_COLOR_DICT[key])})
        return kivy_block_text_color_dict

    @property
    def BoardBGColor(self):
        return toKivyColor(Game2048Settings.BOARD_BG_COLOR)