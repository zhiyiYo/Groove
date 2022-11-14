# coding:utf-8
from typing import List
from enum import Enum

from common.config import config
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QPen, QPainter, QColor
from PyQt5.QtWidgets import QWidget

from .button import SelectionModeBarButtonFactory as BF
from .button import Button


class SelectionModeBarBase(QWidget):
    """ Selection mode bar base class """

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
    downloadSig = pyqtSignal()
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
            'downloadButton': self.downloadSig,
            'checkAllButton': self.checkAllSig,
        }

    def addButton(self, button: int):
        """ add a button to bar """
        self.addButtons([button])

    def addSeparator(self):
        """ add a seperator to bar """
        if not self.buttons:
            return

        self.__separatorIndexes.append(len(self.buttons))

    def insertSeparator(self, index: int):
        """ insert a seperator to bar """
        if index < 1:
            return

        self.__separatorIndexes.append(index)
        self.__separatorIndexes.sort()

    def addButtons(self, buttons: List[int]):
        """ add multi buttons to bar

        Parameters
        ----------
        buttons: List[int]
            button type list
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
        """ set the buttons hidden when there is multiple selection """
        self.__buttonToHides = buttons
        self.__alwaysVisibleButtons = [
            i for i in self.buttons if i not in buttons]

    def setPartButtonHidden(self, isHidden: bool):
        """ set whether to hide part of buttons """
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
        """ adjust button position """
        for index, button in enumerate(self.__currentVisibleButtons[::-1]):
            rawIndex = self.buttons.index(button)
            isRightHasSeparator = (rawIndex + 1 in self.__separatorIndexes)
            button.move(self.width() - (index + 1) * button.width() -
                        41 * isRightHasSeparator, 0)

        # adjust bar height
        heights = [i.height() for i in self.__currentVisibleButtons]
        height = max(heights) if heights else 70
        self.resize(self.width(), height)

        self.update()

    def resizeEvent(self, e):
        self.__adjustButtonPos()

    def paintEvent(self, e):
        """ paint bar """
        painter = QPainter(self)
        bg = 37 if config.theme == 'dark' else 230
        painter.setPen(Qt.NoPen)
        painter.setBrush(QColor(bg, bg, bg))
        painter.drawRect(self.rect())
        painter.setPen(QPen(QColor(203, 203, 203)))
        for index in self.__separatorIndexes:
            x = self.buttons[index - 1].x(
            ) + self.buttons[index - 1].width() + 20
            painter.drawLine(x, 15, x + 1, self.height() - 15)


class SongTabSelectionModeBar(SelectionModeBarBase):
    """ Song tab interface selection mode bar """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.addButtons([
            BF.CANCEL, BF.PLAY, BF.NEXT_TO_PLAY,
            BF.ADD_TO, BF.ALBUM, BF.EDIT_INFO,
            BF.PROPERTY, BF.DELETE, BF.CHECK_ALL
        ])
        self.setToHideButtons(self.buttons[4:-2])
        self.insertSeparator(1)


class OnlineSongSelectionModeBar(SelectionModeBarBase):
    """ Online Song interface selection mode bar """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.addButtons([
            BF.CANCEL, BF.PLAY, BF.NEXT_TO_PLAY,
            BF.ADD_TO, BF.DOWNLOAD, BF.PROPERTY, BF.CHECK_ALL
        ])
        self.setToHideButtons([self.buttons[-2]])
        self.insertSeparator(1)


class SingerTabSelectionModeBar(SelectionModeBarBase):
    """ Singer tab interface selection mode bar """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.addButtons([
            BF.CANCEL, BF.PLAY, BF.NEXT_TO_PLAY,
            BF.ADD_TO, BF.PIN_TO_START, BF.CHECK_ALL
        ])
        self.setToHideButtons(self.buttons[4:5])
        self.insertSeparator(1)


class AlbumTabSelectionModeBar(SelectionModeBarBase):
    """ Album tab interface selection mode bar """

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
    """ Playing interface selection mode bar """

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
    """ Singer interface selection mode bar """

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
    """ Album interface selection mode bar """

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
    """ Playlist card interface selection mode bar """

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
    """ Playlist interface selection mode bar """

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
    """ Selection mode bar type """
    SONG_TAB = 0
    SINGER_TAB = 1
    ALBUM_TAB = 2
    PLAYING = 3
    SINGER = 4
    ALBUM = 5
    PLAYLIST_CARD = 6
    PLAYLIST = 7
    ONLINE_SONG = 8


class SelectionModeBarFactory:
    """ Selection mode bar type """

    @staticmethod
    def create(barType: SelectionModeBarType, parent=None) -> SelectionModeBarBase:
        """ create a selection mode bar """
        barMap = {
            SelectionModeBarType.SONG_TAB: SongTabSelectionModeBar,
            SelectionModeBarType.SINGER_TAB: SingerTabSelectionModeBar,
            SelectionModeBarType.ALBUM_TAB: AlbumTabSelectionModeBar,
            SelectionModeBarType.PLAYING: PlayingSelectionModeBar,
            SelectionModeBarType.SINGER: SingerInterfaceSelectionModeBar,
            SelectionModeBarType.ALBUM: AlbumInterfaceSelectionModeBar,
            SelectionModeBarType.PLAYLIST_CARD: PlaylistCardSelectionModeBar,
            SelectionModeBarType.PLAYLIST: PlaylistSelectionModeBar,
            SelectionModeBarType.ONLINE_SONG: OnlineSongSelectionModeBar,
        }

        if barType not in barMap:
            raise ValueError(f'Selection mode bar type `{barType}` is illegal')

        return barMap[barType](parent)
