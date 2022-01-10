# coding:utf-8
from components.dialog_box.message_dialog import MessageDialog
from PyQt5.QtCore import QSizeF, Qt, QUrl, pyqtSignal, QSize
from PyQt5.QtGui import QPainter
from PyQt5.QtMultimedia import QMediaContent, QMediaPlayer
from PyQt5.QtMultimediaWidgets import QGraphicsVideoItem
from PyQt5.QtWidgets import (QAction, QApplication, QGraphicsScene,
                             QGraphicsView)

from .play_bar import PlayBar


class VideoWindow(QGraphicsView):
    """ 视频界面 """

    fullScreenChanged = pyqtSignal(bool) # 进入/退出全屏

    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.graphicsScene = QGraphicsScene(self)
        self.videoItem = GraphicsVideoItem()
        self.player = QMediaPlayer(self)
        self.playBar = PlayBar(self)
        self.toggleFullScreenAct = QAction(
            self, shortcut=Qt.Key_F11, triggered=self.__toggleFullScreen)
        self.__initWidget()

    def __initWidget(self):
        """ 初始化小部件 """
        self.resize(800, 800)
        self.setMouseTracking(True)
        self.setScene(self.graphicsScene)
        self.addActions([self.toggleFullScreenAct])
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
        self.videoItem.setSize(QSizeF(self.size()))

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

    def pause(self):
        """ 暂停视频 """
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
        self.playBar.setVisible(not self.playBar.isVisible())

    def __enterFullScreen(self):
        """ 进入全屏 """
        self.playBar.fullScreenButton.setFullScreen(True)
        self.fullScreenChanged.emit(True)

    def __exitFullScreen(self):
        """ 退出全屏 """
        self.playBar.fullScreenButton.setFullScreen(False)
        self.fullScreenChanged.emit(False)

    def __toggleFullScreen(self):
        """ 切换全屏状态 """
        if self.window().isFullScreen():
            self.__exitFullScreen()
        else:
            self.__enterFullScreen()

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

    def __onPlayerError(self, error: QMediaPlayer.Error):
        """ 播放器错误槽函数 """
        if error == QMediaPlayer.NoError:
            return

        messageMap = {
            QMediaPlayer.ResourceError: self.tr(
                "The media resource couldn't be resolved."),
            QMediaPlayer.FormatError: self.tr(
                "The format of a media resource isn't supported."),
            QMediaPlayer.NetworkError: self.tr("A network error occurred."),
            QMediaPlayer.AccessDeniedError: self.tr(
                "There are not the appropriate permissions to play the media resource."),
            QMediaPlayer.ServiceMissingError: self.tr(
                "A valid playback service was not found, playback cannot proceed.")
        }
        w = MessageDialog(self.tr('An error occurred'),
                          messageMap[error], self.window())
        w.yesButton.hide()
        w.exec()

    def __connectSignalToSlot(self):
        """ 信号连接到槽 """
        self.player.error.connect(self.__onPlayerError)
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
            self.fullScreenChanged)



class GraphicsVideoItem(QGraphicsVideoItem):
    """ 视频图元 """

    def paint(self, painter: QPainter, option, widget):
        painter.setCompositionMode(QPainter.CompositionMode_Difference)
        super().paint(painter, option, widget)
