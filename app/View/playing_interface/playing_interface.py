# coding:utf-8
from typing import List

from common.database.entity import SongInfo
from common.lyric import Lyric
from common.meta_data.writer import MetaDataWriter
from common.os_utils import getCoverPath, showInFolder
from common.audio_utils import writeAudio
from common.signal_bus import signalBus
from common.style_sheet import setStyleSheet
from common.thread.get_lyric_thread import GetLyricThread
from common.thread.get_mv_url_thread import GetMvUrlThread
from components.buttons.three_state_button import ThreeStatePushButton
from components.dialog_box.message_dialog import MessageDialog
from components.selection_mode_interface.bar import PlayingSelectionModeBar
from components.widgets.label import BlurCoverLabel, MaskLabel
from components.widgets.lyric_widget import LyricWidget
from components.widgets.menu import AddToMenu
from PyQt5.QtCore import (QAbstractAnimation, QEasingCurve,
                          QParallelAnimationGroup, QPoint, QPropertyAnimation,
                          QSize, Qt, QTimer, pyqtSignal)
from PyQt5.QtGui import QColor
from PyQt5.QtMultimedia import QMediaPlaylist
from PyQt5.QtWidgets import QFileDialog, QLabel, QWidget
from View.desktop_lyric_interface import DesktopLyricInterface

from .play_bar import PlayBar
from .song_info_card_chute import SongInfoCardChute
from .song_list_widget import SongListWidget


def handleSelectionMode(func):
    """ Selection mode decorator """

    def wrapper(playingInterface, *args, **kwargs):
        if playingInterface.isInSelectionMode:
            playingInterface.exitSelectionMode()
        return func(playingInterface, *args, **kwargs)

    return wrapper


