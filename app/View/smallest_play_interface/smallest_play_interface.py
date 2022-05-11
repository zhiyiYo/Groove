# coding:utf-8
from copy import deepcopy
from typing import List

from common.database.entity import SongInfo
from common.os_utils import getCoverPath
from common.signal_bus import signalBus
from components.buttons.circle_button import CircleButton
from components.frameless_window import FramelessWindow
from components.widgets.label import BlurCoverLabel
from PyQt5.QtCore import (QAbstractAnimation, QEasingCurve, QEvent, QFile,
                          QParallelAnimationGroup, QPoint, QPropertyAnimation,
                          QRect, Qt, pyqtSignal)
from PyQt5.QtGui import QFont, QFontMetrics
from PyQt5.QtWidgets import QGraphicsOpacityEffect, QLabel, QSlider, QWidget

from .buttons import PlayButton, SmallestPlayModeButton
from .title_bar import TitleBar


class SmallestPlayInterface(FramelessWindow):
    """ Smallest play interface """

    CYCLE_LEFT_SHIFT = 0
    CYCLE_RIGHT_SHIFT = 1
    exitSmallestPlayInterfaceSig = pyqtSignal()

    def __init__(self, playlist: List[SongInfo] = None, parent=None):
        super().__init__(parent)
        self.playlist = playlist if playlist else []
        self.currentIndex = 0
        self.shiftLeftTime = 0
        self.shiftRightTime = 0
        self.cards = []
        self.__unCompleteShift_list = []
        self.albumCoverLabel = BlurCoverLabel(35, (350, 350), self)

        self.playButton = PlayButton(self)
        self.lastSongButton = SmallestPlayModeButton(
            ":/images/smallest_play_interface/Previous.png", self)
        self.nextSongButton = SmallestPlayModeButton(
            ":/images/smallest_play_interface/Next.png", self)
        self.exitButton = CircleButton(
            ":/images/playing_interface/SmallestPlayMode.png", self)
        self.progressBar = QSlider(Qt.Horizontal, self)
        self.aniGroup = QParallelAnimationGroup(self)
        self.titleBar = TitleBar(self)

        self.__createSongInfoCards()
        self.__initWidget()

    def __initWidget(self):
        """ initialize widgets """
        self.resize(350, 350)
        self.setMinimumSize(206, 197)
        self.setWindowFlags(self.windowFlags() | Qt.Window)
        self.windowEffect.addMenuShadowEffect(int(self.winId()))
        self.albumCoverLabel.setScaledContents(True)
        self.progressBar.installEventFilter(self)
        self.__setQss()
        self.exitButton.setToolTip(self.tr('Exit smallest mode'))

        # connect signal to slot
        self.aniGroup.finished.connect(self.__switchSongInfoCard)
        self.lastSongButton.clicked.connect(signalBus.lastSongSig)
        self.nextSongButton.clicked.connect(signalBus.nextSongSig)
        self.playButton.clicked.connect(signalBus.togglePlayStateSig)
        self.titleBar.closeButton.clicked.connect(self.hide)
        self.exitButton.clicked.connect(
            self.exitSmallestPlayInterfaceSig)

    def __createSongInfoCards(self):
        """ 创建歌曲信息卡 """
        # create three song information cards: last, current, next
        self.cards = [SongInfoCard(parent=self) for i in range(3)]

        self.lastCard = self.cards[0]  # type:SongInfoCard
        self.currentCard = self.cards[1]  # type:SongInfoCard
        self.nextCard = self.cards[2]  # type:SongInfoCard

        # create animations
        self.cardAnis = [
            QPropertyAnimation(self.cards[i], b"pos") for i in range(3)]
        self.lastCardAni = self.cardAnis[0]
        self.currentCardAni = self.cardAnis[1]
        self.nextCardAni = self.cardAnis[2]

        for ani in self.cardAnis:
            self.aniGroup.addAnimation(ani)

        for i in range(3):
            self.cards[i].move((i - 1) * self.width(), self.height() - 106)

        if self.playlist:
            self.currentCard.updateCard(self.playlist[0])
            if len(self.playlist) >= 2:
                self.nextCard.updateCard(self.playlist[1])

    def resizeEvent(self, e):
        self.resize(self.size())
        self.albumCoverLabel.resize(self.size())
        self.progressBar.resize(self.width(), 5)
        self.progressBar.move(0, self.height() - 5)
        self.titleBar.resize(self.width(), self.titleBar.height())
        self.exitButton.move(
            self.width() - 7 - self.exitButton.width(),
            self.height() - 7 - self.exitButton.height(),
        )
        self.playButton.move(
            int(self.width() / 2 - self.playButton.width() / 2),
            int(self.height() / 2 - self.playButton.height() / 2),
        )
        self.lastSongButton.move(self.playButton.x() - 75, self.playButton.y())
        self.nextSongButton.move(self.playButton.x() + 75, self.playButton.y())

        for i in range(3):
            self.cards[i].resize(self.width(), self.cards[i].height())

        self.currentCard.move(0, self.height() - 106)
        self.lastCard.move(-self.width(), self.height() - 106)
        self.nextCard.move(self.width(), self.height() - 106)

        # hide cards if the height is too small
        if self.height() <= 320:
            if self.currentCard.isVisible():
                self.currentCard.aniHide()
            self.lastCard.hide()
            self.nextCard.hide()
        elif self.height() > 320:
            if not self.currentCard.isVisible():
                self.currentCard.aniShow()
            else:
                self.currentCard.show()
            self.lastCard.show()
            self.nextCard.show()

    def __setQss(self):
        """ set style sheet """
        f = QFile(":/qss/smallest_play_interface.qss")
        f.open(QFile.ReadOnly)
        self.setStyleSheet(str(f.readAll(), encoding='utf-8'))
        f.close()

    def eventFilter(self, obj, e: QEvent):
        """ 过滤事件 """
        if obj == self.progressBar:
            if e.type() in [QEvent.MouseButtonPress, QEvent.MouseButtonDblClick]:
                return True
        return super().eventFilter(obj, e)

    def __cycleLeftShift(self):
        """ cycle left shift cards """
        self.loopMode = self.CYCLE_LEFT_SHIFT
        self.__setAnimation(
            self.currentCardAni, self.currentCard, -self.width())
        self.__setAnimation(self.nextCardAni, self.nextCard, 0)
        self.aniGroup.removeAnimation(self.lastCardAni)
        self.aniGroup.start()

    def __cycleRightShift(self):
        """ 循环右移 """
        self.loopMode = self.CYCLE_RIGHT_SHIFT
        self.__setAnimation(self.currentCardAni,
                            self.currentCard, self.width())
        self.__setAnimation(self.lastCardAni, self.lastCard, 0)
        self.aniGroup.removeAnimation(self.nextCardAni)
        self.aniGroup.start()

    def __setAnimation(self, animation: QPropertyAnimation, songInfoCard, endX):
        """ cycle right shift cards """
        animation.setEasingCurve(QEasingCurve.OutQuart)
        animation.setTargetObject(songInfoCard)
        animation.setDuration(500)
        animation.setStartValue(songInfoCard.pos())
        animation.setEndValue(QPoint(endX, songInfoCard.y()))

    def __switchSongInfoCard(self):
        """ switch the reference of cards """
        if self.loopMode == self.CYCLE_LEFT_SHIFT:
            self.__resetRef(moveDirection=0)
            self.aniGroup.addAnimation(self.lastCardAni)

            # move cards
            self.cards[[2, 0, 1][self.shiftLeftTime]].move(
                self.width(), self.height() - 106)

            self.currentIndex += 1
            if self.currentIndex != len(self.playlist) - 1:
                self.updateCards()

        elif self.loopMode == self.CYCLE_RIGHT_SHIFT:
            self.__resetRef(moveDirection=1)
            self.aniGroup.addAnimation(self.nextCardAni)

            # move cards
            self.cards[[0, 2, 1][self.shiftRightTime]].move(
                -self.width(), self.height() - 106)

            self.currentIndex -= 1
            if self.currentIndex != 0:
                self.updateCards()

        if self.__unCompleteShift_list:
            index = self.__unCompleteShift_list.pop(0)
            self.__completeShift(index)

    def updateCards(self):
        """ update song information cards """
        self.currentCard.updateCard(self.playlist[self.currentIndex])
        if self.currentIndex >= 1:
            self.lastCard.updateCard(
                self.playlist[self.currentIndex - 1])
        if self.currentIndex <= len(self.playlist) - 2:
            self.nextCard.updateCard(
                self.playlist[self.currentIndex + 1])

    def __resetRef(self, moveDirection=0):
        """ reset the reference to cards

        Parameters
        ----------
        moveDirection: int
            move direction of cards, including:
            * `0`: left shift
            * `1`: right shift
        """
        if moveDirection == 0:
            self.shiftLeftTime = (self.shiftLeftTime + 1) % 3
            self.shiftRightTime = (self.shiftRightTime - 1) % 3
            if self.shiftLeftTime == 0:
                self.__resetRefIndex(0, 1, 2)
            elif self.shiftLeftTime == 1:
                self.__resetRefIndex(1, 2, 0)
            elif self.shiftLeftTime == 2:
                self.__resetRefIndex(2, 0, 1)
        elif moveDirection == 1:
            self.shiftLeftTime = (self.shiftLeftTime - 1) % 3
            self.shiftRightTime = (self.shiftRightTime + 1) % 3
            if self.shiftRightTime == 0:
                self.__resetRefIndex(0, 1, 2)
            elif self.shiftRightTime == 1:
                self.__resetRefIndex(2, 0, 1)
            elif self.shiftRightTime == 2:
                self.__resetRefIndex(1, 2, 0)

    def __resetRefIndex(self, lastIndex, curIndex, nextIndex):
        self.currentCard = self.cards[curIndex]
        self.lastCard = self.cards[lastIndex]
        self.nextCard = self.cards[nextIndex]

    def setCurrentIndex(self, index):
        """ set currently played song """
        if not self.playlist:
            return

        if self.aniGroup.state() != QAbstractAnimation.Running:
            songInfo = self.playlist[index]
            coverPath = getCoverPath(
                songInfo.singer, songInfo.album, "album_big")
            self.albumCoverLabel.setCover(coverPath)
            self.__completeShift(index)
        else:
            self.__unCompleteShift_list.append(index)

    def setPlaylist(self, playlist: list, isResetIndex: bool = True):
        """ set playlist

        Parameters
        ----------
        playlist: list
            playing playlist

        isResetIndex: bool
            whether to reset index to 0
        """
        self.playlist = playlist.copy() if playlist else []
        self.currentIndex = 0 if isResetIndex else self.currentIndex
        if playlist:
            self.currentCard.updateCard(self.playlist[0])
            self.currentCard.show()
            if len(self.playlist) > 1:
                self.nextCard.updateCard(self.playlist[1])
        else:
            self.currentCard.hide()

    def setPlay(self, isPlay: bool):
        """ set play state """
        self.playButton.setPlay(isPlay)

    def clearPlaylist(self):
        """ clear playlist """
        self.playlist.clear()

    def __completeShift(self, index):
        """ complete the shift of cards """
        if index > self.currentIndex:
            self.currentIndex = index - 1
            self.nextCard.updateCard(self.playlist[index])
            self.__cycleLeftShift()
        elif index < self.currentIndex:
            self.currentIndex = index + 1
            self.lastCard.updateCard(self.playlist[index])
            self.__cycleRightShift()


