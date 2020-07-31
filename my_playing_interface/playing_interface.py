import sys
from json import load
from PyQt5.QtCore import (QEasingCurve, QParallelAnimationGroup,
                          QPropertyAnimation, QRect, Qt, QTimer)
from PyQt5.QtGui import QImage, QPixmap, QPalette, QColor
from PyQt5.QtWidgets import QApplication, QGraphicsBlurEffect, QLabel, QWidget

from blur_cover_thread import BlurCoverThread
from play_bar import PlayBar

from song_info_card_chute import SongInfoCardChute
from song_list_widget import SongCardListWidget


class PlayingInterface(QWidget):
    """ 正在播放界面 """

    def __init__(self, playlist: list = None, parent=None):
        super().__init__(parent)
        self.playlist = playlist
        self.currentIndex = 0
        self.isPlaylistVisible = False
        # 创建小部件
        self.blurPixmap = None
        self.blurBackgroundPic = QLabel(self)
        self.blurCoverThread = BlurCoverThread(self)
        self.songInfoCardChute = SongInfoCardChute(self, playlist)
        self.parallelAniGroup = QParallelAnimationGroup(self)
        self.songInfoCardChuteAni = QPropertyAnimation(
            self.songInfoCardChute, b'geometry')
        self.playBar = PlayBar(self)
        self.songListWidget = SongCardListWidget(playlist,self)
        self.playBarAni = QPropertyAnimation(self.playBar, b'geometry')
        self.songListWidgetAni = QPropertyAnimation(
            self.songListWidget, b'geometry')
        # 创建定时器
        self.showPlaylistTimer = QTimer(self)
        self.hidePlaylistTimer = QTimer(self)
        # 初始化
        self.__initWidget()

    def __initWidget(self):
        """ 初始化小部件 """
        self.resize(1100, 870)
        self.playBar.move(0, self.height()-self.playBar.height())
        self.playBar.hide()
        # 开启磨砂线程
        self.blurCoverThread.start()
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
        # 设置背景色
        palette = QPalette()
        palette.setColor(QPalette.Background, QColor(Qt.black))
        self.setPalette(palette)

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
                maxWidth, maxWidth, Qt.KeepAspectRatio, Qt.SmoothTransformation))

    def startBlurThread(self, albumCoverPath):
        """ 开启磨砂线程 """
        self.blurCoverThread.setTargetCover(albumCoverPath)
        self.blurCoverThread.start()

    def resizeEvent(self, e):
        """ 改变尺寸时也改变小部件的大小 """
        super().resizeEvent(e)
        self.__resizeBlurPixmap()
        self.songInfoCardChute.resize(self.size())
        self.blurBackgroundPic.setFixedSize(self.size())
        self.playBar.resize(self.width(), self.playBar.height())
        self.songListWidget.resize(self.width()-60,self.height()-382)
        if self.isPlaylistVisible:
            self.playBar.move(0, 190)
            self.songListWidget.move(30, 382)
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
        #self.parallelAniGroup.start()
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

    def next(self):
        """ 播放下一首 """
        if self.currentIndex != len(self.playlist) - 1:
            self.songInfoCardChute.cycleLeftShift()

    def previous(self):
        """ 播放上一首 """
        if self.currentIndex != 0:
            self.songInfoCardChute.cycleRightShift()

    def setCurrentIndex(self, index):
        """ 更新播放列表下标 """
        self.currentIndex = index

    def __settleDownPlayBar(self):
        """ 定住播放栏 """
        self.songInfoCardChute.stopSongInfoCardTimer()

    def __startSongInfoCardTimer(self):
        """ 重新打开歌曲信息卡的定时器 """
        if not self.playBar.volumeSlider.isVisible():
            # 只有音量滑动条不可见才打开计时器
            self.songInfoCardChute.startSongInfoCardTimer()

    def __connectSignalToSlot(self):
        """ 将信号连接到槽 """
        self.blurCoverThread.blurDone.connect(self.setBlurPixmap)
        # 更新背景封面和下标
        self.songInfoCardChute.currentSongChanged[int].connect(
            self.setCurrentIndex)
        self.songInfoCardChute.currentSongChanged[str].connect(
            self.startBlurThread)
        # 显示和隐藏播放栏
        self.songInfoCardChute.showPlayBarSignal.connect(self.showPlayBar)
        self.songInfoCardChute.hidePlayBarSignal.connect(self.hidePlayBar)
        # 将播放栏的信号连接到槽
        self.playBar.nextSongButton.clicked.connect(self.next)
        self.playBar.lastSongButton.clicked.connect(self.previous)
        self.playBar.pullUpArrowButton.clicked.connect(
            self.showPlaylistButtonSlot)
        self.playBar.showPlaylistButton.clicked.connect(
            self.showPlaylistButtonSlot)
        self.playBar.enterSignal.connect(
            self.__settleDownPlayBar)
        self.playBar.leaveSignal.connect(
            self.__startSongInfoCardTimer)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    with open('Data\\songInfo.json', 'r', encoding='utf-8') as f:
        songInfo_list = load(f)
    demo = PlayingInterface(playlist=songInfo_list)
    demo.show()
    sys.exit(app.exec_())
