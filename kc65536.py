# -*- coding: utf-8 -*-
from datetime import datetime
from random import *
import kivy.utils
from kivy.app import App
from kivy.core.text import Label as CoreLabel
from kivy.core.image import Image as CoreImage
from kivy.core.window import Window
from kivy.graphics import Color, Rectangle
from kivy.logger import Logger
from kivy.uix.widget import Widget
from win32api import GetSystemMetrics
from GameSettings import GameSettings
from kcGameLib import *


kivy.require("1.11.1")


class GameOverError(Exception):
    pass


class Game2048Board(Widget):
    @property
    def TotalBlocks(self):
        return self.settings.Layers * self.settings.LineBlocks * self.settings.LineBlocks

    @property
    def LayerWidth(self):
        return (self.settings.BlockWidth + self.settings.BlockPad) * self.settings.LineBlocks + self.settings.BlockPad

    @property
    def LayerHeight(self):
        return (self.settings.BlockHeight + self.settings.BlockPad) * self.settings.LineBlocks + self.settings.BlockPad

    @property
    def HeaderHeight(self):
        return self.settings.HeaderHeight

    @property
    def BoardBGColor(self):
        return self.settings.BoardBGColor

    @property
    def Layers(self):
        return self.settings.Layers

    @property
    def LayerSpace(self):
        return self.settings.LayerSpace

    @property
    def LineBlocks(self):
        return self.settings.LineBlocks

    @property
    def BlockBGColorDict(self):
        return self.settings.BlockBgColorDict

    @property
    def BlockTextColorDict(self):
        return self.settings.BlockTextColorDict

    @property
    def BlockHeight(self):
        return self.settings.BlockWidth

    @property
    def BlockWidth(self):
        return self.settings.BlockWidth

    @property
    def BlockPad(self):
        return self.settings.BlockPad

    def __init__(self, settings, **kwargs):
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

        self.settings = settings
        self.total_points = 0

        self.resizeWindow()
        self.tileMatrix = self.initMatrix()
        Logger.info(f"tileMatrix : All Zeros")

        self.new_block = (self.Layers, self.LineBlocks, self.LineBlocks)
        Logger.info(f"newBlock : {self.new_block}")
        self.undoMat = []
        self.msg = "New Game"
        self.gameOvered = False
        self.printMatrix()
        self.reset()

        Window.bind(on_resize=self.on_window_resize)

    def initMatrix(self):
        return [[[0 for _ in range(self.LineBlocks)] for _ in range(self.LineBlocks)] for _ in range(self.Layers)]

    def resizeWindow(self):
        Window.size = (self.frame_width, self.frame_height) \
            = (self.LayerWidth * self.Layers + (self.Layers - 1) * self.LayerSpace,
               self.LayerHeight + self.HeaderHeight)
        Window.left = (self.screenWidth - self.frame_width) // 2
        Window.top = (self.screenHeight - self.frame_height) // 2
        Logger.info(f"LayerSize : ({self.LayerWidth}, {self.LayerHeight})")
        Logger.info(f"frameSize : ({self.frame_width}, {self.frame_height})")
        Logger.info(f"headerSize : ({self.frame_width}, {self.HeaderHeight})")

    def DoAStep(self, rotations):
        for i in range(0, rotations):
            self.rotateMatrixClockwise()
        if self.canMove():
            self.moveTiles()
            if self.settings.GameStyle == 0:
                self.mergeTwoEquTiles()
            elif self.settings.GameStyle == 1:
                self.mergeThreeEquTiles()
            elif self.settings.GameStyle == 2:
                self.mergeFibonacciTiles()
            else:
                self.mergeTwoEquTiles()
            for j in range(0, (4 - rotations) % 4):
                self.rotateMatrixClockwise()
            self.placeRandomTile()
        else:
            for j in range(0, (4 - rotations) % 4):
                self.rotateMatrixClockwise()

    def DoMergeTwoLayer(self, ly1, ly2):
        for i in range(0, self.LineBlocks):
            for j in range(0, self.LineBlocks):
                if self.tileMatrix[ly1][i][j] == self.tileMatrix[ly2][i][j]:
                    Logger.debug(f" Merge ({ly1},{i},{j}) {self.tileMatrix[ly1][i][j]} , ")
                    Logger.debug(f"       ({ly2},{i},{j}) {self.tileMatrix[ly2][i][j]} ")
                    Logger.debug(f" Into  ({ly1},{i},{j}) {self.tileMatrix[ly1][i][j] + self.tileMatrix[ly2][i][j]}")
                    self.tileMatrix[ly1][i][j] += self.tileMatrix[ly2][i][j]
                    self.tileMatrix[ly2][i][j] = 0
                    self.addPoints(self.tileMatrix[ly1][i][j])

    def DoMergeUpperLayer(self):
        if self.Layers > 1:
            for ly in range(0, self.Layers - 1):
                self.DoMergeTwoLayer(ly, ly + 1)
            self.placeRandomTile()

    def DoMergeLowerLayer(self):
        if self.Layers > 1:
            for ly in range(self.Layers - 1, 0, -1):
                self.DoMergeTwoLayer(ly, ly - 1)
            self.placeRandomTile()

    def rotateMatrixClockwise(self):
        for ly in range(0, self.Layers):
            for i in range(0, int(self.LineBlocks / 2)):
                for k in range(i, self.LineBlocks - i - 1):
                    temp1 = self.tileMatrix[ly][i][k]
                    temp2 = self.tileMatrix[ly][self.LineBlocks - 1 - k][i]
                    temp3 = self.tileMatrix[ly][self.LineBlocks - 1 - i][self.LineBlocks - 1 - k]
                    temp4 = self.tileMatrix[ly][k][self.LineBlocks - 1 - i]

                    self.tileMatrix[ly][self.LineBlocks - 1 - k][i] = temp1
                    self.tileMatrix[ly][self.LineBlocks - 1 - i][self.LineBlocks - 1 - k] = temp2
                    self.tileMatrix[ly][k][self.LineBlocks - 1 - i] = temp3
                    self.tileMatrix[ly][i][k] = temp4

    def canMove(self):
        """
          因為用了旋轉,所以只要檢查一個方向, left to right
        :return:
        """
        if self.settings.GameStyle == 1:
            for ly in range(0, self.Layers):
                for i in range(0, self.LineBlocks):
                    for j in range(2, self.LineBlocks):
                        if self.tileMatrix[ly][i][j - 2] == 0 or \
                                self.tileMatrix[ly][i][j - 1] == 0 or \
                                self.tileMatrix[ly][i][j] == 0:
                            return True
                        elif (self.tileMatrix[ly][i][j - 2] != 0) and \
                                (self.tileMatrix[ly][i][j - 2] == self.tileMatrix[ly][i][j -1 ]) and \
                                (self.tileMatrix[ly][i][j - 1] == self.tileMatrix[ly][i][j]) :
                            return True
        elif self.settings.GameStyle == 2:
            keylist = self.settings.KeyList
            for ly in range(0, self.Layers):
                for i in range(0, self.LineBlocks):
                    for j in range(1, self.LineBlocks):
                        if self.tileMatrix[ly][i][j - 1] == 0 or \
                                self.tileMatrix[ly][i][j] > 0:
                            return True
                        elif (self.tileMatrix[ly][i][j - 1] != 0) and \
                            self.FibonacciMatchable(keylist, self.tileMatrix[ly][i][j - 1], self.tileMatrix[ly][i][j]):
                            return True
        else: # if self.settings.GameStyle == 0 or other
            for ly in range(0, self.Layers):
                for i in range(0, self.LineBlocks):
                    for j in range(1, self.LineBlocks):
                        if self.tileMatrix[ly][i][j - 1] == 0 and self.tileMatrix[ly][i][j] > 0:
                            return True
                        elif (self.tileMatrix[ly][i][j - 1] == self.tileMatrix[ly][i][j]) and \
                                self.tileMatrix[ly][i][j - 1] != 0:
                            return True
        return False

    def canLayerMove(self):
        """
          檢查上下層可否移動
        :return:
        """
        for ly in range(0, self.Layers - 1):
            for i in range(0, self.LineBlocks):
                for j in range(0, self.LineBlocks):
                    if self.tileMatrix[ly][i][j] == 0 and self.tileMatrix[ly + 1][i][j] > 0:
                        # 當前 層 為零, ly+1層不為零
                        return True
                    elif self.tileMatrix[ly][i][j] != 0 and (
                            self.tileMatrix[ly][i][j] == self.tileMatrix[ly + 1][i][j]):
                        # 當前 層 不為零, 當前 層 = ly+1層
                        return True
                    elif self.tileMatrix[self.Layers - 1 - ly][i][j] == 0 and \
                            self.tileMatrix[self.Layers - 1 - ly - 1][i][j] > 0:
                        # 倒序 當前 層 為零, ly - 1層不為零
                        return True

    def moveTiles(self):
        for ly in range(0, self.Layers):
            for i in range(0, self.LineBlocks):
                for j in range(0, self.LineBlocks - 1):
                    while self.tileMatrix[ly][i][j] == 0 and sum(self.tileMatrix[ly][i][j:]) > 0:
                        for k in range(j, self.LineBlocks - 1):
                            self.tileMatrix[ly][i][k] = self.tileMatrix[ly][i][k + 1]
                        self.tileMatrix[ly][i][self.LineBlocks - 1] = 0


    def TwoEquMatchable(self, a, b):
        return a == b


    def FibonacciMatchable(self, key_list, a, b):
        if (a in key_list) and (b in key_list):
            idx1 = key_list.index(a)
            idx2 = key_list.index(b)
            return (idx1 == idx2 + 1) or (idx1 == idx2 - 1)
        return False

    def mergeTwoEquTiles(self):
        for ly in range(0, self.Layers):
            for i in range(0, self.LineBlocks):
                for k in range(0, self.LineBlocks - 1):
                    if self.tileMatrix[ly][i][k] != 0:
                        if self.TwoEquMatchable(self.tileMatrix[ly][i][k], self.tileMatrix[ly][i][k + 1]):
                            self.tileMatrix[ly][i][k] = self.tileMatrix[ly][i][k] * 2
                            self.tileMatrix[ly][i][k + 1] = 0
                            # this was not intailized so the k value was going out the range value
                            # so by this we ever we merge the files it assigns the present value to zero and
                            # merge the number with the ahead value
                            self.addPoints(self.tileMatrix[ly][i][k])
                            self.moveTiles()

    def mergeFibonacciTiles(self):
        key_list = self.settings.KeyList
        for ly in range(0, self.Layers):
            for i in range(0, self.LineBlocks):
                for k in range(0, self.LineBlocks - 1):
                    if self.tileMatrix[ly][i][k] != 0:
                        if self.FibonacciMatchable(key_list, self.tileMatrix[ly][i][k], self.tileMatrix[ly][i][k + 1]):
                            self.tileMatrix[ly][i][k] = self.tileMatrix[ly][i][k] + self.tileMatrix[ly][i][k + 1]
                            self.tileMatrix[ly][i][k + 1] = 0
                            # this was not intailized so the k value was going out the range value
                            # so by this we ever we merge the files it assigns the present value to zero and
                            # merge the number with the ahead value
                            self.addPoints(self.tileMatrix[ly][i][k])
                            self.moveTiles()

    def ThreeEquMatchable(self, a, b, c):
        return a == b and b == c

    def mergeThreeEquTiles(self):
        for ly in range(0, self.Layers):
            for i in range(0, self.LineBlocks):
                for k in range(0, self.LineBlocks - 2):
                    if self.tileMatrix[ly][i][k] != 0:
                        if self.ThreeEquMatchable(self.tileMatrix[ly][i][k], self.tileMatrix[ly][i][k + 1], self.tileMatrix[ly][i][k + 2]):
                            self.tileMatrix[ly][i][k] = self.tileMatrix[ly][i][k] * 3
                            self.tileMatrix[ly][i][k + 1] = 0
                            self.tileMatrix[ly][i][k + 2] = 0
                            # this was not intailized so the k value was going out the range value
                            # so by this we ever we merge the files it assigns the present value to zero and
                            # merge the number with the ahead value
                            self.addPoints(self.tileMatrix[ly][i][k])
                            self.moveTiles()


    def addPoints(self, inc_points):
        self.total_points += inc_points

    def gen2048NewValue(self, zeroBlocks):
        (a, b, c) = zeroBlocks[randint(0, len(zeroBlocks) - 1)]
        new_val_array = [2, 2, 4]
        new_val = new_val_array[randint(0, len(new_val_array) - 1)]
        return a, b, c, new_val

    def gen339NewValue(self, zeroBlocks):
        (a, b, c) = zeroBlocks[randint(0, len(zeroBlocks) - 1)]
        new_val_array = [3, 3, 9]
        new_val = new_val_array[randint(0, len(new_val_array) - 1)]
        return a, b, c, new_val

    def genFibonNewValue(self, zeroBlocks):
        (a, b, c) = zeroBlocks[randint(0, len(zeroBlocks) - 1)]
        new_val_array = [2, 2, 3, 3]
        new_val = new_val_array[randint(0, len(new_val_array) - 1)]
        return a, b, c, new_val


    def placeRandomTile(self):
        zeroBlocks = []
        for ly in range(0, self.Layers):
            for i in range(0, self.LineBlocks):
                for j in range(0, self.LineBlocks):
                    if self.tileMatrix[ly][i][j] == 0:
                        zeroBlocks.append((ly, i, j))
        if len(zeroBlocks) == 0:
            return

        if self.settings.GameStyle == 0:
            a, b, c, new_val = self.gen2048NewValue(zeroBlocks)
        elif self.settings.GameStyle == 1:
            a, b, c, new_val = self.gen339NewValue(zeroBlocks)
        elif self.settings.GameStyle == 2:
            a, b, c, new_val = self.genFibonNewValue(zeroBlocks)
        else:
            a, b, c, new_val = self.gen2048NewValue(zeroBlocks)
        ##a, b, c, new_val = self.gen339NewValue(zeroBlocks)
        #(a, b, c) = zeros[randint(0, len(zeros) - 1)]
        #new_val_array = [2, 2, 4]
        #new_val = new_val_array[randint(0, len(new_val_array) - 1)]
        self.tileMatrix[a][b][c] = new_val
        self.new_block = (a, b, c)

    def checkIfCanGo(self):
        Logger.info(" checkIfCanGo Check all blocks Full ")
        for i in range(0, self.TotalBlocks):
            (a, b, c) = d1tod3(i, self.LineBlocks)
            if self.tileMatrix[a][b][c] == 0:
                return True
        Logger.info(" checkIfCanGo Check blocks Moveable in Layer")
        #for ly in range(0, self.Layers):
        #    for i in range(0, self.LineBlocks):
        #        for j in range(0, self.LineBlocks - 1):
        #            if self.tileMatrix[ly][i][j] == self.tileMatrix[ly][i][j + 1]:
        #                return True
        #            elif self.tileMatrix[ly][j][i] == self.tileMatrix[ly][j + 1][i]:
        #                return True
        if self.settings.GameStyle == 0:
            for ly in range(0, self.Layers):
                for i in range(0, self.LineBlocks):
                    for j in range(0, self.LineBlocks - 1):
                        if self.TwoEquMatchable(self.tileMatrix[ly][i][j], self.tileMatrix[ly][i][j + 1]):
                            return True
                        elif self.TwoEquMatchable(self.tileMatrix[ly][j][i], self.tileMatrix[ly][j + 1][i]):
                            return True
        elif self.settings.GameStyle == 1:
            for ly in range(0, self.Layers):
                for i in range(0, self.LineBlocks):
                    for j in range(0, self.LineBlocks - 2):
                        if self.ThreeEquMatchable(self.tileMatrix[ly][i][j], self.tileMatrix[ly][i][j + 1], self.tileMatrix[ly][i][j + 2]):
                            return True
                        elif self.ThreeEquMatchable(self.tileMatrix[ly][j][i] , self.tileMatrix[ly][j + 1][i], self.tileMatrix[ly][j + 2][i]):
                            return True
        elif self.settings.GameStyle == 2:
            keylist = self.settings.KeyList
            for ly in range(0, self.Layers):
                for i in range(0, self.LineBlocks):
                    for j in range(0, self.LineBlocks - 1):
                        if self.FibonacciMatchable(keylist, self.tileMatrix[ly][i][j], self.tileMatrix[ly][i][j + 1]):
                            return True
                        elif self.FibonacciMatchable(keylist, self.tileMatrix[ly][j][i], self.tileMatrix[ly][j + 1][i]):
                            return True
        #else:
        #    for ly in range(0, self.Layers):
        #        for i in range(0, self.LineBlocks):
        #            for j in range(0, self.LineBlocks - 1):
        #                if self.matchTwoEqu(self.tileMatrix[ly][i][j], self.tileMatrix[ly][i][j + 1]):
        #                    return True
        #                elif self.matchTwoEqu(self.tileMatrix[ly][j][i], self.tileMatrix[ly][j + 1][i]):
        #                    return True

        Logger.info(" checkIfCanGo Check Layers blocks Between Layers ")
        if self.Layers > 1:
            for ly in range(0, self.Layers - 1):
                for i in range(0, self.LineBlocks):
                    for j in range(0, self.LineBlocks):
                        if self.tileMatrix[ly][i][j] == self.tileMatrix[ly + 1][i][j]:
                            return True
        Logger.info(" checkIfCanGo False")
        return False

    # This module return an matrix rather than we can call it an list
    def convertToLinearMatrix(self):
        mat = []
        for i in range(0, self.TotalBlocks):
            (a, b, c) = d1tod3(i, self.LineBlocks)
            mat.append(self.tileMatrix[a][b][c])
        mat.append(self.total_points)
        return mat

    def addToUndo(self):
        self.undoMat.append(self.convertToLinearMatrix())

    def reset(self):
        self.total_points = 0
        self.tileMatrix = self.initMatrix()
        self.undoMat = []
        self.new_block = (self.Layers, self.LineBlocks, self.LineBlocks)
        self.gameOvered = False
        self.msg = "New Game"
        self.placeRandomTile()
        self.placeRandomTile()
        self.printMatrix()

    def saveGameState(self):
        self.settings.SaveToFile(self.tileMatrix)
        self.msg = f'Saved at {datetime.now().strftime("%Y/%m/%d, %H:%M:%S")}'
        self.printMatrix()

    def loadGameState(self):
        self.settings.LoadFromFile()
        self.tileMatrix = self.settings.TileMatrix
        self.resizeWindow()
        self.gameOvered = False
        self.msg = f'Loaded at {datetime.now().strftime("%Y/%m/%d, %H:%M:%S")}'
        self.printMatrix()

    def undo(self):
        if len(self.undoMat) > 0:
            mat = self.undoMat.pop()
            for i in range(0, self.LineBlocks ** 2):
                self.tileMatrix[self.floor(i / self.LineBlocks)][i % self.LineBlocks] = mat[i]
            self.total_points = mat[self.LineBlocks ** 2]
            self.msg = f'Undo at {datetime.now().strftime("%Y/%m/%d, %H:%M:%S")}'
            self.printMatrix()

    def on_window_resize(self, window, width, height):
        Logger.trace(f"on_window_resize : {window} , {width} ,{height}")
        (self.frame_width, self.frame_height) = (width, height)
        self.printMatrix()

    def _keyboard_closed(self):
        print('My keyboard have been closed!')
        self._keyboard.unbind(on_key_down=self._on_keyboard_down)
        self._keyboard = None

    def DoMergeUpper(self):
        self.addToUndo()
        self.DoMergeUpperLayer()
        self.checkGameOver()
        self.printMatrix()

    def _on_keyboard_down(self, keyboard, keycode, text, modifiers):
        # Keycode is composed of an integer + a string
        # If we hit escape, release the keyboard
        Logger.info(f"press {keycode}")
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
                #if isArrow(keycode[1]):
                #    rotations = getRotations(keycode[1])
                #    self.addToUndo()
                #    self.DoAStep(rotations)
                #    self.checkGameOver()
                #    self.printMatrix()
                if keycode[1] == 'up':
                    self.DoMergeNorth()
                elif keycode[1] == 'down':
                    self.DoMergeSouth()
                elif keycode[1] == 'left':
                    self.DoMergeWest()
                elif keycode[1] == 'right':
                    self.DoMergeEast()
                elif keycode[1] == 'q':
                    self.DoMergeUpper()
                elif keycode[1] == 'e':
                    self.DoMergeLower()
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

    def DoMergeEast(self):
        self.addToUndo()
        self.DoAStep(3)
        self.checkGameOver()
        self.printMatrix()

    def DoMergeWest(self):
        self.addToUndo()
        self.DoAStep(1)
        self.checkGameOver()
        self.printMatrix()

    def DoMergeSouth(self):
        self.addToUndo()
        self.DoAStep(2)
        self.checkGameOver()
        self.printMatrix()

    def DoMergeNorth(self):
        self.addToUndo()
        self.DoAStep(0)
        self.checkGameOver()
        self.printMatrix()

    def DoMergeLower(self):
        self.addToUndo()
        self.DoMergeLowerLayer()
        self.checkGameOver()
        self.printMatrix()

    def checkGameOver(self):
        self.gameOvered = not self.checkIfCanGo()
        if self.gameOvered:
            self.msg = f"Game Over!!Press R to New a Game"

    def toKivyXY(self, x, y, offset=0):
        return x, self.frame_height - y - offset

    def getBlockColor(self, ly, i, j):
        return self.BlockBGColorDict[self.tileMatrix[ly][i][j]]

    def getBlockTextColor(self, ly, i, j):
        return self.BlockTextColorDict[self.tileMatrix[ly][i][j]]

    def getBlockX(self, ly, col):
        return ly * (self.LayerWidth + self.LayerSpace) + col * (self.BlockWidth + self.BlockPad) + self.BlockPad

    def getBlockY(self, row):
        return self.HeaderHeight + row * (self.BlockWidth + self.BlockPad)

    def drawBackGround(self):
        # Draw BackGround
        self.canvas.add(Color(rgb=self.BoardBGColor))
        self.canvas.add(Rectangle(pos=(0, 0), size=(self.frame_width, self.frame_height)))

    def drawHeaderZone(self):
        self.canvas.add(Color(rgb=(1., 1., 1.)))
        label = CoreLabel(text=f"Score : {self.total_points} ", font_size=20)
        label.refresh()
        text = label.texture
        self.canvas.add(Rectangle(size=text.size,
                                  pos=self.toKivyXY(self.BlockPad, text.size[1], text.size[1]),
                                  texture=text))

        if len(self.msg) > 0:
            label = CoreLabel(text=self.msg, font_size=20)
            label.refresh()
            text = label.texture
            self.canvas.add(Rectangle(size=text.size,
                                      pos=self.toKivyXY(self.BlockPad, text.size[1] * 2, text.size[1]),
                                      texture=text))
        #msg = datetime.now().strftime("%H%M%S")
        #rawimg = genQrCodeBytesIO(msg)
        #img = CoreImage(BytesIO(rawimg.read()), ext="png", filename="image.png")
        #self.canvas.add(Rectangle(size=(100, 100), pos=self.toKivyXY(100, 100), texture=img.texture))

    def printMatrix(self):
        self.canvas.clear()

        self.drawBackGround()
        # Draw Banner Zone /Score
        self.drawHeaderZone()
        # Draw Banner Zone /Message

        for ly in range(0, self.Layers):
            for i in range(0, self.LineBlocks):
                for j in range(0, self.LineBlocks):
                    # Draw Block outline
                    self.canvas.add(Color(rgb=self.getBlockColor(ly, i, j)))
                    block_pos = self.toKivyXY(self.getBlockX(ly, i), self.getBlockY(j),
                                              self.BlockWidth + self.BlockPad)
                    self.canvas.add(Rectangle(pos=block_pos, size=(self.BlockWidth, self.BlockHeight)))
                    # Draw Block Text
                    if self.tileMatrix[ly][i][j] != 0:
                        if self.new_block == (ly, i, j):
                            self.canvas.add(Color(rgb=(0., 0., 1.)))
                        else:
                            self.canvas.add(Color(rgb=self.getBlockTextColor(ly, i, j)))
                        label = CoreLabel(text=f"{self.tileMatrix[ly][i][j]}", font_size=48)
                        label.refresh()
                        text = label.texture
                        text_pos = self.toKivyXY(self.getBlockX(ly, i) + self.BlockWidth // 2 - text.size[0] // 2,
                                                 self.getBlockY(j) + self.BlockWidth // 2 - text.size[1] // 2,
                                                 text.size[1] + self.BlockPad)

                        self.canvas.add(Rectangle(pos=text_pos, size=text.size, texture=text))


class KcGames(App):
    def __init__(self, **kwargs):
        super(KcGames, self).__init__(**kwargs)
        self.GameSettings = GameSettings()

    def build(self):
        return Game2048Board(self.GameSettings)


if __name__ == '__main__':
    KcGames().run()
