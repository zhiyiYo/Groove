# coding:utf-8
from common.config import config
from common.database.entity import SongInfo
from common.icon import Icon
from common.signal_bus import signalBus
from components.widgets.menu import DWMMenu
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QFont, QFontMetrics, QIcon
from PyQt5.QtWidgets import QAction, QApplication, QSystemTrayIcon


class SystemTrayIcon(QSystemTrayIcon):
    """ System tray icon """

    exitSignal = pyqtSignal()
    showMainWindowSig = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.isPlay = False
        self.menu = SystemTrayMenu(parent)
        self.setContextMenu(self.menu)
        self.setIcon(QIcon(':/images/logo/logo_small.png'))
        self.clearPlaylist()
        self.__connectSignalToSlot()

    def __connectSignalToSlot(self):
        """ connect signal to slot """
        self.activated.connect(self.__onActivated)
        self.menu.exitAct.triggered.connect(self.exitSignal)
        self.menu.lastSongAct.triggered.connect(signalBus.lastSongSig)
        self.menu.nextSongAct.triggered.connect(signalBus.nextSongSig)
        self.menu.songAct.triggered.connect(signalBus.showPlayingInterfaceSig)
        self.menu.playAct.triggered.connect(self.__onPlayActionTriggered)
        self.menu.settingsAct.triggered.connect(
            signalBus.switchToSettingInterfaceSig)

    def __onActivated(self, reason: QSystemTrayIcon.ActivationReason):
        """ system tray icon activated slot """
        if reason == self.Trigger:
            self.showMainWindowSig.emit()

    def setPlay(self, isPlay: bool):
        """ set play state """
        if self.isPlay == isPlay:
            return

        self.isPlay = isPlay
        c = 'white' if config.theme == 'dark' else 'black'
        if isPlay:
            self.menu.playAct.setIcon(Icon(f':/images/system_tray/Pause_{c}.png'))
            self.menu.playAct.setText(self.tr('Pause'))
        else:
            self.menu.playAct.setIcon(Icon(f':/images/system_tray/Play_{c}.png'))
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
        c = 'white' if config.theme == 'dark' else 'black'
        self.songAct = QAction(
            Icon(f':/images/system_tray/Music_{c}.png'), self.tr('No songs are playing'), self)
        self.playAct = QAction(
            Icon(f':/images/system_tray/Play_{c}.png'), self.tr('Play'), self)
        self.lastSongAct = QAction(
            Icon(f':/images/system_tray/Previous_{c}.png'), self.tr('Last song'), self)
        self.nextSongAct = QAction(
            Icon(f':/images/system_tray/Next_{c}.png'), self.tr('Next song'), self)
        self.settingsAct = QAction(
            Icon(f':/images/system_tray/Settings_{c}.png'), self.tr('Settings'), self)
        self.exitAct = QAction(
            Icon(f':/images/system_tray/SignOut_{c}.png'), self.tr('Exit'), self)
        self.addActions([
            self.songAct, self.playAct, self.lastSongAct, self.nextSongAct])
        self.addSeparator()
        self.addAction(self.settingsAct)
        self.addSeparator()
        self.addAction(self.exitAct)
        self.setObjectName('systemTrayMenu')
        self.setStyle(QApplication.style())
