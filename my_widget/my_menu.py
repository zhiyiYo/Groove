import sys

from ctypes.wintypes import HWND

from PyQt5.QtCore import QAbstractAnimation, QEasingCurve, QEvent, Qt, QPropertyAnimation, QRect
from PyQt5.QtGui import QIcon,QPainter,QPen,QColor,QBrush
from PyQt5.QtWidgets import (QAction, QApplication, QGraphicsDropShadowEffect,QHBoxLayout,
                             QMenu, QWidget)
sys.path.append('..')
from Groove.effects.window_effect import WindowEffect



class Menu(QMenu):
    """ 自定义菜单 """
    windowEffect = WindowEffect()

    def __init__(self, string='', parent=None):
        super().__init__(string,parent)
        #self.class_amended = c_bool(False)  
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.Popup | Qt.NoDropShadowWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground|Qt.WA_StyledBackground)
        #self.setAutoFillBackground(False)
        self.setQss()

    def event(self, e: QEvent):
        if e.type() == QEvent.WinIdChange:
            self.hWnd = HWND(int(self.winId()))
            self.setMenuEffect()
        return QMenu.event(self, e)

    def setMenuEffect(self):
        """ 开启特效 """
        self.windowEffect.setAeroEffect(self.hWnd)
        self.windowEffect.addShadowEffect(True,self.hWnd)

    def setQss(self):
        """ 设置层叠样式 """
        with open('resource\\css\\menu.qss', encoding='utf-8') as f:
            self.setStyleSheet(f.read())


class AddToMenu(Menu):
    """ 添加到菜单 """
    def __init__(self, string='添加到', parent=None):
        super().__init__(string, parent)
        # 创建动作
        self.createActions()

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


class LineEditMenu(Menu):
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
        self.selectAllAct = QAction('全选', self, shortcut='Ctrl+A', triggered=self.parent().selectAll)
        # 创建动作列表
        self.action_list = [self.cutAct, self.copyAct, self.pasteAct, self.cancelAct, self.selectAllAct]
        
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
                    self.addActions(self.action_list[:2] + self.action_list[3:])
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
            QRect(pos.x(), pos.y(), 1, height))
        self.animation.setEndValue(
            QRect(pos.x(), pos.y(), width, height))
        self.setStyle(QApplication.style())
        # 开始动画
        self.animation.start()
        super().exec_(pos)
        

class CardContextMenu(Menu):
    """ 专辑卡和歌手卡右击菜单,cardType用于指定卡片类型,0代表歌手卡,1代表专辑卡 """
    def __init__(self,parent,cardType):
        super().__init__('', parent)
        self.__cardType = cardType
        # 创建动作
        self.createActions()
        # 创建动画
        self.animation = QPropertyAnimation(self, b'geometry')
        self.animation.setDuration(300)
        self.animation.setEasingCurve(QEasingCurve.OutQuad)
        self.setObjectName('cardContextMenu')
        
    def createActions(self):
        """ 创建动作 """
        self.addToMenu = AddToMenu('添加到', self)
        self.addToMenu.setObjectName('addToMenu')
        # 创建动作
        self.playAct = QAction('播放', self)
        self.chooseAct = QAction('选择', self)
        self.nextToPlayAct = QAction('下一首播放', self)
        self.pinToStartMenuAct = QAction('固定到"开始"菜单', self)
        # 如果是专辑卡需要多创建3个动作
        if self.__cardType:
            self.deleteAct = QAction('删除', self)
            self.editInfoAct = QAction('编辑信息', self)
            self.showSongerAct = QAction('显示歌手', self)
        
        # 添加动作到菜单
        self.addActions([self.playAct, self.nextToPlayAct])
        self.addMenu(self.addToMenu)
        if self.__cardType:
            self.addActions([self.showSongerAct, self.pinToStartMenuAct,
                            self.editInfoAct, self.deleteAct])
            self.itemNum = 8                
        else:
            self.addAction(self.pinToStartMenuAct)
            self.itemNum = 5
        self.addSeparator()
        self.addAction(self.chooseAct)


    def exec_(self, pos):
        """ 重写exec_() """
        # 补上separator的margin、高度和菜单的边框厚度
        height = 38 * self.itemNum + 10 + 11 + 2
        width = 176
        self.animation.setStartValue(
            QRect(pos.x(), pos.y(), 1, height))
        self.animation.setEndValue(
            QRect(pos.x(), pos.y(), width, height))
        self.animation.start()
        super().exec_(pos)


class SongCardListContextMenu(Menu):
    """ 歌曲卡列表右击菜单 """

    def __init__(self, parent):
        super().__init__('', parent)
        # 创建动作
        self.createActions()

    def createActions(self):
        """ 创建动作 """
        # 创建主菜单动作
        self.playAct = QAction('播放', self)
        self.nextSongAct = QAction('下一首播放', self)
        self.showAlbumAct = QAction('显示专辑', self)
        self.editInfoAct = QAction('编辑信息', self)
        self.showPropertyAct = QAction('属性', self)
        self.deleteAct = QAction('删除', self)
        self.selectAct = QAction('选择', self)
        # 创建菜单和子菜单
        self.addToMenu = AddToMenu('添加到', self)
        # 将动作添加到菜单中
        self.addActions([self.playAct, self.nextSongAct])
        # 将子菜单添加到主菜单
        self.addMenu(self.addToMenu)
        # 将其余动作添加到主菜单
        self.addActions(
            [self.showAlbumAct, self.editInfoAct, self.showPropertyAct, self.deleteAct])
        self.addSeparator()
        self.addAction(self.selectAct)
        self.itemNum = 8
        # 设置菜单的ID
        self.addToMenu.setObjectName('addToMenu')
        self.setObjectName('songCardContextMenu')

