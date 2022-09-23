# coding:utf-8
from common.crawler import SongQuality
from common.icon import Icon, getIconColor
from common.os_utils import getPlaylistNames
from common.signal_bus import signalBus
from common.style_sheet import setStyleSheet
from common.window_effect import WindowEffect
from PyQt5.QtCore import (QEasingCurve, QEvent, QPropertyAnimation, QRect, Qt,
                          pyqtSignal)
from PyQt5.QtWidgets import QAction, QApplication, QMenu


class MenuIconFactory:
    """ Menu icon factory """

    ADD = "Add"
    ALBUM = "Album"
    CANCEL = "Cancel"
    CHEVRON_RIGHT = "ChevronRight"
    CLEAR = "Clear"
    CONTACT = "Contact"
    COPY = "Copy"
    CUT = "Cut"
    FULL_SCREEN = "FullScreen"
    PASTE = "Paste"
    PLAYING = "Playing"
    PLAYLIST = "Playlist"
    LYRIC = "Lyric"
    MOVIE = "Movie"
    BULLSEYE = "Bullseye"
    LOCK = "Lock"
    UNLOCK = "Unlock"
    CLOSE = "Close"
    SETTINGS = "Settings"
    RELOAD = "Reload"
    HIDE = "Hide"
    VIEW = "View"
    FOLDER_SEARCH = "FolderSearch"
    FILE_COMMENT = "FileComment"
    SPEED = "Speed"
    SPEED_UP = "SpeedUp"
    SPEED_DOWN = "SpeedDown"
    SPEED_RESET = "SpeedReset"

    @classmethod
    def create(cls, iconType: str):
        """ create icon """
        path = f":/images/menu/{iconType}_{getIconColor()}.png"
        return Icon(path)


MIF = MenuIconFactory


class AeroMenu(QMenu):
    """ Aero menu """

    def __init__(self, string="", parent=None):
        super().__init__(string, parent)
        self.windowEffect = WindowEffect()
        self.setWindowFlags(
            Qt.FramelessWindowHint | Qt.Popup | Qt.NoDropShadowWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground | Qt.WA_StyledBackground)
        self.setObjectName("AeroMenu")
        setStyleSheet(self, 'menu')

    def event(self, e: QEvent):
        if e.type() == QEvent.WinIdChange:
            self.setMenuEffect()
        return QMenu.event(self, e)

    def setMenuEffect(self):
        """ set menu effect """
        self.windowEffect.setAeroEffect(self.winId())
        self.windowEffect.addMenuShadowEffect(self.winId())


class DWMMenu(QMenu):
    """ A menu with DWM shadow """

    def __init__(self, title="", parent=None):
        super().__init__(title, parent)
        self.windowEffect = WindowEffect()
        self.setWindowFlags(
            Qt.FramelessWindowHint | Qt.Popup | Qt.NoDropShadowWindowHint)
        self.setAttribute(Qt.WA_StyledBackground)
        self.setQss()

    def event(self, e: QEvent):
        if e.type() == QEvent.WinIdChange:
            self.windowEffect.addMenuShadowEffect(self.winId())
        return QMenu.event(self, e)

    def setQss(self):
        """ set style sheet """
        setStyleSheet(self, 'menu')


class AddToMenu(DWMMenu):
    """ Add to menu """

    addSongsToPlaylistSig = pyqtSignal(str)

    def __init__(self, title="Add to", parent=None):
        super().__init__(title, parent)
        self.setObjectName("addToMenu")
        self.createActions()
        self.setQss()

    def createActions(self):
        """ create actions """
        self.playingAct = QAction(
            MIF.create(MIF.PLAYING), self.tr("Now playing"), self)
        self.newPlaylistAct = QAction(
            MIF.create(MIF.ADD), self.tr("New playlist"), self)

        # create actions according to playlists
        names = getPlaylistNames()
        self.playlistNameActs = [
            QAction(MIF.create(MIF.ALBUM), i, self) for i in names]
        self.action_list = [self.playingAct,
                            self.newPlaylistAct] + self.playlistNameActs
        self.addAction(self.playingAct)
        self.addSeparator()
        self.addActions([self.newPlaylistAct] + self.playlistNameActs)

        # connect the signal of playlist to slot
        for name, act in zip(names, self.playlistNameActs):
            act.triggered.connect(
                lambda checked, playlistName=name: self.addSongsToPlaylistSig.emit(playlistName))

    def actionCount(self):
        return len(self.action_list)


