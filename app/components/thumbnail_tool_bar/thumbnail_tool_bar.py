# coding:utf-8
from common.signal_bus import signalBus
from PyQt5.QtGui import QIcon
from PyQt5.QtWinExtras import QWinThumbnailToolBar, QWinThumbnailToolButton


class ThumbnailPlayButton(QWinThumbnailToolButton):
    """ Thumbnail play button"""

    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.setPlay(False)

    def setPlay(self, isPlay: bool):
        """ set play state """
        self.isPlaying = isPlay
        if self.isPlaying:
            self.setIcon(QIcon(":/images/thumbnail_tool_bar/播放_32_32_2.png"))
        else:
            self.setIcon(QIcon(":/images/thumbnail_tool_bar/暂停_32_32_2.png"))


class ThumbnailToolBar(QWinThumbnailToolBar):
    """ Thumbail tool bar """

    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.playButton = ThumbnailPlayButton(self)
        self.lastSongButton = QWinThumbnailToolButton(self)
        self.nextSongButton = QWinThumbnailToolButton(self)
        self.__initWidget()

    def __initWidget(self):
        """ initialize widgets """
        self.lastSongButton.setIcon(
            QIcon(":/images/thumbnail_tool_bar/上一首_32_32_2.png"))
        self.nextSongButton.setIcon(
            QIcon(":/images/thumbnail_tool_bar/下一首_32_32_2.png"))

        # add button to bar
        self.addButton(self.lastSongButton)
        self.addButton(self.playButton)
        self.addButton(self.nextSongButton)

        # connect signal to slot
        self.lastSongButton.clicked.connect(signalBus.lastSongSig)
        self.nextSongButton.clicked.connect(signalBus.nextSongSig)
        self.playButton.clicked.connect(signalBus.togglePlayStateSig)

    def setButtonsEnabled(self, isEnable: bool):
        """ set button enabled """
        for button in self.buttons():
            button.setEnabled(isEnable)

    def setPlay(self, isPlay: bool):
        """ set play state """
        self.playButton.setPlay(isPlay)