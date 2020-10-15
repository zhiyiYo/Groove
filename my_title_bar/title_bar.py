# coding:utf-8

from win32.lib import win32con
from win32.win32api import SendMessage
from win32.win32gui import ReleaseCapture

from PyQt5.QtCore import Qt, QEvent
from PyQt5.QtGui import QIcon, QPixmap, QResizeEvent
from PyQt5.QtWidgets import QLabel, QWidget

from .title_bar_buttons import BasicButton, MaximizeButton


class TitleBar(QWidget):
    """ 定义标题栏 """

    def __init__(self, parent):
        super().__init__(parent)
        self.resize(1360, 40)
        # 创建记录下标的列表，里面的每一个元素为元组，第一个元素为stackWidget名字，第二个为Index
        self.stackWidgetIndex_list = []
        # 实例化无边框窗口函数类
        self.setAttribute(Qt.WA_TranslucentBackground)
        # 实例化小部件
        self.title = QLabel('MyGroove 音乐', self)
        self.__createButtons()
        # 初始化界面
        self.__initWidget()
        self.__adjustButtonPos()

    def __createButtons(self):
        """ 创建各按钮 """
        self.minBt = BasicButton([
            {'normal': r'resource\images\titleBar\透明黑色最小化按钮_57_40.png',
             'hover': r'resource\images\titleBar\绿色最小化按钮_hover_57_40.png',
             'pressed': r'resource\images\titleBar\黑色最小化按钮_pressed_57_40.png'},
            {'normal': r'resource\images\titleBar\白色最小化按钮_57_40.png',
             'hover': r'resource\images\titleBar\绿色最小化按钮_hover_57_40.png',
             'pressed': r'resource\images\titleBar\黑色最小化按钮_pressed_57_40.png'}], self)
        self.closeBt = BasicButton([
            {'normal': r'resource\images\titleBar\透明黑色关闭按钮_57_40.png',
             'hover': r'resource\images\titleBar\关闭按钮_hover_57_40.png',
             'pressed': r'resource\images\titleBar\关闭按钮_pressed_57_40.png'},
            {'normal': r'resource\images\titleBar\透明白色关闭按钮_57_40.png',
             'hover': r'resource\images\titleBar\关闭按钮_hover_57_40.png',
             'pressed': r'resource\images\titleBar\关闭按钮_pressed_57_40.png'}], self)
        self.returnBt = BasicButton([
            {'normal': r'resource\images\titleBar\黑色返回按钮_60_40.png',
             'hover': r'resource\images\titleBar\黑色返回按钮_hover_60_40.png',
             'pressed': r'resource\images\titleBar\黑色返回按钮_pressed_60_40.png'},
            {'normal': r'resource\images\titleBar\白色返回按钮_60_40.png',
             'hover': r'resource\images\titleBar\白色返回按钮_hover_60_40.png',
             'pressed': r'resource\images\titleBar\白色返回按钮_pressed_60_40.png'}], self, iconSize_tuple=(60, 40))
        self.maxBt = MaximizeButton(self)
        self.button_list = [self.minBt, self.maxBt,
                            self.closeBt, self.returnBt]

    def __initWidget(self):
        """ 初始化小部件 """
        self.setFixedHeight(40)
        self.setStyleSheet("QWidget{background-color:transparent}\
                            QLabel{font:14px 'Microsoft YaHei Light'; padding:10px 15px 10px 15px;}")
        # 隐藏抬头
        self.title.hide()
        # 将按钮的点击信号连接到槽函数
        self.minBt.clicked.connect(self.window().showMinimized)
        self.maxBt.clicked.connect(self.__showRestoreWindow)
        self.closeBt.clicked.connect(self.window().close)
        # 给返回按钮安装事件过滤器
        self.returnBt.installEventFilter(self)
        self.title.installEventFilter(self)
        self.returnBt.hide()

    def __adjustButtonPos(self):
        """ 初始化小部件位置 """
        self.title.move(self.returnBt.isVisible()*60, 0)
        self.closeBt.move(self.width() - 57, 0)
        self.maxBt.move(self.width() - 2 * 57, 0)
        self.minBt.move(self.width() - 3 * 57, 0)

    def resizeEvent(self, e: QResizeEvent):
        """ 尺寸改变时移动按钮 """
        self.__adjustButtonPos()

    def mouseDoubleClickEvent(self, event):
        """ 双击最大化窗口 """
        self.__showRestoreWindow()

    def mousePressEvent(self, event):
        """ 移动窗口 """
        # 判断鼠标点击位置是否允许拖动
        if self.__isPointInDragRegion(event.pos()):
            ReleaseCapture()
            SendMessage(self.window().winId(), win32con.WM_SYSCOMMAND,
                        win32con.SC_MOVE + win32con.HTCAPTION, 0)
            event.ignore()
            # 也可以通过调用windowEffect.dll的接口函数来实现窗口拖动
            # self.windowEffect.moveWindow(HWND(int(self.parent().winId())))

    def __showRestoreWindow(self):
        """ 复原窗口并更换最大化按钮的图标 """
        if self.window().isMaximized():
            self.window().showNormal()
            # 更新标志位用于更换图标
            self.maxBt.setMaxState(False)
        else:
            self.window().showMaximized()
            self.maxBt.setMaxState(True)

    def __isPointInDragRegion(self, pos) -> bool:
        """ 检查鼠标按下的点是否属于允许拖动的区域 """
        x = pos.x()
        left = 60 if self.returnBt.isVisible() else 0
        # 如果最小化按钮看不见也意味着最大化按钮看不见
        right = self.width() - 57 * 3 if self.minBt.isVisible() else self.width() - 57
        return (left < x < right)

    def setWhiteIcon(self, isWhiteIcon: bool):
        """ 设置图标颜色 """
        for button in self.button_list:
            button.setWhiteIcon(isWhiteIcon)

    def eventFilter(self, obj, e: QEvent):
        """ 过滤事件 """
        if obj == self.returnBt:
            if e.type() == QEvent.Hide:
                cond = not (self.title.parent() is self)
                self.title.move(15 * cond, 10 * cond)
            elif e.type() == QEvent.Show:
                self.title.move(self.returnBt.width() +
                                self.title.x(), self.title.y())
        elif obj == self.title:
            if e.type() == QEvent.Show and self.returnBt.isVisible():
                self.title.move(self.returnBt.width() +
                                self.title.y(), self.title.y())
        return super().eventFilter(obj, e)
