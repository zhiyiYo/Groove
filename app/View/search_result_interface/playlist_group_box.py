# coding:utf-8
from typing import Dict, List

from common.database.entity import Playlist
from common.library import Library
from components.playlist_card import HorizonPlaylistCardView, PlaylistCardType
from PyQt5.QtCore import (QEasingCurve, QFile, QMargins,
                          QParallelAnimationGroup, QPropertyAnimation, QSize,
                          Qt, pyqtSignal)
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import (QGraphicsOpacityEffect, QPushButton, QScrollArea,
                             QToolButton, QWidget)


class PlaylistGroupBox(QScrollArea):
    """ 播放列表分组框 """

    def __init__(self, library: Library, parent=None):
        super().__init__(parent=parent)
        self.library = library
        self.playlists = []
        self.titleButton = QPushButton(self.tr('Playlists'), self)
        self.scrollRightButton = QToolButton(self)
        self.scrollLeftButton = QToolButton(self)
        self.opacityAniGroup = QParallelAnimationGroup(self)
        self.leftOpacityEffect = QGraphicsOpacityEffect(self)
        self.rightOpacityEffect = QGraphicsOpacityEffect(self)
        self.leftOpacityAni = QPropertyAnimation(
            self.leftOpacityEffect, b'opacity', self)
        self.rightOpacityAni = QPropertyAnimation(
            self.rightOpacityEffect, b'opacity', self)
        self.scrollAni = QPropertyAnimation(
            self.horizontalScrollBar(), b'value', self)

        self.playlistCardView = HorizonPlaylistCardView(
            library,
            self.playlists,
            PlaylistCardType.LOCAL_SEARCHED_PLAYLIST_CARD,
            margins=QMargins(35, 47, 65, 0),
            parent=self
        )
        self.playlistCards = self.playlistCardView.playlistCards

        self.leftMask = QWidget(self)
        self.rightMask = QWidget(self)
        self.__initWidget()

    def __initWidget(self):
        """ 初始化小部件 """
        self.setFixedHeight(343)
        self.setWidget(self.playlistCardView)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.scrollLeftButton.raise_()
        self.scrollRightButton.raise_()

        self.__setQss()

        self.titleButton.move(37, 0)
        self.leftMask.move(0, 47)
        self.leftMask.resize(35, 296)
        self.rightMask.resize(65, 296)
        self.scrollLeftButton.move(35, 42)

        self.scrollLeftButton.setFixedSize(25, 301)
        self.scrollRightButton.setFixedSize(25, 301)
        self.scrollLeftButton.setIconSize(QSize(15, 15))
        self.scrollRightButton.setIconSize(QSize(15, 15))
        self.scrollLeftButton.setIcon(
            QIcon(':/images/search_result_interface/ChevronLeft.png'))
        self.scrollRightButton.setIcon(
            QIcon(':/images/search_result_interface/ChevronRight.png'))
        self.scrollLeftButton.setGraphicsEffect(self.leftOpacityEffect)
        self.scrollRightButton.setGraphicsEffect(self.rightOpacityEffect)
        self.scrollLeftButton.hide()
        self.scrollRightButton.hide()
        self.leftMask.hide()
        self.resize(1200, 343)

        # 信号连接到槽
        self.__connectSignalToSlot()

    def __setQss(self):
        """ 设置层叠样式 """
        self.leftMask.setObjectName('leftMask')
        self.rightMask.setObjectName('rightMask')
        self.titleButton.setObjectName('titleButton')

        f = QFile(":/qss/playlist_group_box.qss")
        f.open(QFile.ReadOnly)
        self.setStyleSheet(str(f.readAll(), encoding='utf-8'))
        f.close()

        self.titleButton.adjustSize()

    def resizeEvent(self, e):
        self.rightMask.move(self.width()-65, 47)
        self.scrollRightButton.move(self.width()-90, 42)

    def __onScrollHorizon(self, value):
        """ 水平滚动槽函数 """
        self.leftMask.setHidden(value == 0)
        self.rightMask.setHidden(value == self.horizontalScrollBar().maximum())
        self.scrollLeftButton.setHidden(value == 0)
        self.scrollRightButton.setHidden(
            value == self.horizontalScrollBar().maximum())

    def __onScrollRightButtonClicked(self):
        """ 向右滚动按钮点击槽函数 """
        v = self.horizontalScrollBar().value()
        self.scrollAni.setStartValue(v)
        self.scrollAni.setEndValue(
            min(v+868, self.horizontalScrollBar().maximum()))
        self.scrollAni.setDuration(450)
        self.scrollAni.setEasingCurve(QEasingCurve.OutQuad)
        self.scrollAni.start()

    def __onScrollLeftButtonClicked(self):
        """ 向左滚动按钮点击槽函数 """
        v = self.horizontalScrollBar().value()
        self.scrollAni.setStartValue(v)
        self.scrollAni.setEndValue(max(v-868, 0))
        self.scrollAni.setDuration(450)
        self.scrollAni.setEasingCurve(QEasingCurve.OutQuad)
        self.scrollAni.start()

    def deleteSongs(self, songPaths: list):
        """ 从各个播放列表中删除歌曲 """

    def enterEvent(self, e):
        """ 进入窗口时显示滚动按钮 """
        if self.horizontalScrollBar().maximum() == 0:
            return

        # 移除之前的动画
        if self.opacityAniGroup.indexOfAnimation(self.leftOpacityAni) >= 0:
            self.opacityAniGroup.removeAnimation(self.leftOpacityAni)
        if self.opacityAniGroup.indexOfAnimation(self.rightOpacityAni) >= 0:
            self.opacityAniGroup.removeAnimation(self.rightOpacityAni)

        v = self.horizontalScrollBar().value()
        if v != 0:
            self.scrollLeftButton.show()
            self.leftOpacityAni.setStartValue(0)
            self.leftOpacityAni.setEndValue(1)
            self.leftOpacityAni.setDuration(200)
            self.opacityAniGroup.addAnimation(self.leftOpacityAni)

        if v != self.horizontalScrollBar().maximum():
            self.scrollRightButton.show()
            self.rightOpacityAni.setStartValue(0)
            self.rightOpacityAni.setEndValue(1)
            self.rightOpacityAni.setDuration(200)
            self.opacityAniGroup.addAnimation(self.rightOpacityAni)

        self.opacityAniGroup.start()

    def leaveEvent(self, e):
        """ 离开窗口是隐藏滚动按钮 """
        if self.horizontalScrollBar().maximum() == 0:
            return

        # 移除之前的动画
        if self.opacityAniGroup.indexOfAnimation(self.leftOpacityAni) >= 0:
            self.opacityAniGroup.removeAnimation(self.leftOpacityAni)
        if self.opacityAniGroup.indexOfAnimation(self.rightOpacityAni) >= 0:
            self.opacityAniGroup.removeAnimation(self.rightOpacityAni)

        if self.scrollLeftButton.isVisible():
            self.leftOpacityAni.setStartValue(1)
            self.leftOpacityAni.setEndValue(0)
            self.leftOpacityAni.setDuration(200)
            self.opacityAniGroup.addAnimation(self.leftOpacityAni)

        if self.scrollRightButton.isVisible():
            self.rightOpacityAni.setStartValue(1)
            self.rightOpacityAni.setEndValue(0)
            self.leftOpacityAni.setDuration(200)
            self.opacityAniGroup.addAnimation(self.rightOpacityAni)

        self.opacityAniGroup.start()

    def updateWindow(self, playlists: List[Playlist]):
        """ 更新窗口 """
        if playlists == self.playlists:
            return

        # 显示遮罩
        self.horizontalScrollBar().setValue(0)
        self.leftMask.hide()
        self.rightMask.show()

        # 更新播放列表卡
        self.playlists = playlists
        self.playlistCardView.updateAllCards(playlists)

    def __connectSignalToSlot(self):
        """ 信号连接到槽 """
        self.horizontalScrollBar().valueChanged.connect(self.__onScrollHorizon)
        self.scrollLeftButton.clicked.connect(self.__onScrollLeftButtonClicked)
        self.scrollRightButton.clicked.connect(
            self.__onScrollRightButtonClicked)

