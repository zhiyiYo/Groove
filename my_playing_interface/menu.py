# coding:utf-8

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QMenu, QAction


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
            Qt.FramelessWindowHint|Qt.Popup|Qt.NoDropShadowWindowHint)
        # 分配ID
        self.setObjectName('playingInterfaceMenu')
        self.addToMenu.setObjectName('blackAddToMenu')
        # 设置层叠样式
        self.__setQss()

    def __setQss(self):
        """ 设置层叠样式 """
        with open(r'resource\css\menu.qss',encoding='utf-8') as f:
            self.setStyleSheet(f.read())


class AddToMenu(QMenu):
    """ 添加到菜单 """

    def __init__(self, string='添加到', parent=None):
        super().__init__(string, parent)
        # 创建动作
        self.createActions()
        self.setWindowFlags(
            Qt.FramelessWindowHint | Qt.Popup | Qt.NoDropShadowWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)

    def createActions(self):
        """ 创建三个动作 """
        self.playingAct = QAction(
            QIcon(r'resource\images\playing_interface\正在播放_white_17_17.png'), '正在播放', self)
        self.newPlayList = QAction(
            QIcon(r'resource\images\playing_interface\新的播放列表_20_20.png'), '新的播放列表', self)
        self.myLove = QAction(
            QIcon(r'resource\images\playing_interface\播放列表_white_20_20.png'), '我喜欢', self)
        self.action_list = [self.playingAct, self.newPlayList, self.myLove]
        self.addAction(self.playingAct)
        self.addSeparator()
        self.addActions([self.newPlayList, self.myLove])
