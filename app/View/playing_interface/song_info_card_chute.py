# coding:utf-8
from typing import List

from PyQt5.QtCore import (QDateTime, QEasingCurve, QParallelAnimationGroup,
                          QPoint, QPropertyAnimation, Qt, pyqtSignal)
from PyQt5.QtGui import QMouseEvent
from PyQt5.QtWidgets import QWidget

from .song_info_card import SongInfoCard


class SongInfoCardChute(QWidget):
    """ 歌曲信息滑动槽 """

    NO_LOOP = 0
    CYCLE_LEFT_SHIFT = 1
    CYCLE_RIGHT_SHIFT = 2

    showPlayBarSignal = pyqtSignal()
    hidePlayBarSignal = pyqtSignal()
    currentIndexChanged = pyqtSignal([int], [str])
    switchToAlbumInterfaceSig = pyqtSignal(str, str)

    def __init__(self, playlist: list = None, parent=None):
        """
        Parameters
        ----------
        playlist: list
            播放列表

        parent:
            父级窗口
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
        self.unFinishedAni_queque = []  # 未完成的动画队列

        # 创建歌曲信息卡
        for i in range(3):
            card = SongInfoCard(parent=self)
            self.cards.append(card)
            ani = QPropertyAnimation(card, b'pos', self)
            self.scrollAnis.append(ani)
            self.aniGroup.addAnimation(ani)
            card.setVisible(0 <= i-1 <= len(self.playlist)-1)
            if 0 <= i-1 <= len(self.playlist)-1:
                card.updateCard(self.playlist[i-1])

        # 初始化小部件
        self.__initWidget()

    def __initWidget(self):
        """ 初始化小部件 """
        self.resize(1200, 340)
        self.setAttribute(Qt.WA_TranslucentBackground)

        # 信号连接到槽
        self.aniGroup.finished.connect(self.__onScrollAniFinished)
        for card in self.cards:
            card.switchToAlbumInterfaceSig.connect(
                self.switchToAlbumInterfaceSig)
            card.hidePlayBarSignal.connect(self.__hidePlayBar)
            card.showPlayBarSignal.connect(self.__showPlayBar)

    def resizeEvent(self, e):
        for i, card in enumerate(self.cards):
            card.resize(self.width(), 136)
            card.move((i-1)*self.width(), self.height()-204)

    def mousePressEvent(self, e: QMouseEvent):
        """ 按钮按下时记录鼠标位置 """
        super().mousePressEvent(e)
        self.lastMousePosX = e.pos().x()
        self.mousePressedPosX = e.pos().x()
        self.mousePressedTime = QDateTime.currentDateTime().toMSecsSinceEpoch()

    def mouseMoveEvent(self, e: QMouseEvent):
        """ 鼠标按下可拖动歌曲信息卡 """
        for card in self.cards:
            card.move(card.x()-(self.lastMousePosX-e.pos().x()), card.y())

        self.lastMousePosX = e.pos().x()

    def mouseReleaseEvent(self, e: QMouseEvent):
        """ 鼠标松开时重新设置歌曲卡位置 """
        self.loopMode = self.NO_LOOP
        self.isAniTrigerredByMouse = True
        dt = QDateTime.currentDateTime().toMSecsSinceEpoch()-self.mousePressedTime

        # 记录下鼠标移动距离，self.mouseDeltaX > 0代表鼠标向右移动
        dx = self.mouseDeltaX = self.lastMousePosX-self.mousePressedPosX

        # 开始移动动画
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
        """ 恢复歌曲信息卡位置 """
        for i, (card, ani) in enumerate(zip(self.cards, self.scrollAnis)):
            self.__setAnimation(ani, card, (i-1)*self.width())
        self.aniGroup.start()

    def __cycleLeftShift(self):
        """ 歌曲信息卡循环左移 """
        self.loopMode = self.CYCLE_LEFT_SHIFT
        for i, (card, ani) in enumerate(zip(self.cards, self.scrollAnis)):
            self.__setAnimation(ani, card, (i-2)*self.width())
        self.aniGroup.start()

        # 发送更新背景信号
        self.currentIndexChanged[str].emit(self.cards[-1].albumCoverPath)

    def __cycleRightShift(self):
        """ 歌曲卡循环右移 """
        self.loopMode = self.CYCLE_RIGHT_SHIFT
        for i, (card, ani) in enumerate(zip(self.cards, self.scrollAnis)):
            self.__setAnimation(ani, card, i*self.width())

        self.aniGroup.start()

        # 发送更新背景信号
        self.currentIndexChanged[str].emit(self.cards[0].albumCoverPath)

    def __setAnimation(self, ani: QPropertyAnimation, card: SongInfoCard, endX: int):
        """ 设置动画 """
        ani.setDuration(500)
        ani.setTargetObject(card)
        ani.setEasingCurve(QEasingCurve.OutQuart)
        ani.setStartValue(card.pos())
        ani.setEndValue(QPoint(endX, card.y()))

    def __onScrollAniFinished(self):
        """ 滚动完成槽函数 """
        if self.loopMode == self.CYCLE_LEFT_SHIFT:
            # 将最左边的歌曲卡移动到最右边
            self.cards[0].move(self.width(), self.height()-204)

            # 交换歌曲信息卡列表元素位置
            self.cards[0], self.cards[1], self.cards[2] = self.cards[1], \
                self.cards[2], self.cards[0]

            # 更新歌曲信息卡
            self.__updateSongInfoCards()
            if self.isAniTrigerredByMouse:
                self.currentIndexChanged.emit(self.currentIndex)

        elif self.loopMode == self.CYCLE_RIGHT_SHIFT:
            # 将最右边的歌曲卡移动到最左边
            self.cards[2].move(-self.width(), self.height()-204)

            # 交换歌曲信息卡列表元素位置
            self.cards[0], self.cards[1], self.cards[2] = self.cards[2], \
                self.cards[0], self.cards[1]

            # 更新歌曲信息卡
            self.__updateSongInfoCards()
            if self.isAniTrigerredByMouse:
                self.currentIndexChanged.emit(self.currentIndex)

        # 完成未完成的动画，直接跳过中间的未完成动画以加快速度
        if self.unFinishedAni_queque:
            index = self.unFinishedAni_queque.pop()
            self.__cycleShift(index)
            self.unFinishedAni_queque.clear()

    def __updateSongInfoCards(self):
        """ 根据当前歌曲下标更新所有歌曲卡 """
        for i, card in enumerate(self.cards):
            isVisible = 0 <= self.currentIndex+i-1 < len(self.playlist)
            card.setVisible(isVisible)
            if isVisible:
                card.updateCard(self.playlist[self.currentIndex+i-1])

    def __hidePlayBar(self):
        """ 隐藏播放栏 """
        self.hidePlayBarSignal.emit()
        for card in self.cards:
            card.isPlayBarVisible = False

    def __showPlayBar(self):
        """ 显示播放栏 """
        self.showPlayBarSignal.emit()
        for card in self.cards:
            card.isPlayBarVisible = True

    def stopSongInfoCardTimer(self):
        """ 停止歌曲信息卡的计时器 """
        for card in self.cards:
            card.timer.stop()

    def startSongInfoCardTimer(self):
        """ 打开歌曲信息卡的计时器 """
        self.cards[1].timer.start()

    def setCurrentIndex(self, index: int):
        """ 设置当前下标 """
        self.isAniTrigerredByMouse = False
        if self.aniGroup.state() != QPropertyAnimation.Running:
            self.__cycleShift(index)
        else:
            self.unFinishedAni_queque.append(index)

    def setPlaylist(self, playlist: list, isResetIndex: bool, index=0):
        """ 设置播放列表 """
        self.playlist = playlist
        self.currentIndex = index if isResetIndex else self.currentIndex
        for i, card in enumerate(self.cards):
            isVisible = 0 <= self.currentIndex+i-1 <= len(self.playlist)-1
            card.setVisible(isVisible)
            if isVisible:
                card.updateCard(self.playlist[self.currentIndex+i-1])

    def __cycleShift(self, index):
        """ 循环移动 """
        if index > self.currentIndex:
            self.currentIndex = index
            self.cards[2].updateCard(self.playlist[index])
            self.__cycleLeftShift()
        elif index < self.currentIndex:
            self.currentIndex = index
            self.cards[0].updateCard(self.playlist[index])
            self.__cycleRightShift()
