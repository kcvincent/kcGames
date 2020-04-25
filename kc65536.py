from kivy.logger import Logger
from kivy.core.window import Window
from kivy.uix.widget import Widget
from kivy.app import App
from kivy.graphics import Color,  Rectangle
from kivy.core.text import Label as CoreLabel
from random import *
import kivy.utils
from datetime import datetime
from win32api import GetSystemMetrics
from kivy.config import Config
import json
from math import floor

from Game2048Settings import Game2048Settings
from kcGameLib import *
from GameSaveData import GameSaveData

kivy.require("1.11.1")


class GameOverError(Exception):
    pass


class Game2048Board(Widget):
    @property
    def TotalBlocks(self):
        return self.layers * self.line_blocks * self.line_blocks

    @property
    def LayerWidth(self):
        return (self.block_width + self.block_pad) * self.line_blocks + self.block_pad

    @property
    def LayerHeight(self):
        return (self.block_height + self.block_pad) * self.line_blocks + self.block_pad

    def __init__(self, **kwargs):
        super(Game2048Board, self).__init__(**kwargs)

        self.screenWidth = GetSystemMetrics(0)
        self.screenHeight = GetSystemMetrics(1)
        (self.frame_width, self.frame_height) = (0, 0)

        self._keyboard = Window.request_keyboard(self._keyboard_closed, self, 'text')
        if self._keyboard.widget:
            # If it exists, this widget is a VKeyboard object which you can use
            # to change the keyboard layout.
            pass
        self._keyboard.bind(on_key_down=self._on_keyboard_down)

        self.settings = Game2048Settings()
        self.header_height = self.settings.HeaderHeight

        self.board_bg_color = self.settings.BoardBGColor

        self.layers = self.settings.Layers
        self.layer_space = self.settings.LayerSpace

        self.line_blocks = self.settings.LineBlocks
        self.block_bg_color_dict = self.settings.BlockBgColorDict
        self.block_text_color_dict = self.settings.BlockTextColorDict
        self.block_height = self.block_width = self.settings.BlockWidth
        self.block_pad = self.settings.BlockPad

        self.total_points = 0

        self.resizeWindow()
        self.tileMatrix = self.initMatrix()
        Logger.info(f"tileMatrix : All Zeros")

        self.new_block = (self.layers, self.line_blocks, self.line_blocks)
        Logger.info(f"newBlock : {self.new_block}")
        self.undoMat = []
        self.msg = "New Game"
        self.gameOvered = False
        self.printMatrix()
        self.reset()

        Window.bind(on_resize=self.on_window_resize)

    def initMatrix(self):
        return [[[0 for i in range(self.line_blocks)] for i in range(self.line_blocks)] for i in range(self.layers)]

    def resizeWindow(self):
        Window.size = (self.frame_width, self.frame_height) \
            = (self.LayerWidth * self.layers + (self.layers - 1) * self.layer_space,
               self.LayerHeight + self.header_height)
        Logger.info(f"LayerSize : ({self.LayerWidth}, {self.LayerHeight})")
        Logger.info(f"frameSize : ({self.frame_width}, {self.frame_height})")
        Logger.info(f"headerSize : ({self.frame_width}, {self.header_height})")

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

    def DoMergeTwoLayer(self, ly1, ly2):
        for i in range(0, self.line_blocks):
            for j in range(0, self.line_blocks):
                if self.tileMatrix[ly1][i][j] == self.tileMatrix[ly2][i][j]:
                    Logger.debug(f" Merge ({ly1},{i},{j}) {self.tileMatrix[ly1][i][j]} , ({ly2},{i},{j}) {self.tileMatrix[ly2][i][j]}=>  ({ly1},{i},{j}) {self.tileMatrix[ly1][i][j] + self.tileMatrix[ly2][i][j]}")
                    self.tileMatrix[ly1][i][j] += self.tileMatrix[ly2][i][j]
                    self.tileMatrix[ly2][i][j] = 0
                    self.addPoints(self.tileMatrix[ly1][i][j])
        self.placeRandomTile()

    def DoMergeUpperLayer(self):
        if self.layers > 1:
            for ly in range(0, self.layers - 1):
                self.DoMergeTwoLayer(ly, ly + 1)

    def DoMergeLowerLayer(self):
        if self.layers > 1:
            for ly in range(self.layers - 1, 0, -1):
                self.DoMergeTwoLayer(ly, ly - 1)

    def rotateMatrixClockwise(self):
        for ly in range(0, self.layers):
            for i in range(0, int(self.line_blocks / 2)):
                for k in range(i, self.line_blocks - i - 1):
                    temp1 = self.tileMatrix[ly][i][k]
                    temp2 = self.tileMatrix[ly][self.line_blocks - 1 - k][i]
                    temp3 = self.tileMatrix[ly][self.line_blocks - 1 - i][self.line_blocks - 1 - k]
                    temp4 = self.tileMatrix[ly][k][self.line_blocks - 1 - i]

                    self.tileMatrix[ly][self.line_blocks - 1 - k][i] = temp1
                    self.tileMatrix[ly][self.line_blocks - 1 - i][self.line_blocks - 1 - k] = temp2
                    self.tileMatrix[ly][k][self.line_blocks - 1 - i] = temp3
                    self.tileMatrix[ly][i][k] = temp4

    def canMove(self):
        """
          因為用了旋轉,所以只要檢查一個方向
        :return:
        """
        for ly in range(0, self.layers):
            for i in range(0, self.line_blocks):
                for j in range(1, self.line_blocks):
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
            for i in range(0, self.line_blocks):
                for j in range(0, self.line_blocks):
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
            for i in range(0, self.line_blocks):
                for j in range(0, self.line_blocks - 1):
                    while self.tileMatrix[ly][i][j] == 0 and sum(self.tileMatrix[ly][i][j:]) > 0:
                        for k in range(j, self.line_blocks - 1):
                            self.tileMatrix[ly][i][k] = self.tileMatrix[ly][i][k + 1]
                        self.tileMatrix[ly][i][self.line_blocks - 1] = 0

    def mergeTiles(self):
        for ly in range(0, self.layers):
            for i in range(0, self.line_blocks):
                for k in range(0, self.line_blocks - 1):
                    if self.tileMatrix[ly][i][k] == self.tileMatrix[ly][i][k + 1] and self.tileMatrix[ly][i][k] != 0:
                        self.tileMatrix[ly][i][k] = self.tileMatrix[ly][i][k] * 2
                        self.tileMatrix[ly][i][k + 1] = 0
                        # this was not intailized so the k value was going out the range value
                        # so by this we ever we merge the files it assigns the present value to zero and
                        # merge the number with the ahead value
                        self.addPoints(self.tileMatrix[ly][i][k])
                        self.moveTiles()

    def addPoints(self, inc_points):
        self.total_points += inc_points

    def placeRandomTile(self):
        zeros = []
        for ly in range(0, self.layers):
            for i in range(0, self.line_blocks):
                for j in range(0, self.line_blocks):
                    if self.tileMatrix[ly][i][j] == 0:
                        zeros.append((ly, i, j))
        if len(zeros) == 0:
            self.saveGameState()
            raise GameOverError("Game Over ??")

        (a, b, c) = zeros[randint(0, len(zeros)-1)]

        new_val_array = [2, 2, 4]
        new_val = new_val_array[randint(0, len(new_val_array)-1)]
        self.tileMatrix[a][b][c] = new_val
        self.new_block = (a, b, c)

    def checkIfCanGo(self):
        Logger.info(" checkIfCanGo Check all blocks Full ")
        for i in range(0, self.TotalBlocks):
            (a, b, c) = d1tod3(i, self.line_blocks)
            if self.tileMatrix[a][b][c] == 0:
                return True
        Logger.info(" checkIfCanGo Check blocks Moveable in Layer")
        for ly in range(0, self.layers):
            for i in range(0, self.line_blocks):
                for j in range(0, self.line_blocks - 1):
                    if self.tileMatrix[ly][i][j] == self.tileMatrix[ly][i][j + 1]:
                        return True
                    elif self.tileMatrix[ly][j][i] == self.tileMatrix[ly][j + 1][i]:
                        return True
        Logger.info(" checkIfCanGo Check Layers blocks Between Layers ")
        if self.layers > 1:
            for ly in range(0, self.layers-1):
                for i in range(0, self.line_blocks):
                    for j in range(0, self.line_blocks):
                        if self.tileMatrix[ly][i][j] == self.tileMatrix[ly+1][i][j]:
                            return True
        Logger.info(" checkIfCanGo False")
        return False

    # This module return an matrix rather than we can call it an list
    def convertToLinearMatrix(self):
        mat = []
        for i in range(0, self.TotalBlocks):
            (a, b, c) = d1tod3(i, self.line_blocks)
            mat.append(self.tileMatrix[a][b][c])
        mat.append(self.total_points)
        return mat

    def addToUndo(self):
        self.undoMat.append(self.convertToLinearMatrix())

    def reset(self):
        self.total_points = 0
        self.tileMatrix = self.initMatrix()
        self.undoMat = []
        self.new_block = (self.layers, self.line_blocks, self.line_blocks)
        self.gameOvered = False
        self.msg = "New Game"
        self.placeRandomTile()
        self.placeRandomTile()
        self.printMatrix()

    def saveGameState(self):
        gsd = GameSaveData(self.layers, self.line_blocks, self.total_points, self.tileMatrix)
        f = open(self.settings.SaveFileName, 'w')
        f.write(json.dumps(gsd.__dict__))
        f.close()
        self.msg = f'Saved at {datetime.now().strftime("%Y/%m/%d, %H:%M:%S")}'
        self.printMatrix()

    def loadGameState(self):
        f = open(self.settings.SaveFileName, "r")
        jsondata = f.readline()
        f.close()
        gsd = json.loads(jsondata)
        self.layers = gsd['_layers']
        self.line_blocks = gsd['_line_blocks']
        self.total_points = gsd['_total_points']
        self.tileMatrix = gsd['_tile_matrix']
        #mat = (f.readline()).split(' ', self.TotalBlocks)
        #for i in range(0, self.TotalBlocks):
        #   (a, b, c) = d1tod3(i, self.line_blocks)
        #  self.tileMatrix[a][b][c] = int(mat[i])
        self.resizeWindow()
        self.gameOvered = False
        self.msg = f'Loaded at {datetime.now().strftime("%Y/%m/%d, %H:%M:%S")}'
        self.printMatrix()

    def undo(self):
        if len(self.undoMat) > 0:
            mat = self.undoMat.pop()
            for i in range(0, self.line_blocks ** 2):
                self.tileMatrix[self.floor(i / self.line_blocks)][i % self.line_blocks] = mat[i]
            self.total_points = mat[self.line_blocks ** 2]
            self.msg = f'Undo at {datetime.now().strftime("%Y/%m/%d, %H:%M:%S")}'
            self.printMatrix()

    def on_window_resize(self, window, width, height):
        (self.frame_width, self.frame_height) = (width, height)
        self.printMatrix()

    def _keyboard_closed(self):
        print('My keyboard have been closed!')
        self._keyboard.unbind(on_key_down=self._on_keyboard_down)
        self._keyboard = None

    def _on_keyboard_down(self, keyboard, keycode, text, modifiers):
        #Keycode is composed of an integer + a string
        #If we hit escape, release the keyboard
        Logger.info(f"press {keycode} {text} {modifiers}")
        if keycode[1] == 'escape':
            keyboard.release()
        if self.gameOvered:
            Logger.info(f"Game Overed ")
            if keycode[1] == 'r':
                self.reset()
        else:
            Logger.info(f"Processing key")
            if self.checkIfCanGo():
                Logger.info(f"checked")
                if isArrow(keycode[1]):
                    rotations = getRotations(keycode[1])
                    self.addToUndo()
                    self.DoAStep(rotations)
                    self.checkGameOver()
                    self.printMatrix()
                elif keycode[1] == 'q':
                    self.addToUndo()
                    self.DoMergeUpperLayer()
                    self.checkGameOver()
                    self.printMatrix()
                elif keycode[1] == 'e':
                    self.addToUndo()
                    self.DoMergeLowerLayer()
                    self.checkGameOver()
                    self.printMatrix()
                elif keycode[1] == 's':
                    self.saveGameState()
                elif keycode[1] == 'l':
                    self.loadGameState()
                elif keycode[1] == 'u':
                    self.undo()
                Logger.info(f"Done keycode {keycode}")


        # Return True to accept the key. Otherwise, it will be used by
        # the system.
        return True

    def checkGameOver(self):
        self.gameOvered = not self.checkIfCanGo()
        if self.gameOvered:
            self.msg = f"Game Over!!Press R to New a Game"

    def toKivyXY(self, x, y, offset=0):
        """
        :param offset:
        :param x: 0 as Left
        :param y: 0 as Top
        :return: kivy y as Bottom
        """
        return x, self.frame_height - y - offset

    def getBlockColor(self, ly, i, j):
        return self.block_bg_color_dict[self.tileMatrix[ly][i][j]]
    
    def getBlockTextColor(self, ly, i, j):
        return self.block_text_color_dict[self.tileMatrix[ly][i][j]]

    def getBlockX(self, ly, i, j ):
        return ly * (self.LayerWidth + self.layer_space) + i * (self.block_width + self.block_pad) + self.block_pad

    def getBlockY(self, ly, i, j):
        return self.header_height + j * (self.block_width + self.block_pad)

    def drawBackGround(self):
        # Draw BackGround
        self.canvas.add(Color(rgb=self.board_bg_color))
        self.canvas.add(Rectangle(pos=(0, 0), size=(self.frame_width, self.frame_height)))

    def drawHeaderZone(self):
        self.canvas.add(Color(rgb=(1., 1., 1.)))
        label = CoreLabel(text=f"Score : {self.total_points} ", font_size=20)
        label.refresh()
        text = label.texture
        self.canvas.add(Rectangle(size=text.size,
                                  pos=self.toKivyXY(self.block_pad, text.size[1], text.size[1]),
                                  texture=text))

        if len(self.msg) > 0:
            label = CoreLabel(text=self.msg, font_size=20)
            label.refresh()
            text = label.texture
            self.canvas.add(Rectangle(size=text.size,
                                      pos=self.toKivyXY(self.block_pad, text.size[1] * 2, text.size[1]),
                                      texture=text))


    def printMatrix(self):
        self.canvas.clear()

        self.drawBackGround()
        # Draw Banner Zone /Score
        self.drawHeaderZone()
        # Draw Banner Zone /Message

        for ly in range(0, self.layers):
            for i in range(0, self.line_blocks):
                for j in range(0, self.line_blocks):
                    # Draw Block outline
                    self.canvas.add(Color(rgb=self.getBlockColor(ly, i, j)))
                    block_pos = self.toKivyXY(self.getBlockX(ly, i, j), self.getBlockY(ly, i, j), self.block_width + self.block_pad)
                    self.canvas.add(Rectangle(pos=block_pos, size=(self.block_width, self.block_height)))
                    # Draw Block Text
                    if self.tileMatrix[ly][i][j] != 0:
                        if self.new_block == (ly, i, j):
                            self.canvas.add(Color(rgb=(0., 0., 1.)))
                        else:
                            self.canvas.add(Color(rgb=self.getBlockTextColor(ly, i, j)))
                        label = CoreLabel(text=f"{self.tileMatrix[ly][i][j]}", font_size=48)
                        label.refresh()
                        text = label.texture
                        text_pos = self.toKivyXY(self.getBlockX(ly, i, j) + self.block_width // 2 - text.size[0] // 2,
                                                 self.getBlockY(ly, i, j) + self.block_width // 2 - text.size[1] // 2,
                                                 text.size[1] + self.block_pad)

                        #text_pos = self.toKivyXY(ly * (self.layerWidth + self.layerSpace) +
                        #                         i * (self.block_width + self.block_pad) + self.block_pad + self.block_width // 2
                        #                         - text.size[0] // 2,
                        #                         self.header_height + j * (self.block_width + self.block_pad)
                        #                         + self.block_width // 2 - text.size[1] // 2,
                        #                         text.size[1] + self.block_pad)
                        self.canvas.add(Rectangle(pos=text_pos,
                                                  size=text.size,
                                                  texture=text))




class KcGames(App):
    def build_config(self, config):
        config.setdefaults('section1', {
            'key1': 'value1',
            'key2': '42'
        })

    def build(self):
        return Game2048Board()


if __name__ == '__main__':
    KcGames().run()
