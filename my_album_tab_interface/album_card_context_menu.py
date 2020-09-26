# coding:utf-8

from PyQt5.QtWidgets import QAction,QMenu

from my_widget.my_menu import AcrylicMenu, AddToMenu


class AlbumCardContextMenu(AcrylicMenu):
    """ 专辑卡右击菜单"""

    def __init__(self, parent):
        super().__init__('', parent)
        self.setFixedWidth(173)
        # 创建动作
        self.__createActions()
        self.setObjectName('albumCardContextMenu')
        self.setQss()

    def __createActions(self):
        """ 创建动作 """
        # 创建动作
        self.playAct = QAction('播放', self)
        self.selectAct = QAction('选择', self)
        self.nextToPlayAct = QAction('下一首播放', self)
        self.pinToStartMenuAct = QAction('固定到"开始"菜单', self)
        self.deleteAct = QAction('删除', self)
        self.editInfoAct = QAction('编辑信息', self)
        self.showSongerAct = QAction('显示歌手', self)
        self.addToMenu = AddToMenu('添加到', self)
        
        # 添加动作到菜单
        self.addActions([self.playAct, self.nextToPlayAct])
        # 将子菜单添加到主菜单
        self.addMenu(self.addToMenu)
        self.addActions([self.showSongerAct, self.pinToStartMenuAct,
                         self.editInfoAct, self.deleteAct])
        self.addSeparator()
        self.addAction(self.selectAct)


    