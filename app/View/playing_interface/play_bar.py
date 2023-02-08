# coding:utf-8
from common.signal_bus import signalBus
from components.buttons.play_bar_buttons import ButtonFactory as BF
from components.widgets.label import TimeLabel
from components.widgets.menu import PlayingInterfaceMoreActionsMenu
from components.widgets.slider import HollowHandleStyle, Slider
from components.widgets.volume_widget import VolumeWidget
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtWidgets import QWidget



class PlayBar(QWidget):
    """ Play bar """

    enterSignal = pyqtSignal()
    leaveSignal = pyqtSignal()

    searchMvSig = pyqtSignal()
    embedLyricSig = pyqtSignal()
    reloadLyricSig = pyqtSignal()
    savePlaylistSig = pyqtSignal()
    loadLyricFromFileSig = pyqtSignal()
    locateCurrentSongSig = pyqtSignal()
    revealLyricInFolderSig = pyqtSignal()
    lyricVisibleChanged = pyqtSignal(bool)

    def __init__(self, parent=None):
        super().__init__(parent)
        self.isLyricVisible = True
        self.playButton = BF.create(BF.PLAY, self)
        self.volumeButton = BF.create(BF.VOLUME, self)
        self.volumeWidget = VolumeWidget(self.window())
        self.fullScreenButton = BF.create(BF.FULL_SCREEN, self)
        self.playProgressBar = PlayProgressBar(parent=self)
        self.pullUpArrowButton = BF.create(BF.PULL_UP_ARROW, self)
        self.lastSongButton = BF.create(BF.PREVIOUS, self)
        self.nextSongButton = BF.create(BF.NEXT, self)
        self.randomPlayButton = BF.create(BF.RANDOM_PLAY, self)
        self.loopModeButton = BF.create(BF.LOOP_MODE, self)
        self.desktopLyricButton = BF.create(BF.DESKTOP_LYRIC, self)
        self.moreActionsButton = BF.create(BF.MORE, self)
        self.showPlaylistButton = BF.create(BF.PLAYLIST, self)
        self.smallPlayModeButton = BF.create(BF.SMALLEST_PLAY_MODE, self)
        self.progressSlider = self.playProgressBar.progressSlider

        self.__initWidget()

    def __initWidget(self):
        """ initialize widgets """
        self.setFixedHeight(193)
        self.setAttribute(Qt.WA_TranslucentBackground)

        self.lastSongButton.move(17, 85)
        self.playButton.move(77, 85)
        self.nextSongButton.move(137, 85)
        self.randomPlayButton.move(197, 85)
        self.loopModeButton.move(257, 85)
        self.volumeButton.move(317, 85)
        self.desktopLyricButton.move(377, 85)
        self.moreActionsButton.move(437, 85)
        self.playProgressBar.move(0, 45)
        self.volumeWidget.hide()

        self.lastSongButton.setToolTip(self.tr('Previous'))
        self.nextSongButton.setToolTip(self.tr('Next'))
        self.moreActionsButton.setToolTip(self.tr('More actions'))
        self.showPlaylistButton.setToolTip(self.tr('Show playlist'))
        self.smallPlayModeButton.setToolTip(self.tr('Smallest play mode'))

        self.__moveButtons()
        self.__connectSignalToSlot()

    def __onVolumeButtonClicked(self):
        """ show volume slider """
        if not self.volumeWidget.isVisible():
            pos = self.mapToGlobal(self.volumeButton.pos())
            x = pos.x() + int(
                self.volumeButton.width() / 2 - self.volumeWidget.width() / 2)
            y = pos.y()-100
            self.volumeWidget.move(x, y)
            self.volumeWidget.show()
        else:
            self.volumeWidget.hide()

    def __moveButtons(self):
        """ move buttons """
        self.pullUpArrowButton.move(
            self.width()//2 - self.pullUpArrowButton.width()//2, 165)
        self.fullScreenButton.move(self.width() - 64, 85)
        self.smallPlayModeButton.move(self.width() - 124, 85)
        self.showPlaylistButton.move(self.width() - 184, 85)

    def resizeEvent(self, e):
        super().resizeEvent(e)
        self.playProgressBar.resize(self.width(), 38)
        self.__moveButtons()

    def enterEvent(self, e):
        self.enterSignal.emit()

    def leaveEvent(self, e):
        self.leaveSignal.emit()

    def __showMoreActionsMenu(self):
        """ show more actions menu """
        menu = PlayingInterfaceMoreActionsMenu(self, self.isLyricVisible)

        menu.movieAct.triggered.connect(self.searchMvSig)
        menu.embedLyricAct.triggered.connect(self.embedLyricSig)
        menu.reloadLyricAct.triggered.connect(self.reloadLyricSig)
        menu.lyricVisibleChanged.connect(self._onLyricVisibleChanged)
        menu.locateAct.triggered.connect(self.locateCurrentSongSig)
        menu.savePlaylistAct.triggered.connect(self.savePlaylistSig)
        menu.loadLyricFromFileAct.triggered.connect(self.loadLyricFromFileSig)
        menu.clearPlaylistAct.triggered.connect(signalBus.clearPlayingPlaylistSig)
        menu.revealLyricInFolderAct.triggered.connect(self.revealLyricInFolderSig)

        menu.exec(menu.getPopupPos(self.moreActionsButton))

    def _onLyricVisibleChanged(self, isVisible: bool):
        self.isLyricVisible = isVisible
        self.lyricVisibleChanged.emit(isVisible)

    def __connectSignalToSlot(self):
        """ connect signal to slot """
        self.moreActionsButton.clicked.connect(self.__showMoreActionsMenu)

        self.volumeButton.clicked.connect(self.__onVolumeButtonClicked)
        self.volumeWidget.volumeChanged.connect(self.volumeButton.setVolume)
        self.volumeWidget.volumeChanged.connect(signalBus.volumeChanged)
        self.volumeWidget.muteStateChanged.connect(signalBus.muteStateChanged)

        self.lastSongButton.clicked.connect(signalBus.lastSongSig)
        self.nextSongButton.clicked.connect(signalBus.nextSongSig)
        self.playButton.clicked.connect(signalBus.togglePlayStateSig)
        self.fullScreenButton.fullScreenChanged.connect(signalBus.fullScreenChanged)
        self.playProgressBar.progressChanged.connect(signalBus.progressSliderMoved)

    def setCurrentTime(self, time: int):
        """ set current time in milliseconds """
        self.playProgressBar.setCurrentTime(time)

    def setTotalTime(self, time):
        """ set total time in milliseconds """
        self.playProgressBar.setTotalTime(time)


class PlayProgressBar(QWidget):
    """ Play progress bar """

    progressChanged = pyqtSignal(int)

    def __init__(self, duration: int = 0, parent=None):
        """
        Parameters
        ----------
        duration: int
            duration on seconds

        parent:
            parent window
        """
        super().__init__(parent)
        self.progressSlider = Slider(Qt.Horizontal, self)
        self.currentTimeLabel = TimeLabel(0, self)
        self.totalTimeLabel = TimeLabel(duration, self)
        self.__initWidget()

    def __initWidget(self):
        """ initialize widgets """
        self.setFixedHeight(24)
        self.progressSlider.move(73, 0)

        # set the style of slider
        style = HollowHandleStyle({
            "handle.ring-width": 3,
            "handle.hollow-radius": 9,
            "handle.margin": 0
        })
        self.progressSlider.setStyle(style)
        self.progressSlider.setFixedHeight(24)
        self.currentTimeLabel.setObjectName("timeLabel")
        self.totalTimeLabel.setObjectName("timeLabel")

        self.progressSlider.clicked.connect(self.progressChanged)
        self.progressSlider.sliderMoved.connect(self.progressChanged)

    def setCurrentTime(self, time: int):
        """ set current time in milliseconds """
        self.progressSlider.setValue(time)
        self.currentTimeLabel.setTime(int(time/1000))
        self.currentTimeLabel.move(
            33 - 9 * (len(self.totalTimeLabel.text()) - 4), 1)

    def setTotalTime(self, totalTime):
        """ set total time in milliseconds """
        self.totalTimeLabel.setTime(int(totalTime/1000))
        self.progressSlider.setRange(0, totalTime)

    def resizeEvent(self, e):
        self.progressSlider.resize(self.width() - 146, 24)
        self.totalTimeLabel.move(self.width() - 57, 1)
        self.currentTimeLabel.move(33, 1)
        super().resizeEvent(e)
