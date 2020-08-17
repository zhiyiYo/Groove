import sys
from ctypes.wintypes import HWND

from PyQt5.QtCore import (QAbstractAnimation, QEasingCurve, QEvent,
                          QPropertyAnimation, QRect, Qt)
from PyQt5.QtGui import QBrush, QColor, QIcon, QPainter, QPen
from PyQt5.QtWidgets import (QAction, QApplication, QGraphicsDropShadowEffect,
                             QHBoxLayout, QMenu, QWidget)

from effects.window_effect import WindowEffect


class AeroMenu(QMenu):
    """ Aero菜单 """
    windowEffect = WindowEffect()

    def __init__(self, string='', parent=None):
        super().__init__(string, parent)
        self.setWindowFlags(Qt.FramelessWindowHint |
                            Qt.Popup | Qt.NoDropShadowWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground | Qt.WA_StyledBackground)
        self.setObjectName('AeroMenu')
        self.setQss()

    def event(self, e: QEvent):
        if e.type() == QEvent.WinIdChange:
            self.hWnd = HWND(int(self.winId()))
            self.setMenuEffect()
        return QMenu.event(self, e)

    def setMenuEffect(self):
        """ 开启特效 """
        self.windowEffect.setAeroEffect(self.hWnd)
        self.windowEffect.addShadowEffect(self.hWnd)

    def setQss(self):
        """ 设置层叠样式 """
        with open('resource\\css\\menu.qss', encoding='utf-8') as f:
            self.setStyleSheet(f.read())


class AcrylicMenu(QMenu):
    """ 亚克力菜单 """
    windowEffect = WindowEffect()

    def __init__(self, string='', parent=None,acrylicColor='e5e5e5C0'):
        super().__init__(string, parent)
        self.acrylicColor = acrylicColor
        self.__initWidget()

    def event(self, e: QEvent):
        if e.type() == QEvent.WinIdChange:
            self.hWnd = HWND(int(self.winId()))
            self.windowEffect.setAcrylicEffect(self.hWnd, self.acrylicColor, True)
        return QMenu.event(self, e)

    def __initWidget(self):
        """ 初始化菜单 """
        self.setAttribute(Qt.WA_StyledBackground)
        self.setWindowFlags(Qt.FramelessWindowHint |
                            Qt.Popup | Qt.NoDropShadowWindowHint)
        self.setProperty('effect','acrylic')
        self.setObjectName('acrylicMenu')
        self.setQss()

    def setQss(self):
        """ 设置层叠样式 """
        with open('resource\\css\\menu.qss', encoding='utf-8') as f:
            self.setStyleSheet(f.read())


class AddToMenu(AcrylicMenu):
    """ 添加到菜单 """

    def __init__(self, string='添加到', parent=None,acrylicColor='e5e5e5C0'):
        super().__init__(string, parent,acrylicColor)
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
        self.myLove = QAction(
            QIcon('resource\\images\\menu\\黑色我喜欢_20_20.png'), '我喜欢', self)
        self.action_list = [self.playingAct, self.newPlayList, self.myLove]
        self.addAction(self.playingAct)
        self.addSeparator()
        self.addActions([self.newPlayList, self.myLove])

    def connectToSlots(self, slot_list: list):
        """ 将触发信号连接到槽函数 """
        for i in range(3):
            self.action_list[i].triggered.connect(slot_list[i])



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


class CardContextMenu(AcrylicMenu):
    """ 专辑卡和歌手卡右击菜单,cardType用于指定卡片类型,0代表歌手卡,1代表专辑卡 """

    def __init__(self, parent, cardType):
        super().__init__('', parent)
        self.__cardType = cardType
        self.setAttribute(Qt.WA_StyledBackground)
        # 创建动作
        self.createActions()

    def createActions(self):
        """ 创建动作 """
        # 创建动作
        self.playAct = QAction('播放', self)
        self.chooseAct = QAction('选择', self)
        self.nextToPlayAct = QAction('下一首播放', self)
        self.pinToStartMenuAct = QAction('固定到"开始"菜单', self)
        self.addToMenu = AddToMenu(parent=self)
        # 如果是专辑卡需要多创建3个动作
        if self.__cardType:
            self.setFixedWidth(166)
            self.deleteAct = QAction('删除', self)
            self.editInfoAct = QAction('编辑信息', self)
            self.showSongerAct = QAction('显示歌手', self)

        # 添加动作到菜单
        self.addActions([self.playAct, self.nextToPlayAct])
        self.addMenu(self.addToMenu)
        if self.__cardType:
            self.addActions([self.showSongerAct, self.pinToStartMenuAct,
                             self.editInfoAct, self.deleteAct])
        else:
            self.addAction(self.pinToStartMenuAct)
        self.addSeparator()
        self.addAction(self.chooseAct)
