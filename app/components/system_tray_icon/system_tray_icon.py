# coding:utf-8
from common.icon import getIconColor
from common.database.entity import SongInfo
from common.signal_bus import signalBus
from components.widgets.menu import MIF, DWMMenu
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QFont, QFontMetrics, QIcon
from PyQt5.QtWidgets import QAction, QApplication, QSystemTrayIcon


class SystemTrayIcon(QSystemTrayIcon):
    """ System tray icon """

    exitSignal = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.isPlay = False
        self.menu = SystemTrayMenu(parent)
        self.setContextMenu(self.menu)
        self.setIcon(QIcon(':/images/logo/logo_tray.png'))
        self.clearPlaylist()
        self.__connectSignalToSlot()

    def __connectSignalToSlot(self):
        """ connect signal to slot """
        self.activated.connect(self.__onActivated)
        self.menu.exitAct.triggered.connect(self.exitSignal)
        self.menu.lastSongAct.triggered.connect(signalBus.lastSongSig)
        self.menu.nextSongAct.triggered.connect(signalBus.nextSongSig)
        self.menu.songAct.triggered.connect(signalBus.switchToPlayingInterfaceSig)
        self.menu.playAct.triggered.connect(self.__onPlayActionTriggered)
        self.menu.settingsAct.triggered.connect(
            signalBus.switchToSettingInterfaceSig)

    def __onActivated(self, reason: QSystemTrayIcon.ActivationReason):
        """ system tray icon activated slot """
        if reason == self.Trigger:
            signalBus.showMainWindowSig.emit()

    def setPlay(self, isPlay: bool):
        """ set play state """
        if self.isPlay == isPlay:
            return

        self.isPlay = isPlay
        c = getIconColor()
        if isPlay:
            self.menu.playAct.setIcon(MIF.icon(MIF.PAUSE))
            self.menu.playAct.setText(self.tr('Pause'))
        else:
            self.menu.playAct.setIcon(MIF.icon(MIF.PLAY))
            self.menu.playAct.setText(self.tr('Play'))

    def __onPlayActionTriggered(self):
        """ play action triggered slot """
        self.setPlay(not self.isPlay)
        signalBus.togglePlayStateSig.emit()

    def updateWindow(self, songInfo: SongInfo):
        """ update window """
        singer = songInfo.singer or ''
        songName = songInfo.title or ''
        text = singer + ' - ' + songName
        self.setToolTip(text)

        font = QFont('Microsoft YaHei')
        font.setPixelSize(18)
        fontMetric = QFontMetrics(font)
        self.menu.songAct.setText(
            fontMetric.elidedText(text, Qt.ElideRight, 235))

    def clearPlaylist(self):
        """ clear playlist """
        text = self.tr('No songs are playing')
        self.setToolTip(text)
        self.menu.songAct.setText(text)


class SystemTrayMenu(DWMMenu):
    """ System tray menu """

    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.songAct = QAction(
            MIF.icon(MIF.MUSIC_NOTE), self.tr('No songs are playing'), self)
        self.playAct = QAction(
            MIF.icon(MIF.PLAY), self.tr('Play'), self)
        self.lastSongAct = QAction(
            MIF.icon(MIF.PREVIOUS), self.tr('Last song'), self)
        self.nextSongAct = QAction(
            MIF.icon(MIF.NEXT), self.tr('Next song'), self)
        self.settingsAct = QAction(
            MIF.icon(MIF.SETTINGS), self.tr('Settings'), self)
        self.exitAct = QAction(
            MIF.icon(MIF.SIGN_OUT), self.tr('Exit'), self)
        self.addActions([
            self.songAct, self.playAct, self.lastSongAct, self.nextSongAct])
        self.addSeparator()
        self.addAction(self.settingsAct)
        self.addSeparator()
        self.addAction(self.exitAct)
        self.setObjectName('systemTrayMenu')
        self.setStyle(QApplication.style())
