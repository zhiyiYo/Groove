# coding:utf-8

""" 自定义按钮库"""

import sys

from PyQt5.QtCore import QEvent, QPoint, QSize, Qt, QTimer
from PyQt5.QtGui import (QBrush, QColor, QEnterEvent, QIcon, QPainter, QPen,
                         QPixmap)
from PyQt5.QtWidgets import (QApplication, QGraphicsBlurEffect, QLabel,
                             QPushButton, QToolButton)

sys.path.append('..')
from Groove.my_functions.is_not_leave import isNotLeave


class SongerPlayButton(QPushButton):
    """ 歌手头像上的播放按钮 """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.resize(67, 67)

        # 隐藏边框并将背景设置为透明
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)

        # 设置鼠标进入标志位
        self.enter = False
        # 设置悬浮提醒
        self.customToolTip = None

        # 设置背景图
        self.image = QPixmap('resource\\images\\歌手播放按钮_67_67.png')

    def paintEvent(self, e):
        """ 绘制背景 """
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing, True)
        # 设置画笔
        painter.setPen(Qt.NoPen)
        # 设置背景图
        brush = QBrush(self.image)
        painter.setBrush(brush)
        # 绘制背景图
        if not self.enter:
            painter.drawEllipse(5, 5, 57, 57)
        else:
            painter.drawEllipse(0, 0, 67, 67)

    def setCustomToolTip(self, toolTip, toolTipText: str):
        """ 设置提示条和提示条的位置 """
        self.customToolTip = toolTip
        self.customToolTipText = toolTipText

    def enterEvent(self, e: QEnterEvent):
        """ 鼠标进入按钮时增大按钮并显示提示条 """
        # print('鼠标进入播放按钮')
        self.enter = True
        self.update()
        if self.customToolTip and not self.customToolTip.isVisible():
            self.customToolTip.setText(self.customToolTipText)
            self.customToolTip.move(
                e.globalX() - int(self.customToolTip.width() / 2), e.globalY() - 100)
            self.customToolTip.show()

    def leaveEvent(self, e):
        """ 鼠标离开按钮时减小按钮并隐藏提示条 """
        self.enter = False
        self.update()
        if self.parent() and self.customToolTip:
            notLeave = isNotLeave(self)
            if notLeave:
                return
            self.customToolTip.hide()


class SongerAddToButton(QPushButton):
    """ 歌手头像上的添加到按钮 """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.resize(65, 65)

        # 隐藏边框
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)

        # 设置鼠标进入标志位
        self.enter = False
        # 设置悬浮提醒
        self.customToolTip = None

        # 设置背景图
        self.image = QPixmap('resource\\images\\歌手添加到按钮_65_65.png')

    def paintEvent(self, e):
        """ 绘制背景 """
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing, True)
        # 设置画笔
        painter.setPen(Qt.NoPen)
        # 设置背景图
        brush = QBrush(self.image)
        painter.setBrush(brush)
        # 绘制背景图
        if not self.enter:
            painter.drawEllipse(4, 4, 57, 57)
        else:
            painter.drawEllipse(0, 0, 65, 65)

    def setCustomToolTip(self, toolTip, toolTipText: str):
        """ 设置提示条和提示条的位置 """
        self.customToolTip = toolTip
        self.customToolTipText = toolTipText

    def enterEvent(self, e):
        """ 鼠标进入按钮时增大按钮并显示提示条 """
        # print('鼠标进入播放按钮')
        self.enter = True
        self.update()
        if self.customToolTip and not self.customToolTip.isVisible():
            self.customToolTip.setText(self.customToolTipText)
            self.customToolTip.move(
                e.globalX() - int(self.customToolTip.width() / 2), e.globalY() - 100)
            self.customToolTip.show()

    def leaveEvent(self, e):
        """ 鼠标离开按钮时减小按钮并隐藏提示条 """
        self.enter = False
        self.update()
        if self.parent() and self.customToolTip:
            notLeave = isNotLeave(self)
            if notLeave:
                return
            self.customToolTip.hide()


class SongCardPlayButton(QToolButton):
    """ 定义歌曲卡播放按钮 """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedSize(61, 61)
        self.setObjectName('playButton')
        self.setIcon(QIcon('resource\\images\\songCard\\black_play_bt.png'))
        self.setIconSize(QSize(61, 61))


class SongCardAddToButton(QToolButton):
    """ 定义歌曲卡添加到按钮 """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setFixedSize(61, 61)
        self.setObjectName('addToButton')
        self.setIcon(QIcon('resource\\images\\songCard\\black_addTo_bt.png'))
        self.setIconSize(QSize(61, 61))


