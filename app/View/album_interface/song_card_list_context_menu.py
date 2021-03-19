# coding:utf-8

from PyQt5.QtWidgets import QAction

from app.components.menu import AcrylicMenu, AddToMenu


class SongCardListContextMenu(AcrylicMenu):
    """ 歌曲卡列表右击菜单 """

    def __init__(self, parent):
        super().__init__("", parent)
        self.setFixedWidth(128)
        # 创建动作
        self.createActions()

    def createActions(self):
        """ 创建动作 """
        # 创建主菜单动作
        self.playAct = QAction("播放", self)
        self.nextSongAct = QAction("下一首播放", self)
        self.editInfoAct = QAction("编辑信息", self)
        self.showPropertyAct = QAction("属性", self)
        self.deleteAct = QAction("删除", self)
        self.selectAct = QAction("选择", self)
        # 创建菜单和子菜单
        self.addToMenu = AddToMenu("添加到", self)
        # 将动作添加到菜单中
        self.addActions([self.playAct, self.nextSongAct])
        # 将子菜单添加到主菜单
        self.addMenu(self.addToMenu)
        # 将其余动作添加到主菜单
        self.addActions([self.editInfoAct, self.showPropertyAct, self.deleteAct])
        self.addSeparator()
        self.addAction(self.selectAct)
