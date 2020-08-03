# coding:utf-8
from random import shuffle

import sys
from json import load
from PyQt5.QtCore import (QEasingCurve, QParallelAnimationGroup, QAbstractAnimation,
                          QPropertyAnimation, QRect, Qt, QTimer, pyqtSignal)
from PyQt5.QtGui import QPixmap, QMouseEvent
from PyQt5.QtWidgets import QApplication, QGraphicsBlurEffect, QLabel, QWidget

from .blur_cover_thread import BlurCoverThread
from .play_bar import PlayBar

from .song_info_card_chute import SongInfoCardChute
from .song_list_widget import SongListWidget
from .create_song_cards_thread import CreateSongCardsThread
from my_widget.my_button import ThreeStateButton


class PlayingInterface(QWidget):
    """ 正在播放界面 """
    currentIndexChanged = pyqtSignal(int)
    removeMediaSignal = pyqtSignal(int)
    randomPlayAllSignal = pyqtSignal()

    def __init__(self, playlist: list = None, parent=None):
        super().__init__(parent)
        self.playlist = playlist.copy()
        self.currentIndex = 0
        self.isPlaylistVisible = False
        # 创建小部件
        self.blurPixmap = None
        self.blurBackgroundPic = QLabel(self)
        self.blurCoverThread = BlurCoverThread(self)
        self.songInfoCardChute = SongInfoCardChute(self, self.playlist)
        self.parallelAniGroup = QParallelAnimationGroup(self)
        self.songInfoCardChuteAni = QPropertyAnimation(
            self.songInfoCardChute, b'geometry')
        self.playBar = PlayBar(self)
        self.songListWidget = SongListWidget(self.playlist, self)
        self.playBarAni = QPropertyAnimation(self.playBar, b'geometry')
        self.songListWidgetAni = QPropertyAnimation(
            self.songListWidget, b'geometry')
        self.guideLabel = QLabel('在这里，你将看到正在播放的歌曲以及即将播放的歌曲。', self)
        self.randomPlayAllButton = ThreeStateButton(
            {'normal': r'resource\images\playing_interface\全部随机播放_normal_256_39.png',
             'hover': r'resource\images\playing_interface\全部随机播放_hover_256_39.png',
             'pressed': r'resource\images\playing_interface\全部随机播放_pressed_256_39.png'}, self, (256, 39))
        # 实例化创建歌曲卡线程
        self.createSongCardThread = CreateSongCardsThread(
            self.songListWidget, self)
        # 创建定时器
        self.showPlaylistTimer = QTimer(self)
        self.hidePlaylistTimer = QTimer(self)
        # 初始化
        self.__initWidget()

    def __initWidget(self):
        """ 初始化小部件 """
        self.resize(1100, 870)
        self.setAttribute(Qt.WA_StyledBackground)
        self.guideLabel.move(45, 62)
        self.randomPlayAllButton.move(45, 117)
        self.playBar.move(0, self.height()-self.playBar.height())
        self.randomPlayAllButton.hide()
        self.guideLabel.hide()
        self.playBar.hide()
        # 设置层叠样式
        self.setObjectName('playingInterface')
        self.guideLabel.setObjectName('guideLabel')
        self.__setQss()
        # 开启磨砂线程
        if self.playlist:
            self.startBlurThread(
                self.songInfoCardChute.curSongInfoCard.albumCoverPath)
        # 将信号连接到槽
        self.__connectSignalToSlot()
        # 初始化动画
        self.playBarAni.setDuration(500)
        self.songListWidgetAni.setDuration(300)
        self.songListWidgetAni.setEasingCurve(QEasingCurve.InQuad)
        self.playBarAni.setEasingCurve(QEasingCurve.InExpo)
        self.parallelAniGroup.addAnimation(self.playBarAni)
        self.parallelAniGroup.addAnimation(self.songInfoCardChuteAni)
        # 初始化定时器
        self.showPlaylistTimer.setInterval(400)
        self.hidePlaylistTimer.setInterval(50)
        self.showPlaylistTimer.timeout.connect(self.showPlayListTimerSlot)
        self.hidePlaylistTimer.timeout.connect(self.hidePlayListTimerSlot)
        

    def __setQss(self):
        """ 设置层叠样式 """
        with open(r'resource\css\playInterface.qss', encoding='utf-8') as f:
            self.setStyleSheet(f.read())

    def setBlurPixmap(self, blurPixmap):
        """ 设置磨砂pixmap """
        self.blurPixmap = blurPixmap
        # 更新背景
        self.__resizeBlurPixmap()

    def __resizeBlurPixmap(self):
        """ 调整背景图尺寸 """
        maxWidth = max(self.width(), self.height())
        if self.blurPixmap:
            self.blurBackgroundPic.setPixmap(self.blurPixmap.scaled(
                maxWidth, maxWidth, Qt.KeepAspectRatioByExpanding, Qt.SmoothTransformation))

    def startBlurThread(self, albumCoverPath):
        """ 开启磨砂线程 """
        self.blurCoverThread.setTargetCover(albumCoverPath)
        self.blurCoverThread.start()

    def mousePressEvent(self, e: QMouseEvent):
        """ 鼠标点击界面其他位置时隐藏音量条 """
        condX = 166 < e.pos().x() <= self.playBar.volumeSlider.width() + 166
        condY = self.playBar.y() <= e.pos().y() <= self.playBar.y() + \
            self.playBar.volumeSlider.height()
        if not (condX and condY):
            self.playBar.volumeSlider.hide()

    def resizeEvent(self, e):
        """ 改变尺寸时也改变小部件的大小 """
        super().resizeEvent(e)
        self.__resizeBlurPixmap()
        self.songInfoCardChute.resize(self.size())
        self.blurBackgroundPic.setFixedSize(self.size())
        self.playBar.resize(self.width(), self.playBar.height())
        self.songListWidget.resize(self.width()-60, self.height()-382)
        if self.isPlaylistVisible:
            self.playBar.move(0, 190)
            self.songListWidget.move(30, 382)
            self.songInfoCardChute.move(0, 258 - self.height())
        else:
            self.playBar.move(0, self.height() - self.playBar.height())
            self.songListWidget.move(30, self.height())

    def showPlayBar(self):
        """ 显示播放栏 """
        # 只在播放栏不可见的时候显示播放栏和开启动画
        if not self.playBar.isVisible():
            self.playBar.show()
            self.songInfoCardChuteAni.setDuration(450)
            self.songInfoCardChuteAni.setEasingCurve(QEasingCurve.OutCubic)
            self.songInfoCardChuteAni.setStartValue(
                self.songInfoCardChute.rect())
            self.songInfoCardChuteAni.setEndValue(
                QRect(0, -self.playBar.height()+68, self.width(), self.height()))
            self.songInfoCardChuteAni.start()

    def hidePlayBar(self):
        """ 隐藏播放栏 """
        if self.playBar.isVisible() and not self.isPlaylistVisible:
            self.playBar.hide()
            self.songInfoCardChuteAni.setStartValue(
                QRect(0, -self.playBar.height()+68, self.width(), self.height()))
            self.songInfoCardChuteAni.setEndValue(
                QRect(0, 0, self.width(), self.height()))
            self.songInfoCardChuteAni.start()

    def showPlaylist(self):
        """ 显示播放列表 """
        if self.songListWidgetAni.state() != QAbstractAnimation.Running:
            self.songInfoCardChuteAni.setDuration(500)
            self.songInfoCardChuteAni.setEasingCurve(QEasingCurve.InExpo)
            self.songInfoCardChuteAni.setStartValue(
                QRect(0, self.songInfoCardChute.y(), self.width(), self.height()))
            self.songInfoCardChuteAni.setEndValue(
                QRect(0, 258 - self.height(), self.width(), self.height()))
            self.playBarAni.setStartValue(
                QRect(0, self.height()-self.playBar.height(), self.width(), self.playBar.height()))
            self.playBarAni.setEndValue(
                QRect(0, 190, self.width(), self.playBar.height()))
            self.songListWidgetAni.setStartValue(
                QRect(self.songListWidget.x(), self.songListWidget.y(),
                      self.songListWidget.width(), self.songListWidget.height()))
            self.songListWidgetAni.setEndValue(
                QRect(self.songListWidget.x(), 382,
                      self.songListWidget.width(), self.songListWidget.height()))
            if self.sender() == self.playBar.showPlaylistButton:
                self.playBar.pullUpArrowButton.timer.start()
            self.parallelAniGroup.start()
            self.blurBackgroundPic.hide()
            self.isPlaylistVisible = True
            self.showPlaylistTimer.start()

    def showPlayListTimerSlot(self):
        """ 显示播放列表定时器溢出槽函数 """
        self.showPlaylistTimer.stop()
        self.songListWidgetAni.start()

    def hidePlayListTimerSlot(self):
        """ 显示播放列表定时器溢出槽函数 """
        self.hidePlaylistTimer.stop()
        self.parallelAniGroup.start()

    def hidePlaylist(self):
        """ 隐藏播放列表 """
        if self.parallelAniGroup.state() != QAbstractAnimation.Running:
            self.songInfoCardChuteAni.setDuration(500)
            self.songInfoCardChuteAni.setEasingCurve(QEasingCurve.InExpo)
            self.songInfoCardChuteAni.setStartValue(
                QRect(0, self.songInfoCardChute.y(), self.width(), self.height()))
            self.songInfoCardChuteAni.setEndValue(
                QRect(0, -self.playBar.height() + 68, self.width(), self.height()))
            self.playBarAni.setStartValue(
                QRect(0, 190, self.width(), self.playBar.height()))
            self.playBarAni.setEndValue(
                QRect(0, self.height() - self.playBar.height(), self.width(), self.playBar.height()))
            self.songListWidgetAni.setStartValue(
                QRect(self.songListWidget.x(), self.songListWidget.y(),
                      self.songListWidget.width(), self.songListWidget.height()))
            self.songListWidgetAni.setEndValue(
                QRect(self.songListWidget.x(), self.height(),
                      self.songListWidget.width(), self.songListWidget.height()))
            if self.sender() == self.playBar.showPlaylistButton:
                self.playBar.pullUpArrowButton.timer.start()
            # self.parallelAniGroup.start()
            self.songListWidgetAni.start()
            self.hidePlaylistTimer.start()
            self.blurBackgroundPic.show()
            self.isPlaylistVisible = False

    def showPlaylistButtonSlot(self):
        """ 显示或隐藏播放列表 """
        if not self.isPlaylistVisible:
            self.showPlaylist()
        else:
            self.hidePlaylist()

    def setCurrentIndex(self, index):
        """ 更新播放列表下标 """
        if self.currentIndex != index:
            # 在播放列表的最后一首歌被移除时不更新样式
            if index >= len(self.playlist):
                return
            self.currentIndex = index
            self.songListWidget.setCurrentIndex(index)
            self.songInfoCardChute.setCurrentIndex(index)

    def setPlaylist(self, playlist: list):
        """ 更新播放列表 """
        self.playlist = playlist.copy()
        self.currentIndex = 0
        if playlist:
            self.songInfoCardChute.setPlaylist(self.playlist)
            self.createSongCardThread.setPlaylist(self.playlist)
            self.createSongCardThread.run()
        # 如果小部件不可见就显示
        if playlist and not self.songListWidget.isVisible():
            self.songInfoCardChute.show()
            self.playBar.show()
            self.songListWidget.show()
            self.randomPlayAllButton.hide()
            self.guideLabel.hide()

    def __settleDownPlayBar(self):
        """ 定住播放栏 """
        self.songInfoCardChute.stopSongInfoCardTimer()

    def __startSongInfoCardTimer(self):
        """ 重新打开歌曲信息卡的定时器 """
        if not self.playBar.volumeSlider.isVisible():
            # 只有音量滑动条不可见才打开计时器
            self.songInfoCardChute.startSongInfoCardTimer()

    def __songListWidgetCurrentChangedSlot(self, index):
        """ 歌曲列表当前下标改变插槽 """
        self.currentIndex = index
        self.songInfoCardChute.setCurrentIndex(index)
        self.currentIndexChanged.emit(index)

    def __songInfoCardChuteCurrentChangedSlot(self, index):
        """ 歌曲列表当前下标改变插槽 """
        self.currentIndex = index
        self.songListWidget.setCurrentIndex(index)
        self.currentIndexChanged.emit(index)

    def __removeSongFromPlaylist(self, index):
        """ 从播放列表中移除选中的歌曲 """
        lastSongRemoved = False
        if self.currentIndex > index:
            self.currentIndex -= 1
            self.songInfoCardChute.currentIndex -= 1
        elif self.currentIndex == index:
            # 如果被移除的是最后一首需要将当前下标-1
            if index == self.songListWidget.currentIndex + 1:
                self.currentIndex -= 1
                self.songInfoCardChute.currentIndex -= 1
                lastSongRemoved = True
            else:
                self.songInfoCardChute.setCurrentIndex(self.currentIndex)
        self.removeMediaSignal.emit(index)
        # 如果播放列表为空，隐藏小部件
        if len(self.playlist) == 0:
            self.playBar.hide()
            self.songInfoCardChute.hide()
            self.songListWidget.hide()
            self.randomPlayAllButton.show()
            self.guideLabel.show()
        # 如果被移除的是最后一首就将当前播放歌曲置为被移除后的播放列表最后一首
        """ if lastSongRemoved:
            self.currentIndexChanged.emit(self.currentIndex) """

    def __connectSignalToSlot(self):
        """ 将信号连接到槽 """
        self.blurCoverThread.blurDone.connect(self.setBlurPixmap)
        # 更新背景封面和下标
        self.songInfoCardChute.currentIndexChanged[int].connect(
            self.__songInfoCardChuteCurrentChangedSlot)
        self.songInfoCardChute.currentIndexChanged[str].connect(
            self.startBlurThread)
        # 显示和隐藏播放栏
        self.songInfoCardChute.showPlayBarSignal.connect(self.showPlayBar)
        self.songInfoCardChute.hidePlayBarSignal.connect(self.hidePlayBar)
        # 将播放栏的信号连接到槽
        self.playBar.pullUpArrowButton.clicked.connect(
            self.showPlaylistButtonSlot)
        self.playBar.showPlaylistButton.clicked.connect(
            self.showPlaylistButtonSlot)
        self.playBar.enterSignal.connect(
            self.__settleDownPlayBar)
        self.playBar.leaveSignal.connect(
            self.__startSongInfoCardTimer)
        # 将歌曲列表的信号连接到槽函数
        self.songListWidget.currentIndexChanged.connect(
            self.__songListWidgetCurrentChangedSlot)
        self.songListWidget.removeItemSignal.connect(
            self.__removeSongFromPlaylist)
        self.randomPlayAllButton.clicked.connect(
            lambda: self.randomPlayAllSignal.emit())


if __name__ == "__main__":
    app = QApplication(sys.argv)
    with open('Data\\songInfo.json', 'r', encoding='utf-8') as f:
        songInfo_list = load(f)
    demo = PlayingInterface(playlist=songInfo_list)
    demo.show()
    sys.exit(app.exec_())
