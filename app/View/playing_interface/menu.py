# coding:utf-8
import os

from PyQt5.QtCore import QFile, Qt, pyqtSignal
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QAction, QMenu


class Menu(QMenu):
    """ 右击菜单 """

    def __init__(self, parent=None):
        super().__init__(parent)
        # 创建动作
        self.playAct = QAction('播放', self)
        self.addToMenu = AddToMenu(parent=self)
        self.removeAct = QAction('移除', self)
        self.moveUpAct = QAction('向上移动', self)
        self.moveDownAct = QAction('向下移动', self)
        self.showAlbumAct = QAction('显示专辑', self)
        self.propertyAct = QAction('属性', self)
        self.selectAct = QAction('选择', self)
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

    def __init__(self, string='添加到', parent=None):
        super().__init__(string, parent)
        # 创建动作
        self.playingAct = QAction(
            QIcon(':/images/playing_interface/Playing_white.png'), '正在播放', self)
        self.newPlaylistAct = QAction(
            QIcon(':/images/playing_interface/Add_20_20.png'), '新的播放列表', self)
        playlists = self.__getPlaylistNames()
        self.playlistAct_list = [QAction(QIcon(
            ":/images/playing_interface/Album.png"), i, self) for i in playlists]
        self.addAction(self.playingAct)
        self.addSeparator()
        self.addActions([self.newPlaylistAct]+self.playlistAct_list)
        self.action_list = [self.playingAct,
                            self.newPlaylistAct] + self.playlistAct_list
        # 取消阴影
        self.setWindowFlags(
            Qt.FramelessWindowHint | Qt.Popup | Qt.NoDropShadowWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)
        # 将添加到播放列表的信号连接到槽函数
        for name, act in zip(playlists, self.playlistAct_list):
            act.triggered.connect(
                lambda checked, playlistName=name: self.addSongsToPlaylistSig.emit(playlistName))
        # 设置层叠样式
        self.__setQss()

    def __getPlaylistNames(self):
        """ 扫描播放列表文件夹下的播放列表名字 """
        # 扫描播放列表文件夹下的播放列表名字
        os.makedirs('Playlists', exist_ok=True)
        playlistName_list = [
            i[:-5] for i in os.listdir("Playlists") if i.endswith(".json")]
        return playlistName_list

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
