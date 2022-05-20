# coding:utf-8
from typing import List

from common.database.entity import SongInfo
from PyQt5.QtCore import (QDateTime, QEasingCurve, QParallelAnimationGroup,
                          QPoint, QPropertyAnimation, Qt, pyqtSignal)
from PyQt5.QtGui import QMouseEvent
from PyQt5.QtWidgets import QWidget

from .song_info_card import SongInfoCard


class SongInfoCardChute(QWidget):
    """ Song information card chute """

    NO_LOOP = 0
    CYCLE_LEFT_SHIFT = 1
    CYCLE_RIGHT_SHIFT = 2

    showPlayBarSignal = pyqtSignal()
    hidePlayBarSignal = pyqtSignal()
    currentIndexChanged = pyqtSignal([int], [str])
    aniFinished = pyqtSignal()

    def __init__(self, playlist: List[SongInfo] = None, parent=None):
        """
        Parameters
        ----------
        playlist: List[SongInfo]
            playing playlist

        parent:
            parent window
        """
        super().__init__(parent)
        self.playlist = playlist if playlist else []
        self.currentIndex = 0
        self.lastMousePosX = 0          # 鼠标移动位置
        self.mousePressedPosX = 0       # 鼠标按下的横坐标
        self.mousePressedTime = 0       # 鼠标按下的时刻
        self.cards = []                 # type:List[SongInfoCard]
        self.scrollAnis = []
        self.aniGroup = QParallelAnimationGroup(self)
        self.isAniTrigerredByMouse = False  # 滑动动画是否由鼠标触发
        self.unFinishedAnis = []            # 未完成的动画队列

        # create song information cards
        for i in range(3):
            card = SongInfoCard(parent=self)
            self.cards.append(card)
            ani = QPropertyAnimation(card, b'pos', self)
            self.scrollAnis.append(ani)
            self.aniGroup.addAnimation(ani)
            card.setVisible(0 <= i-1 <= len(self.playlist)-1)
            if 0 <= i-1 <= len(self.playlist)-1:
                card.updateCard(self.playlist[i-1])

        self.__initWidget()

    def __initWidget(self):
        """ initialize widgets """
        self.resize(1200, 340)
        self.setAttribute(Qt.WA_TranslucentBackground)

        # connect signal to slot
        self.aniGroup.finished.connect(self.__onScrollAniFinished)
        for card in self.cards:
            card.hidePlayBarSignal.connect(self.__hidePlayBar)
            card.showPlayBarSignal.connect(self.__showPlayBar)

    def resizeEvent(self, e):
        for i, card in enumerate(self.cards):
            card.resize(self.width(), 136)
            card.move((i-1)*self.width(), self.height()-204)

    def mousePressEvent(self, e: QMouseEvent):
        super().mousePressEvent(e)
        self.lastMousePosX = e.pos().x()
        self.mousePressedPosX = e.pos().x()
        self.mousePressedTime = QDateTime.currentDateTime().toMSecsSinceEpoch()

    def mouseMoveEvent(self, e: QMouseEvent):
        for card in self.cards:
            card.move(card.x()-(self.lastMousePosX-e.pos().x()), card.y())

        self.lastMousePosX = e.pos().x()

    def mouseReleaseEvent(self, e: QMouseEvent):
        self.loopMode = self.NO_LOOP
        self.isAniTrigerredByMouse = True
        dt = QDateTime.currentDateTime().toMSecsSinceEpoch()-self.mousePressedTime

        # record the mouse movement distance, dx > 0 represents the mouse move to the right
        dx = self.lastMousePosX - self.mousePressedPosX

        # start the shift animation
        n = len(self.playlist)
        index = self.currentIndex
        if 0 <= n <= 1 or (index == 0 and dx > 0) or (index == n-1 and dx < 0):
            self.__restoreCardPosition()
        elif n >= 2:
            if (dt < 360 and dx < -120) or dx < -self.width()/2:
                self.currentIndex += 1
                self.__cycleLeftShift()
            elif (dt < 360 and dx > 120) or dx > self.width()/2:
                self.currentIndex -= 1
                self.__cycleRightShift()
            else:
                self.__restoreCardPosition()

    def __restoreCardPosition(self):
        """ restore song information card position """
        for i, (card, ani) in enumerate(zip(self.cards, self.scrollAnis)):
            self.__setAnimation(ani, card, (i-1)*self.width())
        self.aniGroup.start()

    def __cycleLeftShift(self):
        """ cycle left shift song information card """
        self.loopMode = self.CYCLE_LEFT_SHIFT
        for i, (card, ani) in enumerate(zip(self.cards, self.scrollAnis)):
            self.__setAnimation(ani, card, (i-2)*self.width())
        self.aniGroup.start()

        # update album cover
        self.currentIndexChanged[str].emit(self.cards[-1].coverPath)

    def __cycleRightShift(self):
        """ cycle right shift song information card """
        self.loopMode = self.CYCLE_RIGHT_SHIFT
        for i, (card, ani) in enumerate(zip(self.cards, self.scrollAnis)):
            self.__setAnimation(ani, card, i*self.width())

        self.aniGroup.start()

        # update album cover
        self.currentIndexChanged[str].emit(self.cards[0].coverPath)

    def __setAnimation(self, ani: QPropertyAnimation, card: SongInfoCard, endX: int):
        """ set the config of animation """
        ani.setDuration(500)
        ani.setTargetObject(card)
        ani.setEasingCurve(QEasingCurve.OutQuart)
        ani.setStartValue(card.pos())
        ani.setEndValue(QPoint(endX, card.y()))

    def __onScrollAniFinished(self):
        """ animation finished slot """
        if self.loopMode == self.CYCLE_LEFT_SHIFT:
            # move the leftmost song card to the far right
            self.cards[0].move(self.width(), self.height()-204)

            # swap elements in song information card list
            self.cards[0], self.cards[1], self.cards[2] = self.cards[1], \
                self.cards[2], self.cards[0]

            # update cards
            self.__updateSongInfoCards()
            if self.isAniTrigerredByMouse:
                self.currentIndexChanged.emit(self.currentIndex)

        elif self.loopMode == self.CYCLE_RIGHT_SHIFT:
            # move the rightmost song card to the far left
            self.cards[2].move(-self.width(), self.height()-204)

            # swap elements in song information card list
            self.cards[0], self.cards[1], self.cards[2] = self.cards[2], \
                self.cards[0], self.cards[1]

            # update cards
            self.__updateSongInfoCards()
            if self.isAniTrigerredByMouse:
                self.currentIndexChanged.emit(self.currentIndex)

        # 完成未完成的动画，直接跳过中间的未完成动画以加快速度
        if self.unFinishedAnis:
            index = self.unFinishedAnis.pop()
            self.__cycleShift(index)
            self.unFinishedAnis.clear()

        self.aniFinished.emit()

    def __updateSongInfoCards(self):
        """ update song information cards """
        for i, card in enumerate(self.cards):
            isVisible = 0 <= self.currentIndex+i-1 < len(self.playlist)
            card.setVisible(isVisible)
            if isVisible:
                card.updateCard(self.playlist[self.currentIndex+i-1])

    def __hidePlayBar(self):
        """ hide play bar """
        self.hidePlayBarSignal.emit()
        for card in self.cards:
            card.isPlayBarVisible = False

    def __showPlayBar(self):
        """ show play bar """
        self.showPlayBarSignal.emit()
        for card in self.cards:
            card.isPlayBarVisible = True

    def stopSongInfoCardTimer(self):
        """ stop the song information card timer """
        for card in self.cards:
            card.timer.stop()

    def startSongInfoCardTimer(self):
        """ start the song information card timer """
        self.cards[1].timer.start()

    def setCurrentIndex(self, index: int):
        """ set currently played song """
        self.isAniTrigerredByMouse = False
        if self.aniGroup.state() != QPropertyAnimation.Running:
            self.__cycleShift(index)
        else:
            self.unFinishedAnis.append(index)

    def setPlaylist(self, playlist: List[SongInfo], isResetIndex: bool, index=0):
        """ set playing playlist """
        self.playlist = playlist
        self.currentIndex = index if isResetIndex else self.currentIndex
        for i, card in enumerate(self.cards):
            isVisible = 0 <= self.currentIndex+i-1 <= len(self.playlist)-1
            card.setVisible(isVisible)
            if isVisible:
                card.updateCard(self.playlist[self.currentIndex+i-1])

    def __cycleShift(self, index):
        """ cycle shift song information cards """
        if index > self.currentIndex:
            self.currentIndex = index
            self.cards[2].updateCard(self.playlist[index])
            self.__cycleLeftShift()
        elif index < self.currentIndex:
            self.currentIndex = index
            self.cards[0].updateCard(self.playlist[index])
            self.__cycleRightShift()
