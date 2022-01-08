# coding:utf-8
from components.frameless_window import FramelessWindow
from PyQt5.QtMultimediaWidgets import QGraphicsVideoItem
from PyQt5.QtMultimedia import QMediaContent, QMediaPlayer
from PyQt5.QtCore import Qt, pyqtSignal, QFile, QUrl, QSizeF
from PyQt5.QtGui import QPixmap, QPainter
from PyQt5.QtWidgets import QWidget, QGraphicsView, QGraphicsScene, QAction

from .play_bar import PlayBar


class VideoWindow(QGraphicsView):
    """ 视频界面 """

    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.graphicsScene = QGraphicsScene(self)
        self.videoItem = QGraphicsVideoItem()
        self.player = QMediaPlayer(self)
        self.playBar = PlayBar(self)
        self.toggleFullScreenAct = QAction(
            self, shortcut=Qt.Key_F11, triggered=self.toggleFullScreen)
        self.exitFullScreenAct = QAction(
            self, shortcut=Qt.Key_Escape, triggered=self.exitFullScreen)
        self.__initWidget()

    def __initWidget(self):
        """ 初始化小部件 """
        self.resize(800, 800)
        self.setMouseTracking(True)
        self.setScene(self.graphicsScene)
        self.addActions([self.toggleFullScreenAct, self.exitFullScreenAct])
        self.setWindowFlags(self.windowFlags() | Qt.Window)
        self.setWindowTitle(self.tr('Groove Music'))

        # 设置视频播放窗口
        self.graphicsScene.addItem(self.videoItem)
        self.player.setVideoOutput(self.videoItem)
        self.setRenderHints(QPainter.Antialiasing |
                            QPainter.SmoothPixmapTransform)

        # 隐藏滚动条
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        # 初始化音量
        self.player.setVolume(30)
        self.playBar.volumeSliderWidget.setVolume(30)

        self.__setQss()
        self.__connectSignalToSlot()

    def resizeEvent(self, e):
        super().resizeEvent(e)
        self.fitInView(self.videoItem, Qt.KeepAspectRatio)
        self.playBar.move(0, self.height()-self.playBar.height())
        self.playBar.setFixedSize(self.width(), self.playBar.height())

    def setVideo(self, url: str):
        """ 设置视频 """
        self.player.setMedia(QMediaContent(QUrl(url)))
        self.play()

    def togglePlayState(self):
        """ 切换播放状态 """
        if self.player.state() == QMediaPlayer.PlayingState:
            self.player.pause()
        else:
            self.play()

    def __setQss(self):
        """ 设置层叠样式 """
        self.setStyleSheet("""
            QGraphicsView {
                background: black;
                border: none
            }
        """)

    def play(self):
        """ 播放视频 """
        self.player.play()
        self.playBar.playButton.setPlay(True)
        self.videoItem.setSize(QSizeF(self.size()))

    def pause(self):
        """ 播放视频 """
        self.player.pause()
        self.playBar.playButton.setPlay(False)

    def closeEvent(self, e):
        """ 关闭时暂停视频 """
        self.pause()
        e.accept()

    def __onDurationChanged(self, duration: int):
        """ 视频时长改变槽函数 """
        if duration < 1:
            return

        self.playBar.setTotalTime(duration)

    def mouseMoveEvent(self, e):
        """ 鼠标移动时显示播放栏 """
        self.__showPlayBar()

    def mousePressEvent(self, e):
        """ 鼠标点击时切换播放栏可见性 """
        self.__togglePlayBar()

    def __showPlayBar(self):
        """ 显示播放栏 """
        if not self.playBar.isVisible():
            self.playBar.show()

    def __togglePlayBar(self):
        """ 切换播放栏可见性 """
        if self.playBar.isVisible():
            self.playBar.hide()
        else:
            self.playBar.show()

    def __onFullScreenChanged(self, isFullScreen: bool):
        """ 全屏按钮点击槽函数 """
        if isFullScreen:
            self.showFullScreen()
        else:
            self.showNormal()

    def enterFullScreen(self):
        """ 进入全屏 """
        self.showFullScreen()
        self.playBar.fullScreenButton.setFullScreen(True)

    def exitFullScreen(self):
        """ 退出全屏 """
        self.showNormal()
        self.playBar.fullScreenButton.setFullScreen(False)

    def toggleFullScreen(self):
        """ 切换全屏状态 """
        if self.isFullScreen():
            self.exitFullScreen()
        else:
            self.enterFullScreen()

    def __onMediaStatusChanged(self, status: QMediaPlayer.MediaStatus):
        """ 媒体状态改变槽函数 """
        if status != QMediaPlayer.EndOfMedia:
            return

        self.playBar.playButton.setPlay(False)

    def __skipBack(self):
        """ 回退 10 秒 """
        pos = self.player.position()
        self.player.setPosition(pos-10000)

    def __skipForward(self):
        """ 快进 10 秒 """
        pos = self.player.position()
        self.player.setPosition(pos+10000)

    def __connectSignalToSlot(self):
        """ 信号连接到槽 """
        self.player.durationChanged.connect(self.__onDurationChanged)
        self.player.positionChanged.connect(self.playBar.setCurrentTime)
        self.player.mediaStatusChanged.connect(self.__onMediaStatusChanged)

        self.playBar.playButton.clicked.connect(self.togglePlayState)
        self.playBar.progressSliderMoved.connect(self.player.setPosition)
        self.playBar.skipBackButton.clicked.connect(self.__skipBack)
        self.playBar.skipForwardButton.clicked.connect(self.__skipForward)
        self.playBar.volumeSliderWidget.muteStateChanged.connect(
            self.player.setMuted)
        self.playBar.volumeSliderWidget.volumeSlider.valueChanged.connect(
            self.player.setVolume)
        self.playBar.fullScreenButton.fullScreenChanged.connect(
            self.__onFullScreenChanged)
