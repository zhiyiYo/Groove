# coding:utf-8

import os

from PyQt5.QtCore import QEasingCurve, QPropertyAnimation, QRect, Qt, QEvent
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QAction, QMenu

from app.common.window_effect import WindowEffect


class MoreActionsMenu(QMenu):
    """ 更多操作菜单 """

    def __init__(self, parent=None):
        super().__init__(parent)
        # 添加动画
        self.animation = QPropertyAnimation(self, b"geometry")
        # 创建窗口效果实例
        self.windowEffect = WindowEffect()
        self.__initWidget()

    def __initWidget(self):
        """ 初始化小部件 """
        self.setWindowFlags(
            Qt.FramelessWindowHint | Qt.Popup | Qt.NoDropShadowWindowHint
        )
        self.setObjectName("albumInterfaceMoreActionMenu")
        self.animation.setDuration(300)
        self.animation.setEasingCurve(QEasingCurve.OutQuad)
        # 设置层叠样式
        self.__setQss()

    def event(self, e: QEvent):
        if e.type() == QEvent.WinIdChange:
            # self.hWnd = HWND(int(self.winId()))
            self.windowEffect.addShadowEffect(self.winId())
        return QMenu.event(self, e)

    def __setQss(self):
        """ 设置层叠样式 """
        with open("app/resource/css/menu.qss", encoding="utf-8") as f:
            self.setStyleSheet(f.read())

    def setActionNum(self, actionNum):
        """ 设置动作的个数 """
        self.clear()
        self.actionNum = actionNum
        self.action_list = []
        self.deleteAct = QAction("删除", self)
        self.action_list.append(self.deleteAct)
        if actionNum >= 2:
            self.editInfoAct = QAction("编辑信息", self)
            self.action_list.append(self.editInfoAct)
            if actionNum == 3:
                self.pinToStartMenuAct = QAction('固定到"开始"菜单', self)
                self.action_list.append(self.pinToStartMenuAct)
        self.addActions(self.action_list[::-1])
        self.currentWidth = [120, 120, 168][self.actionNum - 1]
        self.currentHeight = self.actionNum * 38 + 10

    def exec(self, pos):
        """ 显示菜单 """
        self.animation.setStartValue(
            QRect(pos.x(), pos.y(), 1, self.currentHeight))
        self.animation.setEndValue(
            QRect(pos.x(), pos.y(), self.currentWidth, self.currentHeight)
        )
        # 开始动画
        self.animation.start()
        super().exec(pos)


class AddToMenu(QMenu):
    """ 添加到菜单 """

    def __init__(self, parent=None):
        super().__init__(parent=None)
        # 添加动画
        self.animation = QPropertyAnimation(self, b"geometry")
        # 创建动作
        self.createActions()
        self.__initWidget()

    def __initWidget(self):
        """ 初始化小部件 """
        self.setWindowFlags(
            Qt.FramelessWindowHint | Qt.Popup | Qt.NoDropShadowWindowHint
        )
        self.setObjectName("albumInterfaceAddToMenu")
        self.animation.setDuration(300)
        self.animation.setEasingCurve(QEasingCurve.OutQuad)
        # 设置层叠样式
        self.__setQss()

    def event(self, e: QEvent):
        if e.type() == QEvent.WinIdChange:
            # self.hWnd = HWND(int(self.winId()))
            self.windowEffect.addShadowEffect(self.winId())
        return QMenu.event(self, e)

    def createActions(self):
        """ 创建三个动作 """
        self.playingAct = QAction(
            QIcon("app/resource/images/menu/正在播放.png"), "正在播放", self)
        self.newPlaylistAct = QAction(
            QIcon("app/resource/images/menu/黑色加号.png"), "新的播放列表", self)
        # 根据播放列表创建动作
        playlistName_list = self.__getPlaylistNames()
        self.playlistNameAct_list = [
            QAction(QIcon(r"app\resource\images\menu\黑色我喜欢_20_20.png"), name, self)
            for name in playlistName_list
        ]
        self.action_list = [
            self.playingAct,
            self.newPlaylistAct,
        ] + self.playlistNameAct_list
        self.addAction(self.playingAct)
        self.addSeparator()
        self.addActions([self.newPlaylistAct] + self.playlistNameAct_list)

    def __getPlaylistNames(self):
        """ 扫描播放列表文件夹下的播放列表名字 """
        # 扫描播放列表文件夹下的播放列表名字
        if not os.path.exists("app/Playlists"):
            os.mkdir("app/Playlists")
        playlistName_list = [
            os.path.splitext(i)[0] for i in os.listdir("app/Playlists")
        ]
        return playlistName_list

    def __setQss(self):
        """ 设置层叠样式 """
        with open("app/resource/css/menu.qss", encoding="utf-8") as f:
            self.setStyleSheet(f.read())

    def exec(self, pos):
        """ 显示菜单 """
        self.animation.setStartValue(QRect(pos.x(), pos.y(), 1, 141))
        self.animation.setEndValue(QRect(pos.x(), pos.y(), 170, 141))
        # 开始动画
        self.animation.start()
        super().exec(pos)