class SongInfoCard(QWidget):
    """ Song information card """

    def __init__(self, songInfo: SongInfo = None, parent=None):
        super().__init__(parent)
        self.resize(320, 55)
        self.songNameLabel = QLabel(self)
        self.singerNameLabel = QLabel(self)
        self.opacityEffect = QGraphicsOpacityEffect(self)
        self.ani = QPropertyAnimation(self.opacityEffect, b"opacity")
        self.__initWidget()
        self.updateCard(songInfo)

    def __initWidget(self):
        """ initialize widgets """
        self.setFixedHeight(55)
        self.opacityEffect.setOpacity(1)
        self.setGraphicsEffect(self.opacityEffect)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.songNameLabel.setObjectName("songNameLabel")
        self.singerNameLabel.setObjectName("singerNameLabel")

    def __setSongInfo(self, songInfo: SongInfo):
        """ set song information """
        songInfo = SongInfo() if songInfo is None else songInfo
        self.songName = songInfo.title or ''
        self.singerName = songInfo.singer or ''
        self.songNameLabel.setText(self.songName)
        self.singerNameLabel.setText(self.singerName)

    def updateCard(self, songInfo: SongInfo):
        """ update song information card """
        self.__setSongInfo(songInfo)
        self.__adjustLabel()

    def __adjustLabel(self):
        """ adjust the text of label """
        fontMetrics = QFontMetrics(QFont("Microsoft YaHei", 12, 75))

        maxWidth = self.width() - 30
        songNameWidth, singerNameWidth = 0, 0

        # adjust song name
        for index, char in enumerate(self.songName):
            if songNameWidth + fontMetrics.width(char) > maxWidth:
                self.songNameLabel.setText(self.songName[:index])
                break

            songNameWidth += fontMetrics.width(char)

        self.songNameLabel.setFixedWidth(songNameWidth)

        # adjust singer name
        fontMetrics = QFontMetrics(QFont("Microsoft YaHei", 11))
        for index, char in enumerate(self.singerName):
            if singerNameWidth + fontMetrics.width(char) > maxWidth:
                self.singerNameLabel.setText(self.singerName[:index])
                break

            singerNameWidth += fontMetrics.width(char)

        self.singerNameLabel.setFixedWidth(singerNameWidth)

        # adjust label position
        self.songNameLabel.move(int(self.width() / 2 - songNameWidth / 2), 0)
        self.singerNameLabel.move(
            int(self.width() / 2 - singerNameWidth / 2), 30)

    def resizeEvent(self, e):
        super().resizeEvent(e)
        self.__adjustLabel()

    def aniHide(self):
        """ fade out """
        self.ani.setStartValue(1)
        self.ani.setEndValue(0)
        self.ani.setDuration(150)
        self.ani.finished.connect(self.__hideAniSlot)
        self.ani.start()

    def aniShow(self):
        """ fade in """
        super().show()
        self.ani.setStartValue(0)
        self.ani.setEndValue(1)
        self.ani.setDuration(150)
        self.ani.start()

    def __hideAniSlot(self):
        self.ani.disconnect()
        super().hide()
