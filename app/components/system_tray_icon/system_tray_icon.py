# coding:utf-8
from components.widgets.menu import DWMMenu
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QFont, QFontMetrics, QIcon
from PyQt5.QtWidgets import QAction, QApplication, QSystemTrayIcon


class SystemTrayIcon(QSystemTrayIcon):
    """ 系统托盘图标 """

    exitSignal = pyqtSignal()
    lastSongSig = pyqtSignal()
    nextSongSig = pyqtSignal()
    showMainWindowSig = pyqtSignal()
    togglePlayStateSig = pyqtSignal()
    showPlayingInterfaceSig = pyqtSignal()
    switchToSettingInterfaceSig = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.isPlay = False
        self.menu = SystemTrayMenu(parent)
        self.setContextMenu(self.menu)
        self.setIcon(QIcon(':/images/logo/logo_small.png'))
        self.__connectSignalToSlot()

    def __connectSignalToSlot(self):
        """ 信号连接到槽 """
        self.activated.connect(self.__onActivated)
        self.menu.exitAct.triggered.connect(self.exitSignal)
        self.menu.lastSongAct.triggered.connect(self.lastSongSig)
        self.menu.nextSongAct.triggered.connect(self.nextSongSig)
        self.menu.songAct.triggered.connect(self.showPlayingInterfaceSig)
        self.menu.playAct.triggered.connect(self.__onPlayActionTriggered)
        self.menu.settingsAct.triggered.connect(
            self.switchToSettingInterfaceSig)

    def __onActivated(self, reason: QSystemTrayIcon.ActivationReason):
        """ 激活槽函数 """
        if reason == self.Trigger:
            self.showMainWindowSig.emit()

    def setPlay(self, isPlay: bool):
        """ 设置播放状态 """
        if self.isPlay == isPlay:
            return

        self.isPlay = isPlay
        if isPlay:
            self.menu.playAct.setIcon(QIcon(':/images/system_tray/Pause.png'))
            self.menu.playAct.setText(self.tr('Pause'))
        else:
            self.menu.playAct.setIcon(QIcon(':/images/system_tray/Play.png'))
            self.menu.playAct.setText(self.tr('Play'))

    def __onPlayActionTriggered(self):
        """ 播放动作触发槽函数 """
        self.setPlay(not self.isPlay)
        self.togglePlayStateSig.emit()

    def updateWindow(self, songInfo: dict):
        """ 更新窗口 """
        singer = songInfo.get('singer', '')
        songName = songInfo.get('songName', '')
        text = singer + ' - ' + songName
        self.setToolTip(text)

        font = QFont('Microsoft YaHei')
        font.setPixelSize(18)
        fontMetric = QFontMetrics(font)
        self.menu.songAct.setText(
            fontMetric.elidedText(text, Qt.ElideRight, 235))


class SystemTrayMenu(DWMMenu):
    """ 系统托盘菜单 """

    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.songAct = QAction(
            QIcon(':/images/system_tray/Music.png'), '', self)
        self.playAct = QAction(
            QIcon(':/images/system_tray/Play.png'), self.tr('Play'), self)
        self.lastSongAct = QAction(
            QIcon(':/images/system_tray/Previous.png'), self.tr('Last song'), self)
        self.nextSongAct = QAction(
            QIcon(':/images/system_tray/Next.png'), self.tr('Next song'), self)
        self.settingsAct = QAction(
            QIcon(':/images/system_tray/Settings.png'), self.tr('Settings'), self)
        self.exitAct = QAction(
            QIcon(':/images/system_tray/SignOut.png'), self.tr('Exit'), self)
        self.addActions([
            self.songAct, self.playAct, self.lastSongAct, self.nextSongAct])
        self.addSeparator()
        self.addAction(self.settingsAct)
        self.addSeparator()
        self.addAction(self.exitAct)
        self.setObjectName('systemTrayMenu')
        self.setStyle(QApplication.style())