class RandomPlayButton(QPushButton):
    """ 定义条形随机播放按钮 """

    def __init__(self, text='', slot=None, parent=None):
        super().__init__(text, parent)
        self.setIcon(QIcon('resource\\images\\无序播放所有_130_17.png'))
        self.setIconSize(QSize(130, 17))
        self.setCursor(Qt.PointingHandCursor)
        self.setObjectName('randomPlayButton')
        self.clicked.connect(slot)
        self.installEventFilter(self)

    def eventFilter(self, obj, e):
        """ 当鼠标移到播放模式按钮上时更换图标 """
        if obj == self:
            if e.type() == QEvent.Enter or e.type() == QEvent.HoverMove:
                self.setIcon(
                    QIcon('resource\\images\\无序播放所有_hover_130_17.png'))
            elif e.type() == QEvent.Leave:
                self.setIcon(QIcon('resource\\images\\无序播放所有_130_17.png'))
        return False


class SortModeButton(QPushButton):
    """ 定义排序模式按钮 """

    def __init__(self, text, slot, parent=None):
        super().__init__(text, parent)
        self.setCursor(Qt.PointingHandCursor)
        self.setObjectName('sortModeButton')
        self.clicked.connect(slot)
        
class NavigationButton(QPushButton):
    """ 侧边导航栏按钮 """

    def __init__(self, icon_path, text='', parent=None, buttonSize: tuple = (60, 60), iconSize: tuple = (60, 60)):
        super().__init__(text, parent)
        self.image = QPixmap(icon_path)
        self.iconSizeTuple = iconSize
        self.buttonSizeTuple = buttonSize
        self.initWidget()

    def initWidget(self):
        """ 初始化小部件 """
        # 设置按钮的图标
        self.setFixedSize(self.buttonSizeTuple[0], self.buttonSizeTuple[1])
        self.setIconSize(QSize(self.iconSizeTuple[0], self.iconSizeTuple[1]))
        # 设置属性防止qss不起作用
        self.setAttribute(Qt.WA_StyledBackground | Qt.WA_TranslucentBackground)
        
        # 初始化属性
        self.setProperty('selected', 'false')
        self.setProperty('clickedAgain','false')

                               
    def mousePressEvent(self,e):
        """ 鼠标点击时更新样式 """
        if self.property('clickedAgain')=='true':
            self.update()
        super().mousePressEvent(e)

    def paintEvent(self, e):
        """ 选中时在左边绘制选中标志 """
        super().paintEvent(e)
        painter = QPainter(self)
        painter.setPen(Qt.NoPen)
        # 绘制图标
        brush = QBrush(self.image)
        painter.setBrush(brush)
        painter.drawRect(0, 0, self.iconSizeTuple[0], self.iconSizeTuple[1])
        if self.property('selected') == 'true':
            pen = QPen(QColor(0, 107, 133))
            pen.setWidth(10)
            painter.setPen(pen)
            if self.property('clickedAgain')=='false':
                """ 为什么总是差5 """
                painter.drawLine(0, 6, 0, self.height() - 6)
            else:
                painter.drawLine(1, 7, 1, self.height - 7)

        

class LineEditButton(QToolButton):
    """ 单行编辑框按钮，iconPath_dict提供按钮normal、hover、selected三种状态下的图标地址 """

    def __init__(self, iconPath_dict:dict, parent=None,icon_size:tuple=(40,40)):
        super().__init__(parent)
        # 引用图标地址字典
        self.iconPath_dict = iconPath_dict
        self.resize(icon_size[0],icon_size[1])
        # 初始化小部件
        self.initWidget()
        
    def initWidget(self):
        """ 初始化小部件 """
        self.setCursor(Qt.ArrowCursor)
        self.setIcon(QIcon(self.iconPath_dict['normal']))
        self.setIconSize(QSize(self.width(),self.height()))
        self.setStyleSheet('border: none; margin: 0px')

    def enterEvent(self,e):
        """ hover时更换图标 """
        self.setIcon(QIcon(self.iconPath_dict['hover']))

    def leaveEvent(self, e):
        """ leave时更换图标 """
        self.setIcon(QIcon(self.iconPath_dict['normal']))

    def mousePressEvent(self, e):
        """ 鼠标左键按下时更换图标 """
        if e.button() == Qt.RightButton:
            return
        self.setIcon(QIcon(self.iconPath_dict['selected']))


if __name__ == "__main__":
    app = QApplication(sys.argv)
    demo = SongCardAddToButton()
    demo.show()
    sys.exit(app.exec_())
