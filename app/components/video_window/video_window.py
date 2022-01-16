# coding:utf-8
from pathlib import Path

from common.thread.download_mv_thread import DownloadMvThread
from components.dialog_box.message_dialog import MessageDialog
from components.widgets.state_tooltip import DownloadStateTooltip
from PyQt5.QtCore import QSizeF, Qt, QUrl, pyqtSignal, QTimer
from PyQt5.QtGui import QPainter
from PyQt5.QtMultimedia import QMediaContent, QMediaPlayer
from PyQt5.QtMultimediaWidgets import QGraphicsVideoItem
from PyQt5.QtWidgets import (QAction, QApplication, QGraphicsScene,
                             QGraphicsView, QFileDialog)

from .play_bar import PlayBar


class VideoWindow(QGraphicsView):
    """ 视频界面 """

    downloadSignal = pyqtSignal(str, str)  # 下载 MV
    fullScreenChanged = pyqtSignal(bool)   # 进入/退出全屏

    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.url = ''
        self.videoName = ''
        self.downloadStateTooltip = None
        self.downloadMvThread = DownloadMvThread(self)
        self.graphicsScene = QGraphicsScene(self)
        self.videoItem = GraphicsVideoItem()
        self.player = QMediaPlayer(self)
        self.playBar = PlayBar(self)
        self.hidePlayBarTimer = QTimer(self)
        self.toggleFullScreenAct = QAction(
            self, shortcut=Qt.Key_F11, triggered=self.__toggleFullScreen)
        self.__initWidget()

    def __initWidget(self):
        """ 初始化小部件 """
        self.resize(800, 800)
        self.setMouseTracking(True)
        self.setScene(self.graphicsScene)
        self.addActions([self.toggleFullScreenAct])
        self.hidePlayBarTimer.setSingleShot(True)

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

    def setVideo(self, url: str, videoName: str):
        """ 设置视频 """
        self.url = url
        self.videoName = videoName
        self.resetTransform()
        self.player.setMedia(QMediaContent(QUrl(url)))
        self.videoItem.setSize(QSizeF(self.size()))
        self.play()

    def togglePlayState(self):
        """ 切换播放状态 """
        if self.player.state() == QMediaPlayer.PlayingState:
            self.pause()
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
        self.hidePlayBarTimer.stop()
        self.playBar.show()
        self.hidePlayBarTimer.start(1500)

    def mousePressEvent(self, e):
        """ 鼠标点击时切换播放栏可见性 """
        self.playBar.setVisible(not self.playBar.isVisible())
        if self.playBar.isVisible():
            self.hidePlayBarTimer.start(1500)

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

    def __onDownloadButtonClicked(self):
        """ 下载按钮点击槽函数 """
        path, _ = QFileDialog.getSaveFileName(
            self, self.tr('save as'), f'./{self.videoName}', 'MP4 (*.mp4)')
        if not path:
            return

        self.downloadMvThread.appendDownloadTask(self.url, path)

        if self.downloadMvThread.isRunning():
            self.downloadStateTooltip.appendOneDownloadTask()
            return

        title = self.tr('Downloading MVs')
        content = self.tr('There are') + \
            f' {1} ' + self.tr('left. Please wait patiently')
        self.downloadStateTooltip = DownloadStateTooltip(
            title, content, 1, self.window())
        self.downloadMvThread.downloadOneMvFinished.connect(
            self.downloadStateTooltip.completeOneDownloadTask)

        pos = self.downloadStateTooltip.getSuitablePos()
        self.downloadStateTooltip.move(pos)
        self.downloadStateTooltip.show()
        self.downloadMvThread.start()

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
        self.playBar.downloadButton.clicked.connect(
            self.__onDownloadButtonClicked)

        self.hidePlayBarTimer.timeout.connect(self.playBar.hide)


class GraphicsVideoItem(QGraphicsVideoItem):
    """ 视频图元 """

    def paint(self, painter: QPainter, option, widget):
        painter.setCompositionMode(QPainter.CompositionMode_Difference)
        super().paint(painter, option, widget)