class DownloadMenu(DWMMenu):
    """ Download online music menu """

    downloadSig = pyqtSignal(SongQuality)

    def __init__(self, title="Download", parent=None):
        super().__init__(title=title, parent=parent)
        self.standardQualityAct = QAction(self.tr('Standard'), self)
        self.highQualityAct = QAction(self.tr('HQ'), self)
        self.superQualityAct = QAction(self.tr('SQ'), self)
        self.addActions(
            [self.standardQualityAct, self.highQualityAct, self.superQualityAct])
        self.standardQualityAct.triggered.connect(
            lambda: self.downloadSig.emit(SongQuality.STANDARD))
        self.highQualityAct.triggered.connect(
            lambda: self.downloadSig.emit(SongQuality.HIGH))
        self.superQualityAct.triggered.connect(
            lambda: self.downloadSig.emit(SongQuality.SUPER))
        self.setQss()


class LineEditMenu(DWMMenu):
    """ Line edit menu """

    def __init__(self, parent):
        super().__init__("", parent)
        self.setObjectName("lineEditMenu")
        self.animation = QPropertyAnimation(self, b"geometry")
        self.animation.setDuration(300)
        self.animation.setEasingCurve(QEasingCurve.OutQuad)
        self.setQss()

    def createActions(self):
        self.cutAct = QAction(
            MIF.create(MIF.CUT),
            self.tr("Cut"),
            self,
            shortcut="Ctrl+X",
            triggered=self.parent().cut,
        )
        self.copyAct = QAction(
            MIF.create(MIF.COPY),
            self.tr("Copy"),
            self,
            shortcut="Ctrl+C",
            triggered=self.parent().copy,
        )
        self.pasteAct = QAction(
            MIF.create(MIF.PASTE),
            self.tr("Paste"),
            self,
            shortcut="Ctrl+V",
            triggered=self.parent().paste,
        )
        self.cancelAct = QAction(
            MIF.create(MIF.CANCEL),
            self.tr("Cancel"),
            self,
            shortcut="Ctrl+Z",
            triggered=self.parent().undo,
        )
        self.selectAllAct = QAction(
            self.tr("Select all"), self, shortcut="Ctrl+A", triggered=self.parent().selectAll)
        self.action_list = [self.cutAct, self.copyAct,
                            self.pasteAct, self.cancelAct, self.selectAllAct]

    def exec_(self, pos):
        self.clear()
        self.createActions()
        self.setProperty("hasCancelAct", "false")

        if QApplication.clipboard().mimeData().hasText():
            if self.parent().text():
                self.setProperty("hasCancelAct", "true")
                if self.parent().selectedText():
                    self.addActions(self.action_list)
                else:
                    self.addActions(self.action_list[2:])
            else:
                self.addAction(self.pasteAct)
        else:
            if self.parent().text():
                self.setProperty("hasCancelAct", "true")
                if self.parent().selectedText():
                    self.addActions(
                        self.action_list[:2] + self.action_list[3:])
                else:
                    self.addActions(self.action_list[3:])
            else:
                return

        w = 130+max(self.fontMetrics().width(i.text()) for i in self.actions())
        h = len(self.actions()) * 40 + 10

        self.animation.setStartValue(QRect(pos.x(), pos.y(), 1, 1))
        self.animation.setEndValue(QRect(pos.x(), pos.y(), w, h))
        self.setStyle(QApplication.style())

        self.animation.start()
        super().exec_(pos)


class MoreActionsMenu(AeroMenu):
    """ More actions menu """

    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.animation = QPropertyAnimation(self, b"geometry")
        self._createActions()
        self.__initWidget()

    def __initWidget(self):
        """ initialize widgets """
        self.setObjectName("moreActionsMenu")
        self.animation.setDuration(300)
        self.animation.setEasingCurve(QEasingCurve.OutQuad)

    def _createActions(self):
        """ create actions"""
        raise NotImplementedError

    def exec(self, pos):
        h = len(self.actions()) * 38
        w = max(self.fontMetrics().width(i.text())
                for i in self.actions()) + 65
        self.animation.setStartValue(QRect(pos.x(), pos.y(), 1, h))
        self.animation.setEndValue(QRect(pos.x(), pos.y(), w, h))
        self.animation.start()
        super().exec(pos)


