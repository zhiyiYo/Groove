# coding:utf-8

import sys
from enum import Enum

from PyQt5.QtCore import (QEasingCurve, QParallelAnimationGroup, QPoint,
                          QPropertyAnimation, Qt, QRect, QDateTime)
from PyQt5.QtGui import QMouseEvent
from PyQt5.QtWidgets import QApplication, QWidget

from song_info_card import SongInfoCard


class SongInfoCardChute(QWidget):
    """ 
        歌曲卡滑槽，有三个歌曲卡在循环滑动，当前歌曲卡切换时就切换歌曲
        当前下标为0时，不能换到上一首， 当前下标为len-1时，不能换到下一首
    """

    def __init__(self, parent=None, playlist=None):
        super().__init__(parent)
        # 引用播放列表
        self.playlist = playlist
        self.currentIndex = 0
        self.songInfoCard_list = []
        # 初始化变量
        self.currentSongInfoCard = None
        self.lastSongInfoCard = None
        self.nextSongInfoCard = None
        # 创建并行动画组
        self.parallelAniGroup = QParallelAnimationGroup(self)
        self.curSongInfoCardAni = None
        self.lastSongInfoCardAni = None
        self.nextSongInfoCardAni = None
        self.__initWidget()
        self.now = QDateTime.currentDateTime().toMSecsSinceEpoch()

    def __initWidget(self):
        """ 初始化小部件 """
        self.resize(1300, 970)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.__createWidgets()
        for songInfoCard in self.songInfoCard_list:
            songInfoCard.resize(self.width(), 136)
        self.parallelAniGroup.finished.connect(self.switchSongInfoCard)

    def __createWidgets(self):
        """ 创建小部件 """
        # 创建三个歌曲信息卡，分别为last, current, next
        self.songInfoCard_list = [SongInfoCard(self) for i in range(3)]
        # 引用当前歌曲卡
        self.currentSongInfoCard = self.songInfoCard_list[1]
        # 创建动画
        self.songInfoCardAni_list = [QPropertyAnimation(
            self.songInfoCard_list[i], b'geometry') for i in range(3)]
        # 先隐藏所有歌曲信息卡
        for songInfoCard in self.songInfoCard_list:
            songInfoCard.hide()
        if not self.playlist:
            return
        else:

            self.currentSongInfoCard.updateCard(self.playlist[0])
            self.currentSongInfoCard.show()
            # 引用动画
            self.curSongInfoCardAni = self.songInfoCardAni_list[1]
            self.parallelAniGroup.addAnimation(self.curSongInfoCardAni)
            if len(self.playlist) >= 2:
                self.nextSongInfoCard = self.songInfoCard_list[2]
                self.nextSongInfoCard.show()
                self.nextSongInfoCard.updateCard(self.playlist[1])
                #self.nextSongInfoCard.move(0, self.height() - 204)
                # 引用动画
                self.nextSongInfoCardAni = self.songInfoCardAni_list[2]
                self.parallelAniGroup.addAnimation(self.nextSongInfoCardAni)
                if len(self.playlist) >= 3:
                    self.lastSongInfoCard = self.songInfoCard_list[0]
                    self.lastSongInfoCardAni = self.songInfoCardAni_list[0]

    def mousePressEvent(self, e: QMouseEvent):
        """ 按钮按下时记录鼠标位置 """
        self.mousePressPosX = e.pos().x()
        self.lastMousePosX = e.pos().x()
        # 记下按下的时间
        self.mousePressTime = QDateTime.currentDateTime().toMSecsSinceEpoch()

    def mouseMoveEvent(self, e: QMouseEvent):
        """ 鼠标按下可拖动歌曲信息卡 """
        for songInfoCard in self.songInfoCard_list:
            songInfoCard.move(songInfoCard.x(
            )-(self.lastMousePosX-e.pos().x()), songInfoCard.y())
        # 更新鼠标位置
        self.lastMousePosX = e.pos().x()

    def mouseReleaseEvent(self, e: QMouseEvent):
        """ 鼠标松开时重新设置歌曲卡位置 """
        # 记下松开的时间
        self.mouseReleaseTime = QDateTime.currentDateTime().toMSecsSinceEpoch()
        mouseDeltaTime = self.mouseReleaseTime - self.mousePressTime
        # self.mouseDeltaX > 0代表向右移动
        self.mouseDeltaX = self.lastMousePosX - self.mousePressPosX
        # 设置默认循环移位方式
        self.loopMode = SongInfoCardLoopMode.NO_LOOP

        if len(self.playlist) == 1:
            # 只有1个歌曲卡时不管移动距离是多少都把该歌曲卡放回原位
            self.__restoreCardPosition()
        # 播放列表长度为2
        elif len(self.playlist) == 2:
            if (self.currentIndex == 0 and self.mouseDeltaX > 0) or (self.currentIndex == len(self.playlist)-1 and self.mouseDeltaX < 0):
                self.__restoreCardPosition()
            else:
                if mouseDeltaTime < 1000 and abs(self.mouseDeltaX) >= 120:
                    self.__twoCardLoop()
                else:
                    # 移动距离小于窗口宽度1/2
                    if abs(self.mouseDeltaX) < int(self.width() / 2):
                        self.__restoreCardPosition()
                    # 移动距离超过窗口宽度的1/2或者鼠标移动速度够快时
                    else:
                        self.__twoCardLoop()
        # 播放列表长度大于等于3
        elif len(self.playlist) >= 3:
            # 下标为0时右移或者下标为len-1左移都恢复原状
            if (self.currentIndex == 0 and self.mouseDeltaX > 0) or (self.currentIndex == len(self.playlist)-1 and self.mouseDeltaX < 0):
                self.__restoreCardPosition()
            else:
                if mouseDeltaTime < 1000 and abs(self.mouseDeltaX) >= 120:
                    self.__threeCardLoop()
                else:
                    if abs(self.mouseDeltaX) < int(self.width() / 2):
                        self.__restoreCardPosition()
                    else:
                        self.__threeCardLoop()
        self.parallelAniGroup.start()

    def __setAnimation(self, animation: QPropertyAnimation, songInfoCard, endX):
        """ 设置动画 """
        animation.setEasingCurve(QEasingCurve.OutQuart)
        animation.setTargetObject(songInfoCard)
        animation.setDuration(500)
        # 设置起始值
        animation.setStartValue(QRect(songInfoCard.x(), songInfoCard.y(),
                                      songInfoCard.width(), songInfoCard.height()))
        # 设置结束值
        animation.setEndValue(
            QRect(endX, songInfoCard.y(), songInfoCard.width(), songInfoCard.height()))

    def resizeEvent(self, e):
        """ 改变窗口大小时也改变歌曲卡的大小 """
        for i in range(3):
            self.songInfoCard_list[i].resize(self.width(), 136)
            self.songInfoCard_list[i].move(
                (i - 1) * self.width(), self.height() - 204)

    def switchSongInfoCard(self):
        """ 交换歌曲卡的角色 """
        # 两卡片左移(播放下一首)
        if self.loopMode == SongInfoCardLoopMode.TWO_CARD_SHIFT_LEFT:
            self.currentSongInfoCard = self.songInfoCard_list[2]
            self.lastSongInfoCard = self.songInfoCard_list[1]
            self.nextSongInfoCard = None
            self.songInfoCard_list[0].hide()
            # 更新并行动画组
            self.lastSongInfoCardAni = self.songInfoCardAni_list[0]
            self.parallelAniGroup.addAnimation(self.lastSongInfoCardAni)
            self.parallelAniGroup.removeAnimation(self.nextSongInfoCardAni)
            # 更新下标
            self.currentIndex += 1

        # 两卡片右移(播放上一首)
        elif self.loopMode == SongInfoCardLoopMode.TWO_CARD_SHIFT_RIGHT:
            # 现在lastSongInfoCard = None
            self.currentSongInfoCard = self.songInfoCard_list[1]
            self.lastSongInfoCard = None
            self.nextSongInfoCard = self.songInfoCard_list[2]
            self.songInfoCard_list[0].hide()
            # 更新并行动画组
            self.parallelAniGroup.addAnimation(self.nextSongInfoCardAni)
            if self.lastSongInfoCardAni:
                self.parallelAniGroup.removeAnimation(self.lastSongInfoCardAni)
                self.lastSongInfoCardAni = None
            # 更新下标
            self.currentIndex -= 1

        # 三卡片循环左移
        elif self.loopMode == SongInfoCardLoopMode.THREE_CARD_SHIFT_LEFT:
            self.currentSongInfoCard = self.songInfoCard_list[2]
            self.lastSongInfoCard = self.songInfoCard_list[1]
            self.nextSongInfoCard = self.songInfoCard_list[0]
            # 如果当前下标为0就将lastSongInfoCardAni加到动画组中
            if self.currentIndex == 0:
                self.parallelAniGroup.addAnimation(self.lastSongInfoCardAni)
            # 更新下标
            self.currentIndex += 1
            self.nextSongInfoCard.show()

        # 三卡片循环右移
        elif self.loopMode == SongInfoCardLoopMode.THREE_CARD_SHIFT_RIGHT:
            self.currentSongInfoCard = self.songInfoCard_list[0]
            self.lastSongInfoCard = self.songInfoCard_list[2]
            self.nextSongInfoCard = self.songInfoCard_list[1]
            # 更新下标
            self.currentIndex -= 1
        # 更新歌曲信息卡
        if self.loopMode != SongInfoCardLoopMode.NO_LOOP:
            self.updateCards()

    def __twoCardLoop(self):
        """ 两卡片移动 """
        if self.mouseDeltaX > 0:
            print('右移')
            self.loopMode = SongInfoCardLoopMode.TWO_CARD_SHIFT_RIGHT
            # 播放播放列表的上一首歌
            self.__setAnimation(self.curSongInfoCardAni,
                                self.currentSongInfoCard, self.width())
            self.__setAnimation(self.lastSongInfoCardAni,
                                self.lastSongInfoCard, 0)
        else:
            print('左移')
            self.loopMode = SongInfoCardLoopMode.TWO_CARD_SHIFT_LEFT
            # 播放播放列表的下一首歌
            self.__setAnimation(self.curSongInfoCardAni,
                                self.currentSongInfoCard, -self.width())
            self.__setAnimation(self.nextSongInfoCardAni,
                                self.nextSongInfoCard, 0)

    def __threeCardLoop(self):
        """ 三卡片移动 """
        if self.mouseDeltaX > 0:
            # 播放播放列表的上一首
            self.loopMode = SongInfoCardLoopMode.THREE_CARD_SHIFT_RIGHT
            self.__setAnimation(self.curSongInfoCardAni,
                                self.currentSongInfoCard, self.width())
            self.__setAnimation(self.lastSongInfoCardAni,
                                self.lastSongInfoCard, 0)
            self.nextSongInfoCard.move(-self.width(),
                                       self.nextSongInfoCard.y())
        elif self.mouseDeltaX < 0:
            # 播放播放列表的下一首
            self.loopMode = SongInfoCardLoopMode.THREE_CARD_SHIFT_LEFT
            self.__setAnimation(self.curSongInfoCardAni,
                                self.currentSongInfoCard, -self.width())
            self.__setAnimation(self.nextSongInfoCardAni,
                                self.nextSongInfoCard, 0)
            self.lastSongInfoCard.move(self.width(),
                                       self.lastSongInfoCard.y())

    def __restoreCardPosition(self):
        """ 恢复卡片位置 """
        self.__setAnimation(self.curSongInfoCardAni,
                            self.currentSongInfoCard, 0)
        if self.nextSongInfoCard:
            self.__setAnimation(self.nextSongInfoCardAni,
                                self.nextSongInfoCard, self.width())
        if self.lastSongInfoCard:
            self.__setAnimation(self.lastSongInfoCardAni,
                                self.lastSongInfoCard, -self.width())

    def updateCards(self):
        """ 更新三个歌曲信息卡 """
        if self.currentSongInfoCard:
            self.currentSongInfoCard.updateCard(
                self.playlist[self.currentIndex])
        if self.lastSongInfoCard:
            self.lastSongInfoCard.updateCard(
                self.playlist[self.currentIndex - 1])
        if self.nextSongInfoCard:
            self.nextSongInfoCard.updateCard(
                self.playlist[self.currentIndex + 1])


class SongInfoCardLoopMode(Enum):
    """ 歌曲卡循环移位方式枚举类 """
    NO_LOOP = 0
    # last ← current, current ← next
    TWO_CARD_SHIFT_LEFT = 1
    # last → current,  current → next
    TWO_CARD_SHIFT_RIGHT = 2
    # 循环左移：last ← current ← next ← last
    THREE_CARD_SHIFT_LEFT = 3
    # 循环右移：next → last → current → next
    THREE_CARD_SHIFT_RIGHT = 4


if __name__ == "__main__":
    app = QApplication(sys.argv)
    playlist = [{'songName': 'ハッピーでバッドな眠りは浅い',
                 'songer': '鎖那',
                 'album': ['ハッピーでバッドな眠りは浅い']},
                {'songName': '猫じゃらし',
                 'songer': 'RADWIMPS',
                 'album': ['猫じゃらし - Single']},
                ]
    demo = SongInfoCardChute(playlist=playlist)
    demo.show()
    sys.exit(app.exec_())
