# coding:utf-8
from typing import List
from enum import Enum

from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QPen, QBrush, QPainter, QColor
from PyQt5.QtWidgets import QWidget

from .button import ButtonFactory as BF
from .button import Button


class SelectionModeBarBase(QWidget):
    """ 选择模式栏基类 """

    cancelSig = pyqtSignal()
    playSig = pyqtSignal()
    nextToPlaySig = pyqtSignal()
    addToSig = pyqtSignal()
    singerSig = pyqtSignal()
    albumSig = pyqtSignal()
    propertySig = pyqtSignal()
    editInfoSig = pyqtSignal()
    pinToStartSig = pyqtSignal()
    renameSig = pyqtSignal()
    moveUpSig = pyqtSignal()
    moveDownSig = pyqtSignal()
    deleteSig = pyqtSignal()
    checkAllSig = pyqtSignal(bool)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.buttons = []
        self.__buttonToHides = []
        self.__alwaysVisibleButtons = []
        self.__currentVisibleButtons = []
        self.__separatorIndexes = []
        self.hasHidePartButton = False
        self.__signalMap = {
            'cancelButton': self.cancelSig,
            'playButton': self.playSig,
            'nextToPlayButton': self.nextToPlaySig,
            'addToButton': self.addToSig,
            'singerButton': self.singerSig,
            'albumButton': self.albumSig,
            'propertyButton': self.propertySig,
            'editInfoButton': self.editInfoSig,
            'pinToStartButton': self.pinToStartSig,
            'renameButton': self.renameSig,
            'moveUpButton': self.moveUpSig,
            'moveDownButton': self.moveDownSig,
            'deleteButton': self.deleteSig,
            'checkAllButton': self.checkAllSig
        }

    def addButton(self, button: int):
        """ 向窗口右侧添加一个按钮 """
        self.addButtons([button])

    def addSeparator(self):
        """ 添加分隔符 """
        if not self.buttons:
            return

        self.__separatorIndexes.append(len(self.buttons))

    def insertSeparator(self, index: int):
        """ 在指定位置插入分隔符 """
        if index < 1:
            return

        self.__separatorIndexes.append(index)
        self.__separatorIndexes.sort()

    def addButtons(self, buttons: List[int]):
        """ 向窗口添加多个按钮

        Parameters
        ----------
        buttons: List[int]
            按钮类型列表
        """
        bf = BF()
        buttons = [bf.create(i) for i in buttons]

        for button in buttons:
            name = button.objectName()
            setattr(self, name, button)
            button.setParent(self)
            button.show()

            button.clicked.connect(self.__signalMap[name])
            if name in ['playButton', 'nextToPlayButton', 'pinToStartButton']:
                button.clicked.connect(self.cancelSig)

        self.buttons.extend(buttons)
        self.__currentVisibleButtons.extend(buttons)
        self.__adjustButtonPos()

    def setToHideButtons(self, buttons: List[Button]):
        """ 设置在多选模式下需要隐藏的按钮 """
        self.__buttonToHides = buttons
        self.__alwaysVisibleButtons = [
            i for i in self.buttons if i not in buttons]

    def setPartButtonHidden(self, isHidden: bool):
        """ 隐藏指定的隐藏列表中的按钮 """
        if self.hasHidePartButton == isHidden:
            return

        self.hasHidePartButton = isHidden
        for button in self.__buttonToHides:
            button.setHidden(isHidden)

        if not isHidden:
            self.__currentVisibleButtons = self.buttons
        else:
            self.__currentVisibleButtons = self.__alwaysVisibleButtons

        self.__adjustButtonPos()

    def __adjustButtonPos(self):
        """ 调整此时可见的按钮的位置 """
        for index, button in enumerate(self.__currentVisibleButtons[::-1]):
            rawIndex = self.buttons.index(button)
            isRightHasSeparator = (rawIndex + 1 in self.__separatorIndexes)
            button.move(self.width() - (index + 1) * button.width() -
                        41 * isRightHasSeparator, 0)

        # 调整窗口高度
        heights = [i.height() for i in self.__currentVisibleButtons]
        height = max(heights) if heights else 70
        self.resize(self.width(), height)

        # 刷新界面
        self.update()

    def resizeEvent(self, e):
        """ 改变尺寸时移动按钮 """
        self.__adjustButtonPos()

    def paintEvent(self, e):
        """ 绘制分隔符 """
        painter = QPainter(self)
        painter.setPen(Qt.NoPen)
        painter.setBrush(QBrush(QColor(230, 230, 230)))
        painter.drawRect(self.rect())
        painter.setPen(QPen(QColor(203, 203, 203)))
        for index in self.__separatorIndexes:
            x = self.buttons[index - 1].x(
            ) + self.buttons[index - 1].width() + 20
            painter.drawLine(x, 15, x + 1, self.height() - 15)