class PlayBarMoreActionsMenu(MoreActionsMenu):
    """ Play bar more actions menu """

    def _createActions(self):
        self.savePlayListAct = QAction(
            MIF.create(MIF.ADD), self.tr("Save as a playlist"), self)
        self.clearPlayListAct = QAction(
            MIF.create(MIF.CLEAR), self.tr('Clear now playing'), self)
        self.showPlayListAct = QAction(
            MIF.create(MIF.PLAYLIST), self.tr("Show now playing list"), self)
        self.fullScreenAct = QAction(
            MIF.create(MIF.FULL_SCREEN), self.tr("Go full screen"), self)
        self.addActions([self.showPlayListAct, self.fullScreenAct])

        # play speed submenu
        self.addMenu(PlaySpeedMenu(self.tr("Playback speed"), self))

        self.addActions([self.savePlayListAct, self.clearPlayListAct])


class PlayingInterfaceMoreActionsMenu(MoreActionsMenu):
    """ Playing interface more actions menu """

    lyricVisibleChanged = pyqtSignal(bool)

    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.showLyricAct.setProperty('showLyric', True)
        self.showLyricAct.triggered.connect(self.__onLyricActionTrigger)
        self.adjustSize()

    def __onLyricActionTrigger(self):
        """ lyric action triggered slot """
        isVisible = self.showLyricAct.property('showLyric')
        self.showLyricAct.setProperty('showLyric', not isVisible)
        if isVisible:
            self.showLyricAct.setText(self.tr("Show lyric"))
            self.showLyricAct.setIcon(MIF.create(MIF.VIEW))
        else:
            self.showLyricAct.setText(self.tr("Hide lyric"))
            self.showLyricAct.setIcon(MIF.create(MIF.HIDE))

        self.lyricVisibleChanged.emit(not isVisible)

    def _createActions(self):
        # play speed submenu
        self.addMenu(PlaySpeedMenu(self.tr("Playback speed"), self))

        self.savePlayListAct = QAction(
            MIF.create(MIF.ADD), self.tr("Save as a playlist"), self)
        self.clearPlayListAct = QAction(
            MIF.create(MIF.CLEAR), self.tr('Clear now playing'), self)
        self.locateAct = QAction(
            MIF.create(MIF.BULLSEYE), self.tr('Locate current song'), self)
        self.showLyricAct = QAction(
            MIF.create(MIF.HIDE), self.tr('Hide lyric'), self)
        self.reloadLyricAct = QAction(MIF.create(
            MIF.RELOAD), self.tr("Reload lyric"), self)
        self.revealLyricInFolderAct = QAction(
            MIF.create(MIF.FOLDER_SEARCH), self.tr("Reveal in explorer"), self)
        self.loadLyricFromFileAct = QAction(MIF.create(
            MIF.FILE_COMMENT), self.tr("Use external lyric file"), self)
        self.movieAct = QAction(
            MIF.create(MIF.MOVIE), self.tr('Watch MV'), self)
        self.addActions([
            self.savePlayListAct,
            self.clearPlayListAct,
            self.locateAct,
            self.movieAct
        ])

        # lyric submenu
        self.lyricMenu = DWMMenu(self.tr("Lyric"), self)
        self.lyricMenu.setIcon(MIF.create(MIF.LYRIC))
        self.lyricMenu.addActions([
            self.showLyricAct, self.reloadLyricAct,
            self.loadLyricFromFileAct, self.revealLyricInFolderAct
        ])
        self.addMenu(self.lyricMenu)
        self.lyricMenu.setObjectName("lyricMenu")


class PlaySpeedMenu(DWMMenu):
    """ Play speed menu """

    def __init__(self, title, parent=None):
        super().__init__(title, parent)
        self.setObjectName("playSpeedMenu")
        self.setIcon(MIF.create(MIF.SPEED))

        self.speedUpAct = QAction(MIF.create(
            MIF.SPEED_UP), self.tr("Faster"), self)
        self.speedDownAct = QAction(MIF.create(
            MIF.SPEED_DOWN), self.tr("Slower"), self)
        self.speedResetAct = QAction(MIF.create(
            MIF.SPEED_RESET), self.tr("Normal"), self)
        self.addActions([
            self.speedUpAct, self.speedDownAct, self.speedResetAct])

        self.speedUpAct.triggered.connect(signalBus.playSpeedUpSig)
        self.speedDownAct.triggered.connect(signalBus.playSpeedDownSig)
        self.speedResetAct.triggered.connect(signalBus.playSpeedResetSig)
