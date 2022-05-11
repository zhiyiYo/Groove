# coding:utf-8
from common.icon import Icon
from common.os_utils import getPlaylistNames
from PyQt5.QtCore import QFile, Qt, pyqtSignal
from PyQt5.QtWidgets import QAction, QMenu


class Menu(QMenu):
    """ Context menu """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.playAct = QAction(self.tr('Play'), self)
        self.addToMenu = AddToMenu(self.tr('Add to'), self)
        self.removeAct = QAction(self.tr('Remove'), self)
        self.moveUpAct = QAction(self.tr('Move up'), self)
        self.moveDownAct = QAction(self.tr('Move down'), self)
        self.showAlbumAct = QAction(self.tr('Show album'), self)
        self.propertyAct = QAction(self.tr('Properties'), self)
        self.selectAct = QAction(self.tr('Select'), self)
        self.action_list = [self.playAct, self.removeAct, self.moveUpAct,
                            self.moveDownAct, self.showAlbumAct, self.propertyAct, self.selectAct]
        self.__initWidget()

    def __initWidget(self):
        """ initialize widgets """
        self.addAction(self.playAct)
        self.addMenu(self.addToMenu)
        self.addActions(self.action_list[1:-1])
        self.addSeparator()
        self.addAction(self.selectAct)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setWindowFlags(
            Qt.FramelessWindowHint | Qt.Popup | Qt.NoDropShadowWindowHint)

        self.setObjectName('playingInterfaceMenu')
        self.addToMenu.setObjectName('blackAddToMenu')
        self.__setQss()

    def __setQss(self):
        """ set style sheet """
        f = QFile(":/qss/menu.qss")
        f.open(QFile.ReadOnly)
        self.setStyleSheet(str(f.readAll(), encoding='utf-8'))
        f.close()


class AddToMenu(QMenu):
    """ Add to menu """

    addSongsToPlaylistSig = pyqtSignal(str)  # 将歌曲添加到已存在的自定义播放列表

    def __init__(self, title='Add to', parent=None):
        super().__init__(title, parent)

        self.playingAct = QAction(
            Icon(':/images/playing_interface/Playing_white.png'), self.tr('Now playing'), self)
        self.newPlaylistAct = QAction(
            Icon(':/images/playing_interface/Add_20_20.png'), self.tr('New playlist'), self)
        names = getPlaylistNames()
        self.playlistActs = [QAction(Icon(
            ":/images/playing_interface/Album.png"), i, self) for i in names]

        self.addAction(self.playingAct)
        self.addSeparator()
        self.addActions([self.newPlaylistAct]+self.playlistActs)
        self.action_list = [self.playingAct,
                            self.newPlaylistAct] + self.playlistActs

        self.setWindowFlags(
            Qt.FramelessWindowHint | Qt.Popup | Qt.NoDropShadowWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)

        for name, act in zip(names, self.playlistActs):
            act.triggered.connect(
                lambda checked, playlistName=name: self.addSongsToPlaylistSig.emit(playlistName))

        self.__setQss()

    def actionCount(self):
        return len(self.action_list)

    def __setQss(self):
        """ set style sheet """
        self.setObjectName('blackAddToMenu')
        f = QFile(":/qss/menu.qss")
        f.open(QFile.ReadOnly)
        self.setStyleSheet(str(f.readAll(), encoding='utf-8'))
        f.close()
