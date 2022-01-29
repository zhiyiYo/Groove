# coding:utf-8
from typing import List

from common.database.entity import AlbumInfo
from common.library import Library
from components.album_card import (AlbumBlurBackground, AlbumCardType,
                                   HorizonAlbumCardView)
from PyQt5.QtCore import (QEasingCurve, QFile, QMargins,
                          QParallelAnimationGroup, QPoint, QPropertyAnimation,
                          QSize, Qt, pyqtSignal)
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import (QApplication, QGraphicsOpacityEffect, QPushButton,
                             QScrollArea, QToolButton, QWidget)


class AlbumGroupBox(QScrollArea):
    """ 专辑分组框 """

    playSig = pyqtSignal(list)
    nextToPlaySig = pyqtSignal(list)
    deleteAlbumSig = pyqtSignal(list)
    addAlbumToPlayingSig = pyqtSignal(list)
    switchToSingerInterfaceSig = pyqtSignal(str)
    switchToAlbumInterfaceSig = pyqtSignal(str, str)
    addAlbumToNewCustomPlaylistSig = pyqtSignal(list)
    addAlbumToCustomPlaylistSig = pyqtSignal(str, list)

    def __init__(self, library: Library, parent=None):
        super().__init__(parent=parent)
        self.library = library
        self.titleButton = QPushButton(self.tr('Albums'), self)
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

        self.albumInfos = []  # type:List[AlbumInfo]
        self.albumBlurBackground = AlbumBlurBackground(self)
        self.albumCardView = HorizonAlbumCardView(
            library,
            [],
            AlbumCardType.LOCAL_SEARCHED_ALBUM_CARD,
            margins=QMargins(35, 47, 65, 0),
            parent=self
        )
        self.albumCards = self.albumCardView.albumCards

        self.leftMask = QWidget(self)
        self.rightMask = QWidget(self)
        self.__initWidget()

    def __initWidget(self):
        """ 初始化小部件 """
        self.setFixedHeight(343)
        self.setWidget(self.albumCardView)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.scrollLeftButton.raise_()
        self.scrollRightButton.raise_()
        self.albumBlurBackground.lower()
        # self.hBox.setContentsMargins(35, 47, 65, 0)

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

        f = QFile(":/qss/album_group_box.qss")
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

    def __showBlurAlbumBackground(self, pos: QPoint, picPath: str):
        """ 显示磨砂背景 """
        # 将全局坐标转为窗口坐标
        pos = self.albumCardView.mapFromGlobal(pos)
        self.albumBlurBackground.setBlurAlbum(picPath)
        self.albumBlurBackground.move(pos.x() - 31, pos.y() - 16)
        self.albumBlurBackground.show()

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

    def deleteAlbums(self, albumNames: list):
        """ 删除专辑 """

    def deleteSongs(self, songPaths: list):
        """ 删除歌曲 """

    def updateWindow(self, albumInfos: list):
        """ 更新窗口 """
        if albumInfos == self.albumInfos:
            return

        # 显示遮罩
        self.horizontalScrollBar().setValue(0)
        self.leftMask.hide()
        self.rightMask.show()

        # 更新专辑卡
        self.albumInfos = albumInfos
        self.albumCardView.updateAllAlbumCards(albumInfos)

    def __onPlay(self, singer: str, album: str):
        """ 播放一张专辑 """
        albumInfo = self.library.albumInfoController.getAlbumInfo(
            singer, album)

        if not albumInfo:
            return

        self.playSig.emit(albumInfo.songInfos)

    def __connectSignalToSlot(self):
        """ 连接信号到槽函数 """
        self.horizontalScrollBar().valueChanged.connect(self.__onScrollHorizon)
        self.scrollLeftButton.clicked.connect(self.__onScrollLeftButtonClicked)
        self.scrollRightButton.clicked.connect(
            self.__onScrollRightButtonClicked)

        self.albumCardView.playSig.connect(self.__onPlay)
        self.albumCardView.nextPlaySig.connect(self.nextToPlaySig)
        self.albumCardView.addAlbumToPlayingSig.connect(
            self.addAlbumToPlayingSig)
        self.albumCardView.switchToSingerInterfaceSig.connect(
            self.switchToSingerInterfaceSig)
        self.albumCardView.switchToAlbumInterfaceSig.connect(
            self.switchToAlbumInterfaceSig)
        self.albumCardView.showBlurAlbumBackgroundSig.connect(
            self.__showBlurAlbumBackground)
        self.albumCardView.hideBlurAlbumBackgroundSig.connect(
            self.albumBlurBackground.hide)
        self.albumCardView.addAlbumToCustomPlaylistSig.connect(
            self.addAlbumToCustomPlaylistSig)
        self.albumCardView.addAlbumToNewCustomPlaylistSig.connect(
            self.addAlbumToNewCustomPlaylistSig)