class SongTabSelectionModeBar(SelectionModeBarBase):
    """ 我的音乐歌曲界面选择模式栏 """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.addButtons([
            BF.CANCEL, BF.PLAY, BF.NEXT_TO_PLAY,
            BF.ADD_TO, BF.ALBUM, BF.EDIT_INFO,
            BF.PROPERTY, BF.DELETE, BF.CHECK_ALL
        ])
        self.setToHideButtons(self.buttons[4:-2])
        self.insertSeparator(1)


class AlbumTabSelectionModeBar(SelectionModeBarBase):
    """ 我的音乐专辑界面选择模式栏 """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.addButtons([
            BF.CANCEL, BF.PLAY, BF.NEXT_TO_PLAY,
            BF.ADD_TO, BF.SINGER, BF.PIN_TO_START,
            BF.EDIT_INFO, BF.DELETE, BF.CHECK_ALL
        ])
        self.setToHideButtons(self.buttons[4:-2])
        self.insertSeparator(1)


class PlayingSelectionModeBar(SelectionModeBarBase):
    """ 正在播放界面选择模式栏 """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.addButtons([
            BF.CANCEL, BF.PLAY, BF.ADD_TO,
            BF.DELETE, BF.MOVE_UP, BF.MOVE_DOWN,
            BF.ALBUM, BF.PROPERTY, BF.CHECK_ALL
        ])
        self.setToHideButtons([self.buttons[1]]+self.buttons[4:-1])
        self.insertSeparator(1)


class SingerInterfaceSelectionModeBar(SelectionModeBarBase):
    """ 歌手界面选择模式栏 """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.addButtons([
            BF.CANCEL, BF.PLAY, BF.NEXT_TO_PLAY,
            BF.ADD_TO, BF.PIN_TO_START, BF.EDIT_INFO,
            BF.DELETE, BF.CHECK_ALL
        ])
        self.setToHideButtons(self.buttons[4:6])
        self.insertSeparator(1)


class AlbumInterfaceSelectionModeBar(SelectionModeBarBase):
    """ 专辑界面选择模式栏 """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.addButtons([
            BF.CANCEL, BF.PLAY, BF.NEXT_TO_PLAY,
            BF.ADD_TO, BF.EDIT_INFO, BF.PROPERTY,
            BF.DELETE, BF.CHECK_ALL
        ])
        self.setToHideButtons(self.buttons[4:6])
        self.insertSeparator(1)


class PlaylistCardSelectionModeBar(SelectionModeBarBase):
    """ 播放列表卡界面选择模式栏 """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.addButtons([
            BF.CANCEL, BF.PLAY, BF.NEXT_TO_PLAY,
            BF.ADD_TO, BF.RENAME, BF.PIN_TO_START,
            BF.DELETE, BF.CHECK_ALL
        ])
        self.setToHideButtons(self.buttons[4:6])
        self.insertSeparator(1)


class PlaylistSelectionModeBar(SelectionModeBarBase):
    """ 播放列表界面选择模式栏 """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.addButtons([
            BF.CANCEL, BF.PLAY, BF.NEXT_TO_PLAY,
            BF.ADD_TO, BF.DELETE, BF.ALBUM,
            BF.MOVE_UP, BF.MOVE_DOWN, BF.EDIT_INFO,
            BF.PROPERTY, BF.CHECK_ALL
        ])
        self.setToHideButtons(self.buttons[5:-1])
        self.insertSeparator(1)


class SelectionModeBarType(Enum):
    """ 选择模式栏类型 """
    SONG_TAB = 0
    ALBUM_TAB = 1
    PLAYING = 2
    SINGER = 3
    ALBUM = 4
    PLAYLIST_CARD = 5
    PLAYLIST = 6


class SelectionModeBarFactory:
    """ 选择模式栏工厂 """

    @staticmethod
    def create(barType: SelectionModeBarType, parent=None) -> SelectionModeBarBase:
        """ 创建选择模式栏 """
        barMap = {
            SelectionModeBarType.SONG_TAB: SongTabSelectionModeBar,
            SelectionModeBarType.ALBUM_TAB: AlbumTabSelectionModeBar,
            SelectionModeBarType.PLAYING: PlayingSelectionModeBar,
            SelectionModeBarType.SINGER: SingerInterfaceSelectionModeBar,
            SelectionModeBarType.ALBUM: AlbumInterfaceSelectionModeBar,
            SelectionModeBarType.PLAYLIST_CARD: PlaylistCardSelectionModeBar,
            SelectionModeBarType.PLAYLIST: PlaylistSelectionModeBar,
        }

        if barType not in barMap:
            raise ValueError(f'{barType} 非法')

        return barMap[barType](parent)
