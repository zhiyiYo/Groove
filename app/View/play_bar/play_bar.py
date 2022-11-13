# coding:utf-8
from common.database.entity import SongInfo
from common.image_utils import DominantColor
from common.signal_bus import signalBus
from components.widgets.label import TimeLabel
from components.widgets.menu import PlayBarMoreActionsMenu
from components.widgets.slider import HollowHandleStyle, Slider
from PyQt5.QtCore import (QEasingCurve, QParallelAnimationGroup, QPoint,
                          QPropertyAnimation, Qt, pyqtProperty, pyqtSignal)
from PyQt5.QtGui import QColor, QPainter, QResizeEvent
from PyQt5.QtWidgets import QHBoxLayout, QVBoxLayout, QWidget
from View.play_bar.song_info_card import SongInfoCard

from .play_bar_buttons import (BasicButton, LoopModeButton, PlayButton,
                               RandomPlayButton, VolumeButton)


class PlayBar(QWidget):
    """ Play bar """

    savePlaylistSig = pyqtSignal()
    colorChanged = pyqtSignal(QColor)

    def __init__(self, songInfo: SongInfo, color: QColor, parent=None):
        super().__init__(parent)
        self.__oldWidth = 1280
        self.__color = color
        self.aniGroup = QParallelAnimationGroup(self)
        self.colorAni = QPropertyAnimation(self, b'color', self)
        self.aniDuration = 200

        self.playProgressBar = PlayProgressBar(songInfo.duration, self)
        self.songInfoCard = SongInfoCard(songInfo, self)
        self.centralButtonGroup = CentralButtonGroup(self)
        self.rightWidgetGroup = RightWidgetGroup(self)
        self.moreActionsMenu = PlayBarMoreActionsMenu(self)

        self.__initWidget()

    def __initWidget(self):
        """ initialize widgets """
        self.resize(1280, 115)
        self.setFixedHeight(115)
        self.__referenceWidgets()

        self.aniGroup.addAnimation(self.colorAni)
        self.aniGroup.addAnimation(self.songInfoCard.albumCoverLabel.ani)

        # set background color
        self.setColor(self.__color)
        self.updateVolumeSliderColor(self.__color)

        self.__adjustWidgetPos()
        self.__connectSignalToSlot()

    def __adjustWidgetPos(self):
        """ adjust the position of widgets """
        w = self.width()
        self.playProgressBar.move(
            int(w/2 - self.playProgressBar.width()/2), self.centralButtonGroup.height())
        self.centralButtonGroup.move(
            int(w/2 - self.centralButtonGroup.width()/2), 0)
        self.rightWidgetGroup.move(w - self.rightWidgetGroup.width(), 0)

    def resizeEvent(self, e: QResizeEvent):
        dw = self.width() - self.__oldWidth

        # adjust the width of progress slider
        pBar = self.playProgressBar
        pBar.resize(pBar.width() + dw//3, pBar.height())

        self.__adjustWidgetPos()
        self.__adjustSongInfoCardWidth()

        self.__oldWidth = self.width()

    def __showMoreActionsMenu(self):
        """ show more actions menu """
        globalPos = self.rightWidgetGroup.mapToGlobal(
            self.moreActionsButton.pos())
        x = globalPos.x() + self.moreActionsButton.width() - 250
        y = int(globalPos.y() + self.moreActionsButton.height() / 2 - 300 / 2)
        self.moreActionsMenu.exec(QPoint(x, y))

    def __referenceWidgets(self):
        """ reference widgets and methods """
        self.randomPlayButton = self.centralButtonGroup.randomPlayButton
        self.lastSongButton = self.centralButtonGroup.lastSongButton
        self.playButton = self.centralButtonGroup.playButton
        self.nextSongButton = self.centralButtonGroup.nextSongButton
        self.loopModeButton = self.centralButtonGroup.loopModeButton
        self.progressSlider = self.playProgressBar.progressSlider
        self.volumeButton = self.rightWidgetGroup.volumeButton
        self.volumeSlider = self.rightWidgetGroup.volumeSlider
        self.smallPlayModeButton = self.rightWidgetGroup.smallPlayModeButton
        self.moreActionsButton = self.rightWidgetGroup.moreActionsButton
        self.setCurrentTime = self.playProgressBar.setCurrentTime
        self.setTotalTime = self.playProgressBar.setTotalTime

    def updateWindow(self, songInfo: SongInfo):
        """ update play bar """
        self.songInfoCard.updateWindow(songInfo)
        self.__adjustSongInfoCardWidth()

    def __adjustSongInfoCardWidth(self):
        """ adjust the width of song information card """
        card = self.songInfoCard
        card.adjustSize()
        if card.width() >= self.playProgressBar.x() - 20:
            card.setFixedWidth(self.playProgressBar.x() - 20)
            card.textWindow.setMaxWidth(card.width() - 155)

    def setRandomPlay(self, isRandomPlay: bool):
        """ set whether to play randomly """
        self.randomPlayButton.setRandomPlay(isRandomPlay)

    def setMute(self, isMute: bool):
        """ set whether to mute """
        self.volumeButton.setMute(isMute)

    def setVolume(self, volume: int):
        """ set volume """
        self.volumeSlider.setValue(volume)
        self.volumeButton.setVolumeLevel(volume)

    def setPlay(self, isPlay: bool):
        """ set play state """
        self.playButton.setPlay(isPlay)

    def __connectSignalToSlot(self):
        """ connect signal to slot """
        self.nextSongButton.clicked.connect(signalBus.nextSongSig)
        self.lastSongButton.clicked.connect(signalBus.lastSongSig)
        self.playButton.clicked.connect(signalBus.togglePlayStateSig)
        self.volumeSlider.valueChanged.connect(signalBus.volumeChanged)
        self.progressSlider.clicked.connect(signalBus.progressSliderMoved)
        self.songInfoCard.clicked.connect(signalBus.showPlayingInterfaceSig)
        self.songInfoCard.albumChanged.connect(self.__onAlbumChanged)
        self.moreActionsButton.clicked.connect(self.__showMoreActionsMenu)
        self.progressSlider.sliderMoved.connect(signalBus.progressSliderMoved)
        self.smallPlayModeButton.clicked.connect(
            signalBus.showSmallestPlayInterfaceSig)
        self.moreActionsMenu.fullScreenAct.triggered.connect(
            lambda: signalBus.fullScreenChanged.emit(True))
        self.moreActionsMenu.savePlayListAct.triggered.connect(
            self.savePlaylistSig)
        self.moreActionsMenu.showPlayListAct.triggered.connect(
            signalBus.showPlayingPlaylistSig)
        self.moreActionsMenu.clearPlayListAct.triggered.connect(
            signalBus.clearPlayingPlaylistSig)

    def __onAlbumChanged(self, albumPath: str):
        """ album changed slot """
        r, g, b = DominantColor.getDominantColor(albumPath)
        color = QColor(r, g, b)
        self.colorChanged.emit(color)

        t = self.aniDuration
        self.colorAni.setStartValue(self.getColor())
        self.colorAni.setEndValue(color)
        self.colorAni.setEasingCurve(QEasingCurve.OutCubic)
        self.colorAni.setDuration(t)

        self.songInfoCard.albumCoverLabel.ani.setStartValue(0)
        self.songInfoCard.albumCoverLabel.ani.setEndValue(1)
        self.songInfoCard.albumCoverLabel.ani.setEasingCurve(
            QEasingCurve.OutCubic)
        self.songInfoCard.albumCoverLabel.ani.setDuration(t)

        self.aniGroup.start()
        self.updateVolumeSliderColor(color)

    def updateVolumeSliderColor(self, color: QColor):
        """ update the sub-page color of volume slider

        Parameters
        ----------
        color: QColor
            background color of play bar
        """
        if color.lightness() >= 127:
            subPageColor = QColor(70, 23, 180)
        else:
            subPageColor = QColor(255, 255, 255)

        self.volumeSlider.setStyle(HollowHandleStyle(
            {"sub-page.color": subPageColor}))

    def setLoopMode(self, loopMode):
        """ set loop mode """
        self.loopModeButton.setLoopMode(loopMode)

    def paintEvent(self, e):
        painter = QPainter(self)
        painter.setPen(Qt.NoPen)
        painter.setBrush(self.__color)
        painter.drawRect(self.rect())

    def setColor(self, color: QColor):
        """ set background color """
        self.__color = color
        self.update()

    def getColor(self):
        return self.__color

    color = pyqtProperty(QColor, getColor, setColor)


class CentralButtonGroup(QWidget):
    """ Central button group """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.randomPlayButton = RandomPlayButton(self)
        self.lastSongButton = BasicButton(
            ':/images/play_bar/Previous.png', self)
        self.nextSongButton = BasicButton(':/images/play_bar/Next.png', self)
        self.playButton = PlayButton(self)
        self.loopModeButton = LoopModeButton(self)

        self.vBoxLayout = QVBoxLayout(self)
        self.__initWidgets()

    def __initWidgets(self):
        """ initialize widgets """
        self.setFixedSize(317, 67 + 8 + 3)

        hBoxLayout = QHBoxLayout()
        hBoxLayout.setSpacing(0)
        hBoxLayout.setContentsMargins(0, 0, 0, 0)

        buttons = [self.randomPlayButton, self.lastSongButton,
                   self.playButton, self.nextSongButton, self.loopModeButton]

        for i, button in enumerate(buttons):
            hBoxLayout.addWidget(button, 0, Qt.AlignCenter)
            if i != 4:
                hBoxLayout.addSpacing(16)

        self.vBoxLayout.addSpacing(8)
        self.vBoxLayout.setSpacing(0)
        self.vBoxLayout.setContentsMargins(0, 0, 0, 0)
        self.vBoxLayout.addLayout(hBoxLayout)

        # set tooltip
        self.lastSongButton.setToolTip(self.tr('Previous'))
        self.nextSongButton.setToolTip(self.tr('Next'))


class RightWidgetGroup(QWidget):
    """ Right widget group """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.hBoxLayout = QHBoxLayout(self)
        self.volumeButton = VolumeButton(self)
        self.volumeSlider = Slider(Qt.Horizontal, self)
        self.smallPlayModeButton = BasicButton(
            ":/images/play_bar/SmallestPlayMode.png", self)
        self.moreActionsButton = BasicButton(
            ":/images/play_bar/More.png", self)

        self.__initWidget()
        self.__initLayout()

    def __initWidget(self):
        """ initialize widgets """
        self.setFixedSize(301, 16 + 67)
        self.volumeSlider.setRange(0, 100)
        self.volumeSlider.setStyle(HollowHandleStyle(
            {"sub-page.color": QColor(255, 255, 255)}))
        self.volumeSlider.setFixedHeight(28)
        self.volumeSlider.setValue(20)
        self.smallPlayModeButton.setToolTip(self.tr('Smallest play mode'))
        self.moreActionsButton.setToolTip(self.tr('More actions'))

    def __initLayout(self):
        """ initialize layout """
        spacings = [7, 8, 8, 5, 7]
        widgets = [self.volumeButton, self.volumeSlider,
                   self.smallPlayModeButton, self.moreActionsButton]

        self.hBoxLayout.setSpacing(0)
        self.hBoxLayout.setContentsMargins(0, 0, 0, 0)

        for i in range(4):
            self.hBoxLayout.addSpacing(spacings[i])
            self.hBoxLayout.addWidget(widgets[i])

        self.hBoxLayout.addSpacing(spacings[-1])


class PlayProgressBar(QWidget):
    """ Play progress bar """

    def __init__(self, duration: int, parent=None):
        """
        Parameters
        ----------
        duration: int
            duration of song in seconds

        parent:
            parent window
        """
        super().__init__(parent)
        self.progressSlider = Slider(Qt.Horizontal, self)
        self.currentTimeLabel = TimeLabel(0, self)
        self.totalTimeLabel = TimeLabel(duration or 0, self)
        self.hBoxLayout = QHBoxLayout(self)
        self.__initWidget()

    def __initWidget(self):
        """ initialize widgets """
        self.resize(450, 30)

        # set the style of slider
        self.setStyleSheet("""
            QLabel {
                color: white;
                font: 15px 'Segoe UI';
                font-weight: 500;
                background-color: transparent;
            }
        """)
        self.progressSlider.setStyle(HollowHandleStyle())
        self.progressSlider.setRange(0, 0)
        self.progressSlider.setFixedHeight(28)

        # add widgets to layout
        self.hBoxLayout.addWidget(self.currentTimeLabel, 0, Qt.AlignHCenter)
        self.hBoxLayout.addWidget(self.progressSlider, 0, Qt.AlignHCenter)
        self.hBoxLayout.addWidget(self.totalTimeLabel, 0, Qt.AlignHCenter)
        self.hBoxLayout.setContentsMargins(0, 0, 0, 0)
        self.hBoxLayout.setSpacing(10)

    def setCurrentTime(self, currentTime: int):
        """ set current time in milliseconds """
        self.currentTimeLabel.setTime(int(currentTime/1000))

    def setTotalTime(self, totalTime: int):
        """ set total time in milliseconds """
        self.totalTimeLabel.setTime(int(totalTime/1000))
        self.progressSlider.setRange(0, totalTime)

    def resizeEvent(self, e):
        self.progressSlider.setFixedWidth(self.width() - 100)
        super().resizeEvent(e)