class PlayingInterface(QWidget):
    """ 正在播放界面 """

    removeSongSignal = pyqtSignal(int)                   # 从播放列表移除歌曲
    savePlaylistSig = pyqtSignal()                       # 保存播放列表
    currentIndexChanged = pyqtSignal(int)                # 当前歌曲改变
    selectionModeStateChanged = pyqtSignal(bool)         # 进入/退出选择模式
    switchToVideoInterfaceSig = pyqtSignal(str)          # 切换到视频界面

    def __init__(self, playlist: List[SongInfo] = None, parent=None):
        super().__init__(parent)
        self.playlist = playlist if playlist else []
        self.currentIndex = 0
        self.isPlaylistVisible = False
        self.isInSelectionMode = True
        self.isLyricVisible = True

        # create threads
        self.getLyricThread = GetLyricThread(self)
        self.getMvUrlThread = GetMvUrlThread(self)

        # create widgets
        self.albumCoverLabel = BlurCoverLabel(12, (450, 450), self)
        self.maskLabel = MaskLabel(QColor(0, 0, 0, 215), self)
        self.songInfoCardChute = SongInfoCardChute(self.playlist, self)
        self.lyricWidget = LyricWidget(self.songInfoCardChute)
        self.desktopLyricInterface = DesktopLyricInterface()
        self.parallelAniGroup = QParallelAnimationGroup(self)
        self.playBar = PlayBar(self)
        self.songListWidget = SongListWidget(self.playlist, self)
        self.selectionModeBar = PlayingSelectionModeBar(self)
        self.guideLabel = QLabel(self.tr(
            "Here, you will see the song being played and the songs to be played."), self)
        self.randomPlayAllButton = ThreeStatePushButton(
            {
                "normal": ":/images/playing_interface/Shuffle_normal.png",
                "hover": ":/images/playing_interface/Shuffle_hover.png",
                "pressed": ":/images/playing_interface/Shuffle_pressed.png",
            },
            self.tr(" Shuffle all songs in your collection"),
            (30, 22),
            self
        )

        # create animations
        self.playBarAni = QPropertyAnimation(self.playBar, b"pos")
        self.songInfoCardChuteAni = QPropertyAnimation(
            self.songInfoCardChute, b"pos")
        self.songListWidgetAni = QPropertyAnimation(
            self.songListWidget, b"pos")

        # create timer
        self.showPlaylistTimer = QTimer(self)
        self.hidePlaylistTimer = QTimer(self)

        self.__initWidget()

    def __initWidget(self):
        """ initialize widgets """
        self.resize(1100, 870)
        self.currentSmallestModeSize = QSize(340, 340)
        self.setAttribute(Qt.WA_StyledBackground)
        self.guideLabel.move(45, 62)
        self.lyricWidget.move(0, 60)
        self.randomPlayAllButton.move(45, 117)
        self.playBar.move(0, self.height() - self.playBar.height())

        # hide widgets
        self.randomPlayAllButton.hide()
        self.selectionModeBar.hide()
        self.guideLabel.hide()
        self.maskLabel.hide()
        self.playBar.hide()

        self.__setQss()

        # start to blur cover
        if self.playlist:
            self.albumCoverLabel.setCover(self.coverPath)

        self.__connectSignalToSlot()

        # initialize animations
        self.playBarAni.setDuration(350)
        self.songListWidgetAni.setDuration(350)
        self.songListWidgetAni.setEasingCurve(QEasingCurve.InOutQuad)
        self.playBarAni.setEasingCurve(QEasingCurve.InOutQuad)
        self.parallelAniGroup.addAnimation(self.playBarAni)
        self.parallelAniGroup.addAnimation(self.songInfoCardChuteAni)

        # initialize timers
        self.showPlaylistTimer.setInterval(120)
        self.hidePlaylistTimer.setInterval(120)
        self.showPlaylistTimer.timeout.connect(self.showPlaylistTimerSlot)
        self.hidePlaylistTimer.timeout.connect(self.hidePlaylistTimerSlot)

        self.__getLyric()

    def __setQss(self):
        """ set style sheet """
        self.setObjectName("playingInterface")
        self.guideLabel.setObjectName("guideLabel")
        self.randomPlayAllButton.setObjectName("randomPlayAllButton")
        setStyleSheet(self, 'playing_interface')

    @property
    def coverPath(self):
        return self.songInfoCardChute.cards[1].coverPath

    def resizeEvent(self, e):
        super().resizeEvent(e)
        self.albumCoverLabel.setFixedSize(self.size())
        self.albumCoverLabel.adjustCover()
        self.maskLabel.resize(self.size())
        self.songInfoCardChute.resize(self.size())
        self.lyricWidget.resize(
            self.width(), self.height()-258-self.lyricWidget.y())
        self.playBar.resize(self.width(), self.playBar.height())
        self.songListWidget.resize(self.width(), self.height() - 382)

        self.selectionModeBar.resize(
            self.width(), self.selectionModeBar.height())
        self.selectionModeBar.move(
            0, self.height()-self.selectionModeBar.height())

        if self.isPlaylistVisible:
            self.playBar.move(0, 190)
            self.songListWidget.move(0, 382)
            self.songInfoCardChute.move(0, 258 - self.height())
        else:
            self.playBar.move(0, self.height() - self.playBar.height())
            self.songListWidget.move(0, self.height())

    def showPlayBar(self):
        """ show play bar """
        if self.playBar.isVisible():
            return

        self.playBar.show()
        self.songInfoCardChuteAni.setDuration(450)
        self.songInfoCardChuteAni.setEasingCurve(QEasingCurve.OutCubic)
        self.songInfoCardChuteAni.setStartValue(self.songInfoCardChute.pos())
        self.songInfoCardChuteAni.setEndValue(
            QPoint(0, -self.playBar.height() + 68))
        self.songInfoCardChuteAni.start()

    def hidePlayBar(self):
        """ hide play bar """
        if not self.playBar.isVisible() or self.isPlaylistVisible:
            return

        self.playBar.hide()
        self.songInfoCardChuteAni.setEasingCurve(QEasingCurve.OutCirc)
        self.songInfoCardChuteAni.setEndValue(QPoint(0, 0))
        self.songInfoCardChuteAni.setStartValue(
            QPoint(0, -self.playBar.height() + 68))
        self.songInfoCardChuteAni.start()

    def showPlaylist(self):
        """ show playlist """
        if self.songListWidgetAni.state() == QAbstractAnimation.Running:
            return

        self.playBar.showPlaylistButton.setToolTip(
            self.tr('Hide playlist'))
        self.playBar.pullUpArrowButton.setToolTip(self.tr('Hide playlist'))

        self.songInfoCardChuteAni.setDuration(350)
        self.songInfoCardChuteAni.setEasingCurve(QEasingCurve.InOutQuad)
        self.songInfoCardChuteAni.setStartValue(self.songInfoCardChute.pos())
        self.songInfoCardChuteAni.setEndValue(QPoint(0, 258 - self.height()))
        self.playBarAni.setStartValue(self.playBar.pos())
        self.playBarAni.setEndValue(QPoint(0, 190))
        self.songListWidgetAni.setStartValue(self.songListWidget.pos())
        self.songListWidgetAni.setEndValue(
            QPoint(self.songListWidget.x(), 382))

        if self.sender() == self.playBar.showPlaylistButton:
            self.playBar.pullUpArrowButton.timer.start()

        self.playBar.setVisible(len(self.playlist) > 0)
        self.parallelAniGroup.start()
        self.maskLabel.show()
        self.albumCoverLabel.setVisible(len(self.playlist) > 0)
        self.showPlaylistTimer.start()

    def showPlaylistTimerSlot(self):
        """ show playlist timer time out slot """
        self.showPlaylistTimer.stop()
        self.songListWidgetAni.start()
        self.isPlaylistVisible = True

    def hidePlaylistTimerSlot(self):
        """ hide playlist timer time out slot """
        self.hidePlaylistTimer.stop()
        self.parallelAniGroup.start()

    @handleSelectionMode
    def hidePlaylist(self):
        """ hide playlist """
        if self.parallelAniGroup.state() == QAbstractAnimation.Running:
            return

        self.playBar.showPlaylistButton.setToolTip(
            self.tr('Show playlist'))
        self.playBar.pullUpArrowButton.setToolTip(self.tr('Show playlist'))

        self.songInfoCardChuteAni.setDuration(350)
        self.songInfoCardChuteAni.setEasingCurve(QEasingCurve.InOutQuad)
        self.songInfoCardChuteAni.setStartValue(self.songInfoCardChute.pos())
        self.songInfoCardChuteAni.setEndValue(
            QPoint(0, -self.playBar.height() + 68))
        self.playBarAni.setStartValue(QPoint(0, 190))
        self.playBarAni.setEndValue(
            QPoint(0, self.height() - self.playBar.height()))
        self.songListWidgetAni.setStartValue(self.songListWidget.pos())
        self.songListWidgetAni.setEndValue(
            QPoint(self.songListWidget.x(), self.height()))

        if self.sender() is self.playBar.showPlaylistButton:
            self.playBar.pullUpArrowButton.timer.start()

        # self.parallelAniGroup.start()
        self.songListWidgetAni.start()
        self.hidePlaylistTimer.start()
        self.albumCoverLabel.show()
        self.maskLabel.hide()
        self.isPlaylistVisible = False

    def __onShowPlaylistButtonClicked(self):
        """ show playlist button clicked """
        if not self.isPlaylistVisible:
            self.showPlaylist()
        else:
            self.hidePlaylist()

    def setCurrentIndex(self, index):
        """ set currently played song """
        if self.currentIndex == index or index <= -1:
            return

        if index >= len(self.playlist):
            return

        self.lyricWidget.setLoadingState(True)
        self.desktopLyricInterface.updateWindow(self.playlist[index])
        self.currentIndex = index
        self.songListWidget.setCurrentIndex(index)
        # background cover will be updated by songInfoCardChute's signal
        self.songInfoCardChute.setCurrentIndex(index)

    def setPlaylist(self, playlist: List[SongInfo], isResetIndex: bool = True, index=0):
        """ set playing playlist

        Parameters
        ----------
        playlist: List[SongInfo]
            playing playlist

        isResetIndex: bool
            whether to reset index to 0

        index: int
            the index of currently played song
        """
        self.playlist = playlist.copy() if playlist else []
        self.currentIndex = index if isResetIndex else self.currentIndex
        self.songInfoCardChute.setPlaylist(self.playlist, isResetIndex, index)
        self.songListWidget.updateSongCards(self.playlist, isResetIndex, index)
        self.albumCoverLabel.setCover(self.coverPath)
        self.__setGuideLabelHidden(len(playlist) > 0)
        self.__getLyric()

    def setPlay(self, isPlay: bool):
        """ set play state """
        self.playBar.playButton.setPlay(isPlay)
        self.desktopLyricInterface.setPlay(isPlay)

    def __settleDownPlayBar(self):
        """ settle down play bar """
        self.songInfoCardChute.stopSongInfoCardTimer()

    def __startSongInfoCardTimer(self):
        """ restart the timer of song information cards """
        if not self.playBar.volumeSliderWidget.isVisible():
            self.songInfoCardChute.startSongInfoCardTimer()

    def __removeSongFromPlaylist(self, index):
        """ remove a song from playlist """
        n = len(self.playlist)

        if self.currentIndex > index:
            self.currentIndex -= 1
            self.songInfoCardChute.currentIndex -= 1

        elif self.currentIndex == index:
            self.currentIndex -= 1
            self.songInfoCardChute.currentIndex -= 1
            if n > 0:
                songInfo = self.playlist[self.currentIndex]
                self.albumCoverLabel.setCover(getCoverPath(
                    songInfo.singer, songInfo.album, "album_big"))
                self.__getLyric()

        # update song information of song information card
        if n > 0:
            self.songInfoCardChute.cards[1].updateCard(
                self.playlist[self.currentIndex])

            if self.currentIndex == n-1:
                self.songInfoCardChute.cards[-1].hide()
            else:
                self.songInfoCardChute.cards[-1].updateCard(
                    self.playlist[self.currentIndex+1])

            if self.currentIndex == 0:
                self.songInfoCardChute.cards[0].hide()
            else:
                self.songInfoCardChute.cards[0].updateCard(
                    self.playlist[self.currentIndex-1])

        self.removeSongSignal.emit(index)

        if len(self.playlist) == 0:
            self.__setGuideLabelHidden(False)

    @handleSelectionMode
    def clearPlaylist(self):
        """ clear playlist """
        self.playlist.clear()
        self.songListWidget.clearSongCards()
        self.desktopLyricInterface.clear()
        self.__setGuideLabelHidden(False)
        self.playBar.hide()
        self.currentIndex = 0

    def __setGuideLabelHidden(self, isHidden: bool):
        """ set whether to hide guide label """
        self.randomPlayAllButton.setHidden(isHidden)
        self.guideLabel.setHidden(isHidden)
        self.songListWidget.setHidden(not isHidden)
        self.albumCoverLabel.setHidden(not isHidden)
        self.playBar.setHidden(not isHidden)
        self.songInfoCardChute.setHidden(not isHidden)

    def updateSongInfoByIndex(self, index: int, songInfo: SongInfo):
        """ update song information by index """
        self.playlist[index] = songInfo

        # update album cover
        index_ = self.songInfoCardChute.currentIndex
        isDefaultCover = self.albumCoverLabel.coverPath == getCoverPath(
            '', '', "album_big")
        if self.currentIndex != index_ and index == index_ or \
                self.currentIndex == index_ and index_ == 0 or isDefaultCover:
            self.songInfoCardChute.cards[1].updateCard(songInfo)
            self.albumCoverLabel.setCover(getCoverPath(
                songInfo.singer, songInfo.album, "album_big"))

    def updateSongInfo(self, newSongInfo: SongInfo):
        """ update song information """
        self.songListWidget.updateOneSongCard(newSongInfo)
        self.playlist = self.songListWidget.songInfos
        self.songInfoCardChute.playlist = self.playlist

    def updateMultiSongInfos(self, songInfos: List[SongInfo]):
        """ update multi song information """
        self.songListWidget.updateMultiSongCards(songInfos)
        self.playlist = self.songListWidget.songInfos
        self.songInfoCardChute.playlist = self.playlist

    @handleSelectionMode
    def __onShowSmallestPlayInterfaceButtonClicked(self):
        """ show smallest play interface """
        signalBus.fullScreenChanged.emit(False)
        signalBus.showSmallestPlayInterfaceSig.emit()

    def setRandomPlay(self, isRandomPlay: bool):
        """ set whether to play randomly """
        self.playBar.randomPlayButton.setRandomPlay(isRandomPlay)

    def setMute(self, isMute: bool):
        """ set whether to mute """
        self.playBar.volumeButton.setMute(isMute)
        self.playBar.volumeSliderWidget.volumeButton.setMute(isMute)

    def setVolume(self, volume: int):
        """ set volume """
        if self.playBar.volumeSliderWidget.volumeSlider.value() == volume:
            return

        self.playBar.volumeSliderWidget.setVolume(volume)
        self.playBar.volumeButton.setVolumeLevel(volume)

    def setCurrentTime(self, currentTime: int):
        """ set current time in milliseconds """
        self.playBar.setCurrentTime(currentTime)

    def setLyricCurrentTime(self, currentTime: int):
        """ set lyric current time in milliseconds """
        self.lyricWidget.setCurrentTime(currentTime)
        self.desktopLyricInterface.setCurrentTime(
            currentTime, self.playBar.progressSlider.maximum())

    def setFullScreen(self, isFullScreen: int):
        """ set full screen """
        self.playBar.fullScreenButton.setFullScreen(isFullScreen)

    def setLoopMode(self, loopMode: QMediaPlaylist.PlaybackMode):
        """ set loop mode """
        self.playBar.loopModeButton.setLoopMode(loopMode)

    def __onSelectionModeChanged(self, isOpenSelectionMode: bool):
        """ selection mode changed slot """
        self.isInSelectionMode = isOpenSelectionMode
        self.selectionModeBar.setVisible(isOpenSelectionMode)
        self.selectionModeStateChanged.emit(isOpenSelectionMode)

    def __onCancelButtonClicked(self):
        """ selection mode bar cancel button clicked slot """
        self.selectionModeBar.checkAllButton.setCheckedState(
            not self.songListWidget.isAllSongCardsChecked)
        self.songListWidget.unCheckAllSongCards()
        self.selectionModeBar.checkAllButton.setCheckedState(True)

    def __onCheckAllButtonClicked(self):
        """ selection mode bar check all button clicked slot """
        isChecked = not self.songListWidget.isAllSongCardsChecked
        self.songListWidget.setAllChecked(isChecked)
        self.selectionModeBar.checkAllButton.setCheckedState(isChecked)

    def __onSelectionModeBarAlbumButtonClicked(self):
        """ selection mode bar album button clicked slot """
        songCard = self.songListWidget.checkedSongCards[0]
        songCard.setChecked(False)
        signalBus.switchToAlbumInterfaceSig.emit(
            songCard.singer, songCard.album)

    def __onSelectionModeBarDeleteButtonClicked(self):
        """ selection mode bar delete button clicked slot """
        for songCard in self.songListWidget.checkedSongCards.copy():
            songCard.setChecked(False)
            self.songListWidget.removeSongCard(songCard.itemIndex)

    def __onSelectionModeBarPlayButtonClicked(self):
        """ selection mode bar play button clicked slot """
        songCard = self.songListWidget.checkedSongCards[0]
        songCard.setChecked(False)
        self.currentIndexChanged.emit(songCard.itemIndex)

    def __onSelectionModeBarPropertyButtonClicked(self):
        """ selection mode bar property button clicked slot """
        songCard = self.songListWidget.checkedSongCards[0]
        songCard.setChecked(False)
        self.songListWidget.showSongPropertyDialog(songCard.songInfo)

    def __onSelectionModeBarAddToButtonClicked(self):
        """ selection mode bar add to button clicked slot """
        menu = AddToMenu(parent=self)
        btn = self.selectionModeBar.addToButton
        pos = self.selectionModeBar.mapToGlobal(btn.pos())
        x = pos.x()+btn.width()+5
        y = pos.y()+btn.height()//2-(13+38*menu.actionCount())//2
        songInfos = [
            i.songInfo for i in self.songListWidget.checkedSongCards]

        for act in menu.action_list:
            act.triggered.connect(self.exitSelectionMode)

        menu.newPlaylistAct.triggered.connect(
            lambda: signalBus.addSongsToNewCustomPlaylistSig.emit(songInfos))
        menu.addSongsToPlaylistSig.connect(
            lambda name: signalBus.addSongsToCustomPlaylistSig.emit(name, songInfos))
        menu.exec(QPoint(x, y))

    def exitSelectionMode(self):
        """ exit selection mode """
        self.__onCancelButtonClicked()

    def __getLyric(self):
        """ get lyrics of currently played song """
        if not self.playlist:
            return

        songInfo = self.playlist[self.currentIndex]
        if self.getLyricThread.songInfo == songInfo:
            return

        self.lyricWidget.setLoadingState(True)
        self.desktopLyricInterface.updateWindow(songInfo)
        self.getLyricThread.get(songInfo)

    def __reloadLyric(self):
        """ reload lyrics """
        if not self.playlist:
            return

        self.lyricWidget.setLoadingState(True)
        self.getLyricThread.reload()

    def __revealLyricFileInExplorer(self):
        """ reveal lyric file in explorer """
        path = self.getLyricThread.getLyricPath()
        if path.exists():
            showInFolder(path)
        else:
            self.__showMessageDialog(
                self.tr("Open failed"), self.tr("Lyrics file does not exist"))

    def __loadLyricFromFile(self):
        """ load lyric from file """
        path, _ = QFileDialog.getOpenFileName(
            self, self.tr("Open"), "./", self.tr("Lyric files")+"(*.lrc;*.txt;*.json)")
        if not path:
            return

        lyric = Lyric.load(path)
        if lyric.isValid():
            self.lyricWidget.setLoadingState(True)
            lyric.save(self.getLyricThread.getLyricPath())
            self.setLyric(lyric)
        else:
            self.__showMessageDialog(
                self.tr("Parse lyric failed"),
                self.tr("Unable to parse the selected lyrics file")
            )

    def setLyric(self, lyric: Lyric):
        """ set lyric """
        if self.isLyricVisible:
            self.lyricWidget.show()

        # update lyric
        self.lyricWidget.setLyric(lyric)
        self.desktopLyricInterface.setLyric(lyric)

        # update current lyric
        time = self.playBar.progressSlider.value()
        self.lyricWidget.setCurrentTime(time)
        self.desktopLyricInterface.setCurrentTime(
            time, self.playBar.progressSlider.maximum())

    def __onLyricVisibleChanged(self, isVisible: bool):
        """ lyrics visibility changed slot """
        self.lyricWidget.setVisible(isVisible)
        self.isLyricVisible = isVisible

    @writeAudio
    def __embedLyric(self, checked):
        """ embed lyrics to audio file """
        if not self.playlist or not self.lyricWidget.lyric:
            return

        songInfo = self.playlist[self.currentIndex]
        lyric = Lyric.load(self.getLyricThread.getLyricPath(), True)
        if lyric.isValid():
            MetaDataWriter().writeLyric(songInfo.file, lyric)

    def __searchMV(self):
        """ search MV """
        if not self.playlist:
            return

        songInfo = self.playlist[self.currentIndex]
        self.getMvUrlThread.search(songInfo.singer, songInfo.title)

    def __onCrawlMvUrlFinished(self, url: str):
        """ crawl the play url of MV finished slot """
        if not url:
            self.__showMessageDialog(
                self.tr('Unable to find the corresponding MV'),
                self.tr('Sorry, there are no MVs available for the current song'),
            )
            return

        self.switchToVideoInterfaceSig.emit(url)

    def __showMessageDialog(self, title: str, content: str):
        """ show message dialog """
        w = MessageDialog(title, content, self.window())
        w.cancelButton.setText(self.tr("Close"))
        w.yesButton.hide()
        w.exec_()

    def __connectSignalToSlot(self):
        """ connect signal to slot """
        self.getLyricThread.crawlFinished.connect(self.setLyric)
        self.getMvUrlThread.crawlFinished.connect(self.__onCrawlMvUrlFinished)
        self.randomPlayAllButton.clicked.connect(signalBus.randomPlayAllSig)

        # song information chute signal
        self.songInfoCardChute.currentIndexChanged[int].connect(
            self.currentIndexChanged)
        self.songInfoCardChute.currentIndexChanged[str].connect(
            self.albumCoverLabel.setCover)
        self.songInfoCardChute.showPlayBarSignal.connect(self.showPlayBar)
        self.songInfoCardChute.hidePlayBarSignal.connect(self.hidePlayBar)
        self.songInfoCardChute.aniFinished.connect(self.__getLyric)

        # play bar signal
        self.playBar.volumeSliderWidget.volumeSlider.valueChanged.connect(
            signalBus.volumeChanged)
        self.playBar.fullScreenButton.fullScreenChanged.connect(
            signalBus.fullScreenChanged)
        self.playBar.progressSlider.sliderMoved.connect(
            signalBus.progressSliderMoved)
        self.playBar.progressSlider.clicked.connect(
            signalBus.progressSliderMoved)
        self.playBar.lastSongButton.clicked.connect(signalBus.lastSongSig)
        self.playBar.nextSongButton.clicked.connect(signalBus.nextSongSig)
        self.playBar.playButton.clicked.connect(signalBus.togglePlayStateSig)
        self.playBar.desktopLyricButton.lyricVisibleChanged.connect(
            self.desktopLyricInterface.setVisible)
        self.playBar.pullUpArrowButton.clicked.connect(
            self.__onShowPlaylistButtonClicked)
        self.playBar.showPlaylistButton.clicked.connect(
            self.__onShowPlaylistButtonClicked)
        self.playBar.smallPlayModeButton.clicked.connect(
            lambda i: self.__onShowSmallestPlayInterfaceButtonClicked())
        self.playBar.enterSignal.connect(self.__settleDownPlayBar)
        self.playBar.leaveSignal.connect(self.__startSongInfoCardTimer)
        self.playBar.moreActionsMenu.clearPlayListAct.triggered.connect(
            signalBus.clearPlayingPlaylistSig)
        self.playBar.moreActionsMenu.savePlayListAct.triggered.connect(
            lambda: signalBus.addSongsToNewCustomPlaylistSig.emit(self.playlist))
        self.playBar.moreActionsMenu.loadLyricFromFileAct.triggered.connect(
            self.__loadLyricFromFile)
        self.playBar.moreActionsMenu.reloadLyricAct.triggered.connect(
            self.__reloadLyric)
        self.playBar.moreActionsMenu.revealLyricInFolderAct.triggered.connect(
            self.__revealLyricFileInExplorer)
        self.playBar.moreActionsMenu.lyricVisibleChanged.connect(
            self.__onLyricVisibleChanged)
        self.playBar.moreActionsMenu.embedLyricAct.triggered.connect(
            self.__embedLyric)
        self.playBar.moreActionsMenu.movieAct.triggered.connect(
            self.__searchMV)
        self.playBar.moreActionsMenu.locateAct.triggered.connect(
            self.songListWidget.locateCurrentSong)

        # song list widget signal
        self.songListWidget.currentIndexChanged.connect(
            self.currentIndexChanged)
        self.songListWidget.removeSongSig.connect(
            self.__removeSongFromPlaylist)
        self.songListWidget.selectionModeStateChanged.connect(
            self.__onSelectionModeChanged)
        self.songListWidget.checkedNumChanged.connect(
            lambda n: self.selectionModeBar.setPartButtonHidden(n > 1))
        self.songListWidget.isAllCheckedChanged.connect(
            lambda x: self.selectionModeBar.checkAllButton.setCheckedState(not x))

        # selection mode bar signal
        self.selectionModeBar.cancelButton.clicked.connect(
            self.__onCancelButtonClicked)
        self.selectionModeBar.checkAllButton.clicked.connect(
            self.__onCheckAllButtonClicked)
        self.selectionModeBar.playButton.clicked.connect(
            self.__onSelectionModeBarPlayButtonClicked)
        self.selectionModeBar.deleteButton.clicked.connect(
            self.__onSelectionModeBarDeleteButtonClicked)
        self.selectionModeBar.propertyButton.clicked.connect(
            self.__onSelectionModeBarPropertyButtonClicked)
        self.selectionModeBar.albumButton.clicked.connect(
            self.__onSelectionModeBarAlbumButtonClicked)
        self.selectionModeBar.addToButton.clicked.connect(
            self.__onSelectionModeBarAddToButtonClicked)

        # desktop lyric interface signal
        self.desktopLyricInterface.closeButton.clicked.connect(
            lambda: self.playBar.desktopLyricButton.setLyricVisible(False))
