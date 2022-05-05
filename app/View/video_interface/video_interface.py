# coding:utf-8
from common.thread.download_mv_thread import DownloadMvThread
from components.dialog_box.message_dialog import MessageDialog
from components.widgets.state_tooltip import DownloadStateTooltip
from PyQt5.QtCore import QSizeF, Qt, QTimer, QUrl, pyqtSignal
from PyQt5.QtGui import QPainter
from PyQt5.QtMultimedia import QMediaContent, QMediaPlayer
from PyQt5.QtMultimediaWidgets import QGraphicsVideoItem
from PyQt5.QtWidgets import QAction, QFileDialog, QGraphicsScene, QGraphicsView

from .play_bar import PlayBar


class VideoInterface(QGraphicsView):
    """ Video window """

    downloadSignal = pyqtSignal(str, str)  # download MV
    fullScreenChanged = pyqtSignal(bool)   # enter/exit full screen

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
        """ initialize widgets """
        self.resize(800, 800)
        self.setMouseTracking(True)
        self.setScene(self.graphicsScene)
        self.addActions([self.toggleFullScreenAct])
        self.hidePlayBarTimer.setSingleShot(True)

        # set the widget to play video
        self.graphicsScene.addItem(self.videoItem)
        self.player.setVideoOutput(self.videoItem)
        self.setRenderHints(QPainter.Antialiasing |
                            QPainter.SmoothPixmapTransform)

        # hide scroll bar
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)

        # initialize volume
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
        """ set the video to play """
        self.url = url
        self.videoName = videoName
        self.resetTransform()
        self.player.setMedia(QMediaContent(QUrl(url)))
        self.videoItem.setSize(QSizeF(self.size()))
        self.play()

    def togglePlayState(self):
        """ toggle play state """
        if self.player.state() == QMediaPlayer.PlayingState:
            self.pause()
        else:
            self.play()

    def __setQss(self):
        """ set style sheet """
        self.setStyleSheet("""
            QGraphicsView {
                background: black;
                border: none
            }
        """)

    def play(self):
        """ play video """
        self.player.play()
        self.playBar.playButton.setPlay(True)

    def pause(self):
        """ pause video """
        self.player.pause()
        self.playBar.playButton.setPlay(False)

    def closeEvent(self, e):
        """ 关闭时暂停视频 """
        self.pause()
        e.accept()

    def __onDurationChanged(self, duration: int):
        """ duration changed slot """
        if duration < 1:
            return

        self.playBar.setTotalTime(duration)

    def mouseMoveEvent(self, e):
        self.hidePlayBarTimer.stop()
        self.playBar.show()
        self.setCursor(Qt.ArrowCursor)
        self.hidePlayBarTimer.start(1500)

    def mousePressEvent(self, e):
        self.playBar.setVisible(not self.playBar.isVisible())
        if self.playBar.isVisible():
            self.hidePlayBarTimer.start(1500)

    def __enterFullScreen(self):
        """ enter full screen """
        self.playBar.fullScreenButton.setFullScreen(True)
        self.playBar.fullScreenButton.setToolTip(self.tr('Exit fullscreen'))
        self.fullScreenChanged.emit(True)

    def __exitFullScreen(self):
        """ exit full screen """
        self.playBar.fullScreenButton.setFullScreen(False)
        self.playBar.fullScreenButton.setToolTip(self.tr('Show fullscreen'))
        self.fullScreenChanged.emit(False)

    def __toggleFullScreen(self):
        """ toggle full screen """
        if self.window().isFullScreen():
            self.__exitFullScreen()
        else:
            self.__enterFullScreen()

    def __onMediaStatusChanged(self, status: QMediaPlayer.MediaStatus):
        """ media status changed slot """
        if status != QMediaPlayer.EndOfMedia:
            return

        self.playBar.playButton.setPlay(False)

    def __skipBack(self):
        """ Back up for 10 seconds. """
        pos = self.player.position()
        self.player.setPosition(pos-10000)

    def __skipForward(self):
        """ Fast forward 10 seconds """
        pos = self.player.position()
        self.player.setPosition(pos+10000)

    def __onPlayerError(self, error: QMediaPlayer.Error):
        """ play error slot """
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
        """ download button clicked slot """
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

    def __onFullScreenChanged(self, isFullScreen: bool):
        """ full screen changed slot """
        text = self.tr('Exit fullscreen') if isFullScreen else self.tr(
            'Show fullscreen')
        self.playBar.fullScreenButton.setToolTip(text)
        self.fullScreenChanged.emit(isFullScreen)

    def __onHideTimeOut(self):
        self.playBar.hide()
        self.setCursor(Qt.BlankCursor)

    def __connectSignalToSlot(self):
        """ connect signal to slot """
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
            self.__onFullScreenChanged)
        self.playBar.downloadButton.clicked.connect(
            self.__onDownloadButtonClicked)

        self.hidePlayBarTimer.timeout.connect(self.__onHideTimeOut)


class GraphicsVideoItem(QGraphicsVideoItem):
    """ Graphics video item """

    def paint(self, painter: QPainter, option, widget):
        painter.setCompositionMode(QPainter.CompositionMode_Difference)
        super().paint(painter, option, widget)
