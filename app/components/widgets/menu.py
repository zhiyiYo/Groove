# coding:utf-8
from common.icon import Icon
from common.os_utils import getPlaylistNames
from common.window_effect import WindowEffect
from PyQt5.QtCore import (QEasingCurve, QEvent, QFile, QPropertyAnimation,
                          QRect, Qt, pyqtSignal)
from PyQt5.QtWidgets import QAction, QApplication, QMenu


class AeroMenu(QMenu):
    """ Aero menu """

    def __init__(self, string="", parent=None):
        super().__init__(string, parent)
        self.windowEffect = WindowEffect()
        self.setWindowFlags(
            Qt.FramelessWindowHint | Qt.Popup | Qt.NoDropShadowWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground | Qt.WA_StyledBackground)
        self.setObjectName("AeroMenu")
        self.setQss()

    def event(self, e: QEvent):
        if e.type() == QEvent.WinIdChange:
            self.setMenuEffect()
        return QMenu.event(self, e)

    def setMenuEffect(self):
        """ set menu effect """
        self.windowEffect.setAeroEffect(self.winId())
        self.windowEffect.addMenuShadowEffect(self.winId())

    def setQss(self):
        """ set style sheet """
        f = QFile(":/qss/menu.qss")
        f.open(QFile.ReadOnly)
        self.setStyleSheet(str(f.readAll(), encoding='utf-8'))
        f.close()


class AcrylicMenu(QMenu):
    """ Acrylic menu """

    def __init__(self, string="", parent=None, acrylicColor="e5e5e5CC"):
        super().__init__(string, parent)
        self.acrylicColor = acrylicColor
        self.windowEffect = WindowEffect()
        self.__initWidget()

    def event(self, e: QEvent):
        if e.type() == QEvent.WinIdChange:
            self.windowEffect.setAcrylicEffect(
                self.winId(), self.acrylicColor, True)
        return QMenu.event(self, e)

    def __initWidget(self):
        """ initialize widgets """
        self.setAttribute(Qt.WA_StyledBackground)
        self.setWindowFlags(
            Qt.FramelessWindowHint | Qt.Popup | Qt.NoDropShadowWindowHint)
        self.setProperty("effect", "acrylic")
        self.setObjectName("acrylicMenu")
        self.setQss()

    def setQss(self):
        """ set style sheet """
        f = QFile(":/qss/menu.qss")
        f.open(QFile.ReadOnly)
        self.setStyleSheet(str(f.readAll(), encoding='utf-8'))
        f.close()


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
        f = QFile(":/qss/menu.qss")
        f.open(QFile.ReadOnly)
        self.setStyleSheet(str(f.readAll(), encoding='utf-8'))
        f.close()


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
            Icon(":/images/menu/Playing.png"), self.tr("Now playing"), self)
        self.newPlaylistAct = QAction(
            Icon(":/images/menu/Add.png"), self.tr("New playlist"), self)

        # create actions according to playlists
        names = getPlaylistNames()
        self.playlistNameActs = [
            QAction(Icon(":/images/menu/Album.png"), i, self) for i in names]
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

    downloadSig = pyqtSignal(str)

    def __init__(self, title="Download", parent=None):
        super().__init__(title=title, parent=parent)
        self.standardQualityAct = QAction(self.tr('Standard'), self)
        self.highQualityAct = QAction(self.tr('HQ'), self)
        self.superQualityAct = QAction(self.tr('SQ'), self)
        self.addActions(
            [self.standardQualityAct, self.highQualityAct, self.superQualityAct])
        self.standardQualityAct.triggered.connect(
            lambda: self.downloadSig.emit('Standard quality'))
        self.highQualityAct.triggered.connect(
            lambda: self.downloadSig.emit('High quality'))
        self.superQualityAct.triggered.connect(
            lambda: self.downloadSig.emit('Super quality'))
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
            Icon(":/images/menu/Cut.png"),
            self.tr("Cut"),
            self,
            shortcut="Ctrl+X",
            triggered=self.parent().cut,
        )
        self.copyAct = QAction(
            Icon(":/images/menu/Copy.png"),
            self.tr("Copy"),
            self,
            shortcut="Ctrl+C",
            triggered=self.parent().copy,
        )
        self.pasteAct = QAction(
            Icon(":/images/menu/Paste.png"),
            self.tr("Paste"),
            self,
            shortcut="Ctrl+V",
            triggered=self.parent().paste,
        )
        self.cancelAct = QAction(
            Icon(":/images/menu/Cancel.png"),
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
        self.action_list = []
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
        h = len(self.action_list) * 38
        w = max(self.fontMetrics().width(i.text())
                for i in self.action_list) + 65
        self.animation.setStartValue(QRect(pos.x(), pos.y(), 1, h))
        self.animation.setEndValue(QRect(pos.x(), pos.y(), w, h))
        self.animation.start()
        super().exec(pos)


class PlayBarMoreActionsMenu(MoreActionsMenu):
    """ Play bar more actions menu """

    def _createActions(self):
        self.savePlayListAct = QAction(
            Icon(":/images/menu/Add.png"), self.tr("Save as a playlist"), self)
        self.clearPlayListAct = QAction(
            Icon(":/images/menu/Clear.png"), self.tr('Clear now playing'), self)
        self.showPlayListAct = QAction(
            Icon(":/images/menu/Playlist.png"), self.tr("Show now playing list"), self)
        self.fullScreenAct = QAction(
            Icon(":/images/menu/FullScreen.png"), self.tr("Go full screen"), self)
        self.action_list = [self.showPlayListAct, self.fullScreenAct,
                            self.savePlayListAct, self.clearPlayListAct]
        self.addActions(self.action_list)


class PlayingInterfaceMoreActionsMenu(MoreActionsMenu):
    """ Playing interface more actions menu """

    lyricVisibleChanged = pyqtSignal(bool)

    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.lyricAct.setProperty('showLyric', True)
        self.lyricAct.triggered.connect(self.__onLyricActionTrigger)
        self.adjustSize()

    def __onLyricActionTrigger(self):
        """ lyric action triggered slot """
        isVisible = self.lyricAct.property('showLyric')
        self.lyricAct.setProperty('showLyric', not isVisible)
        self.lyricAct.setText(
            self.tr('Show lyric') if isVisible else self.tr('Hide lyric'))

        self.lyricVisibleChanged.emit(not isVisible)

    def _createActions(self):
        self.savePlayListAct = QAction(
            Icon(":/images/menu/Add.png"), self.tr("Save as a playlist"), self)
        self.clearPlayListAct = QAction(
            Icon(":/images/menu/Clear.png"), self.tr('Clear now playing'), self)
        self.lyricAct = QAction(
            Icon(':/images/menu/Lyric.png'), self.tr('Hide lyric'), self)
        self.movieAct = QAction(
            Icon(':/images/menu/Movie.png'), self.tr('Watch MV'), self)
        self.action_list = [
            self.savePlayListAct,
            self.clearPlayListAct,
            self.lyricAct,
            self.movieAct
        ]
        self.addActions(self.action_list)
