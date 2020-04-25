from operator import truediv
from kivy.logger import Logger
from kivy.core.window import Window
from kivy.uix.widget import Widget
from kivy.app import App
from kivy.graphics import Color,  Rectangle
from kivy.core.text import Label as CoreLabel
from random import *
import kivy.utils
from datetime import datetime
#import sys
from win32api import GetSystemMetrics

kivy.require("1.11.1")


def d1tod3(d1, b):
    b2 = b**2
    return d1//b2, (d1 % b2) // b, d1 % b


def d3tod1(d1, d2, d3, b):
    b2 = b**2
    return d1*b2 + d2*b + d3


def floor(n):
    return int(n - (n % 1))


def toKivyColor(rgb):
    b = tuple(map(truediv, rgb, (255.0, 255.0, 255.0)))
    return b


def isArrow(k):
    return k == 'up' or k == 'down' or k == 'left' or k == 'right'


def getRotations(k):
    if k == 'up':
        return 0
    elif k == 'down':
        return 2
    elif k == 'left':
        return 1
    elif k == 'right':
        return 3


class GameOverError(Exception):
    pass


class GBoard(Widget):
    """
     GBoard = GameBoard
    """
    DEFAULT_LAYERS = 3
    LAYER_SPACE = 30

    DEFAULT_LINE_BLOCKS = 3
    DEFAULT_BLOCK_WIDTH = 120
    BOARD_BG_COLOR = (187, 173, 160)
    HEADER_HEIGHT = 100
    BLOCK_PAD = 10
    SAVE_FILENAME = "SaveData.txt"
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
        0:     (205, 193, 180),
        2:     (119, 110, 101),
        4:     (119, 110, 101),
        8:     (249, 246, 242),
        16:     (249, 246, 242),
        32:     (249, 246, 242),
        64:     (249, 246, 242),
        128:     (249, 246, 242),
        256:     (249, 246, 242),
        512:     (249, 246, 242),
        1024:     (249, 246, 242),
        2048:     (249, 246, 242),
        4096:     (249, 246, 242),
        8192:     (249, 246, 242),
        16384:     (249, 246, 242),
        32768:     (249, 246, 242),
        65536:     (249, 246, 242),
        131072:     (249, 246, 242),
        262144:     (249, 246, 242),
        524288:     (249, 246, 242),
        1048576:     (249, 246, 242),
        2097152:     (249, 246, 242)
    }

    def __init__(self, **kwargs):
        super(GBoard, self).__init__(**kwargs)
        (self.screenWidth, self.screenHeight) = (800, 600)
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

        self.screenWidth = GetSystemMetrics(0)
        self.screenHeight = GetSystemMetrics(1)

        (self.frameWidth, self.frameHeight) = (0, 0)

        self._keyboard = Window.request_keyboard(self._keyboard_closed, self, 'text')
        if self._keyboard.widget:
            # If it exists, this widget is a VKeyboard object which you can use
            # to change the keyboard layout.
            pass
        self._keyboard.bind(on_key_down=self._on_keyboard_down)

        self.kivy_block_bg_color_dict = dict()
        for key in GBoard.BLOCK_BG_COLOR_DICT:
            self.kivy_block_bg_color_dict.update({key: toKivyColor(GBoard.BLOCK_BG_COLOR_DICT[key])})

        self.kivy_block_text_color_dict = dict()
        for key in GBoard.BLOCK_TEXT_COLOR_DICT:
            self.kivy_block_text_color_dict.update({key: toKivyColor(GBoard.BLOCK_TEXT_COLOR_DICT[key])})

        self.layers = max(GBoard.DEFAULT_LAYERS, 0)
        Logger.info(f"layers : {self.layers}")

        self.layerSpace = max(GBoard.LAYER_SPACE, 0)
        Logger.info(f"layerSpace : {self.layerSpace}")

        self.lineBlocks = max(GBoard.DEFAULT_LINE_BLOCKS, 3)
        Logger.info(f"lineBlocks : {self.lineBlocks}")

        self.boardBgColor = toKivyColor(GBoard.BOARD_BG_COLOR)
        Logger.info(f"boardBgColor : {self.boardBgColor}")

        self.totalBlocks = self.layers * self.lineBlocks * self.lineBlocks
        Logger.info(f"totalBlocks : {self.totalBlocks}")

        self.headerHeight = GBoard.HEADER_HEIGHT
        Logger.info(f"headerHeight : {self.headerHeight}")

        self.totalPoints = 0
        Logger.info(f"totalPoints : {self.totalPoints}")

        self.blockHeight = self.blockWidth = max(GBoard.DEFAULT_BLOCK_WIDTH, 80)
        Logger.info(f"blockWidth : {self.blockWidth}")
        Logger.info(f"blockHeight : {self.blockHeight}")

        self.blockPad = max(GBoard.BLOCK_PAD, 5)
        Logger.info(f"blockPad : {self.blockPad}")

        self.layerWidth = (self.blockWidth + self.blockPad) * self.lineBlocks
        Logger.info(f"layerWidth : {self.layerWidth}")
        self.layerHeight = (self.blockHeight + self.blockPad) * self.lineBlocks + self.blockPad
        Logger.info(f"layerHeight : {self.layerHeight}")

        self.resizeWindow()
        self.tileMatrix = self.initMatrix()
        Logger.info(f"tileMatrix : All Zeros")

        self.newBlock = (self.layers, self.lineBlocks, self.lineBlocks)
        Logger.info(f"newBlock : {self.newBlock}")
        self.undoMat = []
        self.msg = "New Game"
        self.gameOvered = False
        self.printMatrix()
        self.reset()

        Window.bind(on_resize=self.on_window_resize)

    def initMatrix(self):
        return [[[0 for i in range(self.lineBlocks)] for i in range(self.lineBlocks)] for i in range(self.layers)]

    def resizeWindow(self):
        self.layerWidth = (self.blockWidth + self.blockPad) * self.lineBlocks + self.blockPad
        self.layerHeight = (self.blockHeight + self.blockPad) * self.lineBlocks + self.blockPad

        Window.size = (self.frameWidth, self.frameHeight) \
            = (self.layerWidth * self.layers + (self.layers - 1) * self.layerSpace,
               self.layerHeight + GBoard.HEADER_HEIGHT)
        Logger.info(f"layerWidth : {self.layerWidth}")
        Logger.info(f"layerHeight : {self.layerHeight}")
        Logger.info(f"frameSize : ({self.frameWidth}, {self.frameHeight})")

    def DoAStep(self, rotations):
        for i in range(0, rotations):
            self.rotateMatrixClockwise()
        if self.canMove():
            self.moveTiles()
            self.mergeTiles()
            for j in range(0, (4 - rotations) % 4):
                self.rotateMatrixClockwise()
            self.placeRandomTile()
        else:
            for j in range(0, (4 - rotations) % 4):
                self.rotateMatrixClockwise()

    def DoMergeUpperLayer(self):
        if self.layers > 1:
            for ly in range(0, self.layers - 1):
                self.DoMergeTwoLayer(ly, ly + 1)

    def DoMergeTwoLayer(self, ly1, ly2):
        for i in range(0, self.lineBlocks):
            for j in range(0, self.lineBlocks):
                if self.tileMatrix[ly1][i][j] == self.tileMatrix[ly2][i][j]:
                    Logger.debug(f" Merge ({ly1},{i},{j}) {self.tileMatrix[ly1][i][j]} , ({ly2},{i},{j}) {self.tileMatrix[ly2][i][j]}=>  ({ly1},{i},{j}) {self.tileMatrix[ly1][i][j] + self.tileMatrix[ly2][i][j]}")
                    self.tileMatrix[ly1][i][j] += self.tileMatrix[ly2][i][j]
                    self.tileMatrix[ly2][i][j] = 0
                    self.addPoints(self.tileMatrix[ly1][i][j])
        self.placeRandomTile()

    def DoMergeLowerLayer(self):
        if self.layers > 1:
            for ly in range(self.layers - 1, 0, -1):
                self.DoMergeTwoLayer(ly, ly - 1)

    def rotateMatrixClockwise(self):
        for ly in range(0, self.layers):
            for i in range(0, int(self.lineBlocks / 2)):
                for k in range(i, self.lineBlocks - i - 1):
                    temp1 = self.tileMatrix[ly][i][k]
                    temp2 = self.tileMatrix[ly][self.lineBlocks - 1 - k][i]
                    temp3 = self.tileMatrix[ly][self.lineBlocks - 1 - i][self.lineBlocks - 1 - k]
                    temp4 = self.tileMatrix[ly][k][self.lineBlocks - 1 - i]

                    self.tileMatrix[ly][self.lineBlocks - 1 - k][i] = temp1
                    self.tileMatrix[ly][self.lineBlocks - 1 - i][self.lineBlocks - 1 - k] = temp2
                    self.tileMatrix[ly][k][self.lineBlocks - 1 - i] = temp3
                    self.tileMatrix[ly][i][k] = temp4

    def canMove(self):
        """
          因為用了旋轉,所以只要檢查一個方向
        :return:
        """
        for ly in range(0, self.layers):
            for i in range(0, self.lineBlocks):
                for j in range(1, self.lineBlocks):
                    if self.tileMatrix[ly][i][j - 1] == 0 and self.tileMatrix[ly][i][j] > 0:
                        return True
                    elif (self.tileMatrix[ly][i][j - 1] == self.tileMatrix[ly][i][j]) and self.tileMatrix[ly][i][j - 1] != 0:
                        return True
        return False

    def canLayerMove(self):
        """
          檢查上下層可否移動
        :return:
        """
        for ly in range(0, self.layers - 1):
            for i in range(0, self.lineBlocks):
                for j in range(0, self.lineBlocks):
                    if self.tileMatrix[ly][i][j] == 0 and self.tileMatrix[ly + 1][i][j] > 0:
                        #當前 層 為零, ly+1層不為零
                        return True
                    elif self.tileMatrix[ly][i][j] != 0 and (self.tileMatrix[ly][i][j] == self.tileMatrix[ly + 1][i][j]):
                        # 當前 層 不為零, 當前 層 = ly+1層
                        return True
                    elif self.tileMatrix[self.layers - 1 - ly][i][j] == 0 and self.tileMatrix[self.layers - 1 - ly - 1][i][j] > 0:
                        # 倒序 當前 層 為零, ly - 1層不為零
                        return True

    def moveTiles(self):
        for ly in range(0, self.layers):
            for i in range(0, self.lineBlocks):
                for j in range(0, self.lineBlocks - 1):
                    while self.tileMatrix[ly][i][j] == 0 and sum(self.tileMatrix[ly][i][j:]) > 0:
                        for k in range(j, self.lineBlocks - 1):
                            self.tileMatrix[ly][i][k] = self.tileMatrix[ly][i][k + 1]
                        self.tileMatrix[ly][i][self.lineBlocks - 1] = 0

    def mergeTiles(self):
        for ly in range(0, self.layers):
            for i in range(0, self.lineBlocks):
                for k in range(0, self.lineBlocks - 1):
                    if self.tileMatrix[ly][i][k] == self.tileMatrix[ly][i][k + 1] and self.tileMatrix[ly][i][k] != 0:
                        self.tileMatrix[ly][i][k] = self.tileMatrix[ly][i][k] * 2
                        self.tileMatrix[ly][i][k + 1] = 0
                        # this was not intailized so the k value was going out the range value
                        # so by this we ever we merge the files it assigns the present value to zero and
                        # merge the number with the ahead value
                        self.addPoints(self.tileMatrix[ly][i][k])
                        self.moveTiles()

    def addPoints(self, inc_points):
        self.totalPoints += inc_points

    def placeRandomTile(self):
        zeros = []
        for ly in range(0, self.layers):
            for i in range(0, self.lineBlocks):
                for j in range(0, self.lineBlocks):
                    if self.tileMatrix[ly][i][j] == 0:
                        zeros.append((ly, i, j))
        if len(zeros) == 0:
            self.saveGameState()
            raise GameOverError("Game Over ??")

        #while self.tileMatrix[self.floor(k / self.lineBlocks)][k % self.lineBlocks] != 0:
        #    k = self.generateRandomNo
        (a, b, c) = zeros[randint(0, len(zeros)-1)]

        #(a, b, c) = d1tod3(randint(0, self.totalBlocks-1), self.lineBlocks)
        #while self.tileMatrix[a][b][c] != 0:
        #    (a, b, c) = d1tod3(randint(0, self.totalBlocks-1), self.lineBlocks)

        new_val_array = [2, 2, 4]
        new_val = new_val_array[randint(0, len(new_val_array)-1)]
        self.tileMatrix[a][b][c] = new_val
        self.newBlock = (a, b, c)


    def checkIfCanGo(self):
        for i in range(0, self.totalBlocks):
            (a, b, c) = d1tod3(i, self.lineBlocks)
            if self.tileMatrix[a][b][c] == 0:
                return True
        for ly in range(0, self.layers):
            for i in range(0, self.lineBlocks):
                for j in range(0, self.lineBlocks - 1):
                    if self.tileMatrix[ly][i][j] == self.tileMatrix[ly][i][j + 1]:
                        return True
                    elif self.tileMatrix[ly][j][i] == self.tileMatrix[ly][j + 1][i]:
                        return True
        for ly in range(0, self.layers-1):
            for i in range(0, self.lineBlocks):
                for j in range(0, self.lineBlocks):
                    if self.tileMatrix[ly][i][j] == self.tileMatrix[ly+1][i][j]:
                        return True
        return False

    # This module return an matrix rather than we can call it an list
    def convertToLinearMatrix(self):
        mat = []
        for i in range(0, self.totalBlocks):
            (a, b, c) = d1tod3(i, self.lineBlocks)
            mat.append(self.tileMatrix[a][b][c])
        mat.append(self.totalPoints)
        return mat

    def addToUndo(self):
        self.undoMat.append(self.convertToLinearMatrix())

    def reset(self):
        self.totalPoints = 0
        self.tileMatrix = self.initMatrix()
        self.undoMat = []
        self.newBlock = (self.layers, self.lineBlocks, self.lineBlocks)
        self.gameOvered = False
        self.msg = "New Game"
        self.placeRandomTile()
        self.placeRandomTile()
        self.printMatrix()

    def saveGameState(self):
        f = open(GBoard.SAVE_FILENAME, "w")
        f.write(f"{self.layers}\n")
        f.write(f"{self.lineBlocks}\n")
        f.write(f"{self.totalPoints}\n")
        line1 = " "
        for ly in range(0, self.layers):
            for i in range(0, self.lineBlocks):
                for j in range(0, self.lineBlocks):
                    line1 += str(self.tileMatrix[ly][i][j]) + " "
        f.write(line1.strip()() + "\n")
        f.close()
        self.msg = f'Saved at {datetime.now().strftime("%Y/%m/%d, %H:%M:%S")}'
        self.printMatrix()

    def loadGameState(self):
        f = open(GBoard.SAVE_FILENAME, "r")
        self.layers = int(f.readline())
        self.lineBlocks = int(f.readline())
        self.totalPoints = int(f.readline())
        self.totalBlocks = self.layers * self.lineBlocks * self.lineBlocks
        mat = (f.readline()).split(' ', self.totalBlocks)
        for i in range(0, self.totalBlocks):
            (a, b, c) = d1tod3(i, self.lineBlocks)
            self.tileMatrix[a][b][c] = int(mat[i])
        f.close()
        self.resizeWindow()
        self.gameOvered = False
        self.msg = f'Loaded at {datetime.now().strftime("%Y/%m/%d, %H:%M:%S")}'
        self.printMatrix()

    def undo(self):
        if len(self.undoMat) > 0:
            mat = self.undoMat.pop()
            for i in range(0, self.lineBlocks ** 2):
                self.tileMatrix[self.floor(i / self.lineBlocks)][i % self.lineBlocks] = mat[i]
            self.totalPoints = mat[self.lineBlocks ** 2]
            self.msg = f'Undo at {datetime.now().strftime("%Y/%m/%d, %H:%M:%S")}'
            self.printMatrix()

    def on_window_resize(self, window, width, height):
        (self.frameWidth, self.frameHeight) = (width, height)
        self.printMatrix()

    def _keyboard_closed(self):
        print('My keyboard have been closed!')
        self._keyboard.unbind(on_key_down=self._on_keyboard_down)
        self._keyboard = None

    def _on_keyboard_down(self, keyboard, keycode, text, modifiers):
        #print('The key', keycode, 'have been pressed')
        #print(' - text is %r' % text)
        #print(' - modifiers are %r' % modifiers)
        #Keycode is composed of an integer + a string
        #If we hit escape, release the keyboard
        Logger.info(f"press {keycode} {text} {modifiers}")
        if keycode[1] == 'escape':
            keyboard.release()
        if self.gameOvered:
            if keycode[1] == 'r':
                self.reset()
        else:
            if self.checkIfCanGo():
                if isArrow(keycode[1]):
                    rotations = getRotations(keycode[1])
                    self.addToUndo()
                    self.DoAStep(rotations)
                    self.gameOvered = not self.checkIfCanGo()
                    self.printMatrix()
                elif keycode[1] == 'q':
                    self.addToUndo()
                    self.DoMergeUpperLayer()
                    self.gameOvered = not self.checkIfCanGo()
                    self.printMatrix()
                elif keycode[1] == 'e':
                    self.addToUndo()
                    self.DoMergeLowerLayer()
                    self.gameOvered = not self.checkIfCanGo()
                    self.printMatrix()
                elif keycode[1] == 's':
                    self.saveGameState()
                elif keycode[1] == 'l':
                    self.loadGameState()
                elif keycode[1] == 'u':
                    self.undo()
            else:
                self.gameOvered = True
                self.msg = f"Game Over!!Press R to New a Game"
                self.printMatrix()
        # Return True to accept the key. Otherwise, it will be used by
        # the system.
        return True

    def toKivyXY(self, x, y, offset=0):
        """
        :param offset:
        :param x: 0 as Left
        :param y: 0 as Top
        :return: kivy y as Bottom
        """
        return x, self.frameHeight - y - offset

    def printMatrix(self):
        self.canvas.clear()
        # Draw BackGround
        self.canvas.add(Color(rgb=self.boardBgColor))
        self.canvas.add(Rectangle(pos=(0, 0), size=(self.frameWidth, self.frameHeight)))
        # Draw Banner Zone /Score
        self.canvas.add(Color(rgb=(1., 1., 1.)))
        label = CoreLabel(text=f"Score : {self.totalPoints} ", font_size=20)
        label.refresh()
        text = label.texture
        self.canvas.add(Rectangle(size=text.size,
                                  pos=self.toKivyXY(GBoard.BLOCK_PAD, text.size[1], text.size[1]),
                                  texture=text))
        # Draw Banner Zone /Message
        if len(self.msg) > 0:
            label = CoreLabel(text=self.msg, font_size=20)
            label.refresh()
            text = label.texture
            self.canvas.add(Rectangle(size=text.size,
                                      pos=self.toKivyXY(GBoard.BLOCK_PAD, text.size[1] * 2, text.size[1]),
                                      texture=text))

        for ly in range(0, self.layers):
            for i in range(0, self.lineBlocks):
                for j in range(0, self.lineBlocks):
                    # Draw Block outline
                    #print("Cell Info:")
                    #print(self.tileMatrix[ly][i][j])
                    #print(self.kivy_block_bg_color_dict[self.tileMatrix[ly][i][j]])
                    self.canvas.add(Color(rgb=self.kivy_block_bg_color_dict[self.tileMatrix[ly][i][j]]))
                    block_pos = self.toKivyXY(ly * (self.layerWidth + self.LAYER_SPACE) +
                                              i * (self.blockWidth + GBoard.BLOCK_PAD) + GBoard.BLOCK_PAD,
                                              GBoard.HEADER_HEIGHT + j * (self.blockWidth + GBoard.BLOCK_PAD),
                                              self.blockWidth + GBoard.BLOCK_PAD)
                    #print(f" (ly,i,j) ({ly},{i},{j})  : {block_pos}")
                    self.canvas.add(Rectangle(pos=block_pos,
                                              size=(self.blockWidth, self.blockWidth)))
                    # Draw Block Text
                    if self.tileMatrix[ly][i][j] != 0:
                        if self.newBlock == (ly, i, j):
                            self.canvas.add(Color(rgb=(0., 0., 1.)))
                        else:
                            self.canvas.add(Color(rgb=self.kivy_block_text_color_dict[self.tileMatrix[ly][i][j]]))
                        label = CoreLabel(text=f"{self.tileMatrix[ly][i][j]}", font_size=48)
                        label.refresh()
                        text = label.texture
                        text_pos = self.toKivyXY(ly * (self.layerWidth + self.LAYER_SPACE) +
                                                 i * (self.blockWidth + GBoard.BLOCK_PAD) + GBoard.BLOCK_PAD + self.blockWidth // 2
                                                 - text.size[0] // 2,
                                                 GBoard.HEADER_HEIGHT + j * (self.blockWidth + GBoard.BLOCK_PAD)
                                                 + self.blockWidth // 2 - text.size[1] // 2,
                                                 text.size[1] + GBoard.BLOCK_PAD)
                        self.canvas.add(Rectangle(pos=text_pos,
                                                  size=text.size,
                                                  texture=text))


class Kv65536(App):
    def build(self):
        return GBoard()


if __name__ == '__main__':
    Kv65536().run()
