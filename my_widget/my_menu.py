# coding:utf-8

import os

from PyQt5.QtCore import (QAbstractAnimation, QEasingCurve, QEvent,
                          QPropertyAnimation, QRect, Qt, pyqtSignal)
from PyQt5.QtGui import QBrush, QColor, QIcon, QPainter, QPen
from PyQt5.QtWidgets import (QAction, QApplication, QGraphicsDropShadowEffect,
                             QHBoxLayout, QMenu, QWidget)

from effects.window_effect import WindowEffect


class AeroMenu(QMenu):
    """ Aero菜单 """

    def __init__(self, string='', parent=None):
        super().__init__(string, parent)
        self.setWindowFlags(Qt.FramelessWindowHint |
                            Qt.Popup | Qt.NoDropShadowWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground | Qt.WA_StyledBackground)
        self.setObjectName('AeroMenu')
        self.setQss()

    def event(self, e: QEvent):
        if e.type() == QEvent.WinIdChange:
            self.setMenuEffect()
        return QMenu.event(self, e)

    def setMenuEffect(self):
        """ 开启特效 """
        WindowEffect.setAeroEffect(self.winId())
        WindowEffect.addShadowEffect(self.winId())

    def setQss(self):
        """ 设置层叠样式 """
        with open('resource\\css\\menu.qss', encoding='utf-8') as f:
            self.setStyleSheet(f.read())


class AcrylicMenu(QMenu):
    """ 亚克力菜单 """

    def __init__(self, string='', parent=None, acrylicColor='e5e5e5CC'):
        super().__init__(string, parent)
        self.acrylicColor = acrylicColor
        self.__initWidget()

    def event(self, e: QEvent):
        if e.type() == QEvent.WinIdChange:
            WindowEffect.setAcrylicEffect(
                self.winId(), self.acrylicColor, True)
        return QMenu.event(self, e)

    def __initWidget(self):
        """ 初始化菜单 """
        self.setAttribute(Qt.WA_StyledBackground)
        self.setWindowFlags(Qt.FramelessWindowHint |
                            Qt.Popup | Qt.NoDropShadowWindowHint)
        self.setProperty('effect', 'acrylic')
        self.setObjectName('acrylicMenu')
        self.setQss()

    def setQss(self):
        """ 设置层叠样式 """
        with open('resource\\css\\menu.qss', encoding='utf-8') as f:
            self.setStyleSheet(f.read())


class AddToMenu(AcrylicMenu):
    """ 添加到菜单 """
    addSongsToPlaylistSig = pyqtSignal(str)  # 将歌曲添加到已存在的自定义播放列表

    def __init__(self, string='添加到', parent=None, acrylicColor='e5e5e5C0'):
        super().__init__(string, parent, acrylicColor)
        self.setObjectName('addToMenu')
        # 创建动作
        self.createActions()
        self.setQss()

    def createActions(self):
        """ 创建三个动作 """
        self.playingAct = QAction(
            QIcon('resource\\images\\menu\\正在播放.png'), '正在播放', self)
        self.newPlayList = QAction(
            QIcon('resource\\images\\menu\\黑色加号.png'), '新的播放列表', self)
        # 根据播放列表创建动作
        playlistName_list = self.__getPlaylistNames()
        self.playlistNameAct_list = [
            QAction(QIcon(r'resource\images\menu\黑色我喜欢_20_20.png'), name, self) for name in playlistName_list]
        self.action_list = [self.playingAct,
                            self.newPlayList] + self.playlistNameAct_list
        self.addAction(self.playingAct)
        self.addSeparator()
        self.addActions([self.newPlayList] + self.playlistNameAct_list)
        # 将添加到播放列表的信号连接到槽函数
        for name, playlistNameAct in zip(playlistName_list, self.playlistNameAct_list):
            # lambda表达式只有在执行的时候才回去寻找变量name，所以需要将name固定下来
            playlistNameAct.triggered.connect(
                lambda checked, playlistName=name: self.addSongsToPlaylistSig.emit(playlistName))

    def __getPlaylistNames(self):
        """ 扫描播放列表文件夹下的播放列表名字 """
        # 扫描播放列表文件夹下的播放列表名字
        if not os.path.exists('Playlists'):
            os.mkdir('Playlists')
        playlistName_list = [i[:-5] for i in os.listdir('Playlists') if i.endswith('.json')]
        return playlistName_list

    def actionCount(self):
        """ 返回菜单中的动作数 """
        return len(self.action_list)


class LineEditMenu(AeroMenu):
    """ 单行输入框右击菜单 """

    def __init__(self, parent):
        super().__init__('', parent)
        # 不能直接改width
        self.animation = QPropertyAnimation(self, b'geometry')
        self.initWidget()

    def initWidget(self):
        """ 初始化小部件 """
        self.setObjectName('lineEditMenu')
        self.animation.setDuration(300)
        self.animation.setEasingCurve(QEasingCurve.OutQuad)
        self.setQss()

    def createActions(self):
        # 创建动作
        self.cutAct = QAction(
            QIcon('resource\\images\\menu\\黑色剪刀.png'), '剪切', self, shortcut='Ctrl+X', triggered=self.parent().cut)
        self.copyAct = QAction(
            QIcon('resource\\images\\menu\\黑色复制.png'), '复制', self, shortcut='Ctrl+C', triggered=self.parent().copy)
        self.pasteAct = QAction(
            QIcon('resource\\images\\menu\\黑色粘贴.png'), '粘贴', self, shortcut='Ctrl+V', triggered=self.parent().paste)
        self.cancelAct = QAction(
            QIcon('resource\\images\\menu\\黑色撤销.png'), '取消操作', self, shortcut='Ctrl+Z', triggered=self.parent().undo)
        self.selectAllAct = QAction(
            '全选', self, shortcut='Ctrl+A', triggered=self.parent().selectAll)
        # 创建动作列表
        self.action_list = [self.cutAct, self.copyAct,
                            self.pasteAct, self.cancelAct, self.selectAllAct]

    def exec_(self, pos):
        # 删除所有动作
        self.clear()
        # clear之后之前的动作已不再存在故需重新创建
        self.createActions()
        # 初始化属性
        self.setProperty('hasCancelAct', 'false')
        width = 176
        actionNum = len(self.action_list)
        # 访问系统剪贴板
        self.clipboard = QApplication.clipboard()
        # 根据剪贴板内容是否为text分两种情况讨论
        if self.clipboard.mimeData().hasText():
            # 再根据3种情况分类讨论
            if self.parent().text():
                self.setProperty('hasCancelAct', 'true')
                width = 213
                if self.parent().selectedText():
                    self.addActions(self.action_list)
                else:
                    self.addActions(self.action_list[2:])
                    actionNum -= 2
            else:
                self.addAction(self.pasteAct)
                actionNum = 1
        else:
            if self.parent().text():
                self.setProperty('hasCancelAct', 'true')
                width = 213
                if self.parent().selectedText():
                    self.addActions(
                        self.action_list[:2] + self.action_list[3:])
                    actionNum -= 1
                else:
                    self.addActions(self.action_list[3:])
                    actionNum -= 3
            else:
                return
        # 每个item的高度为38px，10为上下的内边距和
        height = actionNum * 38 + 10
        # 不能把初始的宽度设置为0px，不然会报警
        self.animation.setStartValue(
            QRect(pos.x(), pos.y(), 1, 1))
        self.animation.setEndValue(
            QRect(pos.x(), pos.y(), width, height))
        self.setStyle(QApplication.style())
        # 开始动画
        self.animation.start()
        super().exec_(pos)