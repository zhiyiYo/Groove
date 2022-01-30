# coding:utf-8
from pathlib import Path

from common.os_utils import getPlaylistNames
from PyQt5.QtCore import QFile, Qt, pyqtSignal
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QAction, QMenu


class Menu(QMenu):
    """ 右击菜单 """

    def __init__(self, parent=None):
        super().__init__(parent)
        # 创建动作
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
        # 初始化
        self.__initWidget()

    def __initWidget(self):
        """ 初始化小部件 """
        self.addAction(self.playAct)
        self.addMenu(self.addToMenu)
        self.addActions(self.action_list[1:-1])
        self.addSeparator()
        self.addAction(self.selectAct)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setWindowFlags(
            Qt.FramelessWindowHint | Qt.Popup | Qt.NoDropShadowWindowHint)
        # 分配ID
        self.setObjectName('playingInterfaceMenu')
        self.addToMenu.setObjectName('blackAddToMenu')
        # 设置层叠样式
        self.__setQss()

    def __setQss(self):
        """ 设置层叠样式 """
        f = QFile(":/qss/menu.qss")
        f.open(QFile.ReadOnly)
        self.setStyleSheet(str(f.readAll(), encoding='utf-8'))
        f.close()


class AddToMenu(QMenu):
    """ 添加到菜单 """

    addSongsToPlaylistSig = pyqtSignal(str)  # 将歌曲添加到已存在的自定义播放列表
    playlistFolder = Path('cache/Playlists')

    def __init__(self, title='Add to', parent=None):
        super().__init__(title, parent)

        # 创建动作
        self.playingAct = QAction(
            QIcon(':/images/playing_interface/Playing_white.png'), self.tr('Now playing'), self)
        self.newPlaylistAct = QAction(
            QIcon(':/images/playing_interface/Add_20_20.png'), self.tr('New playlist'), self)
        names = getPlaylistNames()
        self.playlistActs = [QAction(QIcon(
            ":/images/playing_interface/Album.png"), i, self) for i in names]

        self.addAction(self.playingAct)
        self.addSeparator()
        self.addActions([self.newPlaylistAct]+self.playlistActs)
        self.action_list = [self.playingAct,
                            self.newPlaylistAct] + self.playlistActs
        # 取消阴影
        self.setWindowFlags(
            Qt.FramelessWindowHint | Qt.Popup | Qt.NoDropShadowWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)

        # 将添加到播放列表的信号连接到槽函数
        for name, act in zip(names, self.playlistActs):
            act.triggered.connect(
                lambda checked, playlistName=name: self.addSongsToPlaylistSig.emit(playlistName))

        # 设置层叠样式
        self.__setQss()

    def actionCount(self):
        """ 返回菜单中的动作数 """
        return len(self.action_list)

    def __setQss(self):
        """ 设置层叠样式 """
        self.setObjectName('blackAddToMenu')
        f = QFile(":/qss/menu.qss")
        f.open(QFile.ReadOnly)
        self.setStyleSheet(str(f.readAll(), encoding='utf-8'))
        f.close()
