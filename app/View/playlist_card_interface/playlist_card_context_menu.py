# coding:utf-8

from PyQt5.QtWidgets import QAction, QMenu

from app.components.menu import AcrylicMenu, AddToMenu


class PlaylistCardContextMenu(AcrylicMenu):
    """ 播放列表卡右击菜单 """

    def __init__(self, string="", parent=None, acrylicColor="e5e5e5C0"):
        super().__init__(string, parent, acrylicColor)
        # 创建动作
        self.__createActions()
        self.setObjectName("playlistCardContextMenu")
        self.setQss()

    def __createActions(self):
        """ 创建动作 """
        # 创建动作
        self.playAct = QAction("播放", self)
        self.nextToPlayAct = QAction("下一首播放", self)
        self.addToMenu = AddToMenu("添加到", self)
        self.renameAct = QAction("重命名", self)
        self.pinToStartMenuAct = QAction('固定到"开始"菜单', self)
        self.deleteAct = QAction("删除", self)
        self.selectAct = QAction("选择", self)

        # 添加动作到菜单
        self.addActions([self.playAct, self.nextToPlayAct])
        # 将子菜单添加到主菜单
        self.addMenu(self.addToMenu)
        self.addActions([self.renameAct, self.pinToStartMenuAct, self.deleteAct])
        self.addSeparator()
        self.addAction(self.selectAct)
