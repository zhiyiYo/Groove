# coding:utf-8
from win32.lib import win32con
from win32.win32api import SendMessage
from win32.win32gui import ReleaseCapture

from PyQt5.QtCore import Qt, QEvent
from PyQt5.QtGui import QResizeEvent
from PyQt5.QtWidgets import QLabel, QWidget

from .title_bar_buttons import BasicButton, MaximizeButton


class TitleBar(QWidget):
    """ 定义标题栏 """

    def __init__(self, parent):
        super().__init__(parent)
        self.resize(1360, 40)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.title = QLabel(self.tr("Groove Music"), self)
        self.__createButtons()
        self.__initWidget()

    def __createButtons(self):
        """ 创建各按钮 """
        self.minButton = BasicButton(
            [
                {
                    "normal": ":/images/title_bar/透明黑色最小化按钮_57_40.png",
                    "hover": ":/images/title_bar/绿色最小化按钮_hover_57_40.png",
                    "pressed": ":/images/title_bar/黑色最小化按钮_pressed_57_40.png",
                },
                {
                    "normal": ":/images/title_bar/白色最小化按钮_57_40.png",
                    "hover": ":/images/title_bar/绿色最小化按钮_hover_57_40.png",
                    "pressed": ":/images/title_bar/黑色最小化按钮_pressed_57_40.png",
                },
            ],
            self,
        )
        self.closeButton = BasicButton(
            [
                {
                    "normal": ":/images/title_bar/透明黑色关闭按钮_57_40.png",
                    "hover": ":/images/title_bar/关闭按钮_hover_57_40.png",
                    "pressed": ":/images/title_bar/关闭按钮_pressed_57_40.png",
                },
                {
                    "normal": ":/images/title_bar/透明白色关闭按钮_57_40.png",
                    "hover": ":/images/title_bar/关闭按钮_hover_57_40.png",
                    "pressed": ":/images/title_bar/关闭按钮_pressed_57_40.png",
                },
            ],
            self,
        )
        self.returnButton = BasicButton(
            [
                {
                    "normal": ":/images/title_bar/黑色返回按钮_60_40.png",
                    "hover": ":/images/title_bar/黑色返回按钮_hover_60_40.png",
                    "pressed": ":/images/title_bar/黑色返回按钮_pressed_60_40.png",
                },
                {
                    "normal": ":/images/title_bar/白色返回按钮_60_40.png",
                    "hover": ":/images/title_bar/白色返回按钮_hover_60_40.png",
                    "pressed": ":/images/title_bar/白色返回按钮_pressed_60_40.png",
                },
            ],
            self,
            iconSize_tuple=(60, 40),
        )
        self.maxButton = MaximizeButton(self)
        self.buttons = [self.minButton, self.maxButton,
                        self.closeButton, self.returnButton]

    def __initWidget(self):
        """ 初始化小部件 """
        self.setFixedHeight(40)
        self.title.setObjectName('titleLabel')
        self.setStyleSheet("""
            QWidget{background-color:transparent}
            QLabel{
                font:14px 'Segoe UI Semilight','Microsoft YaHei Light';
                padding:10px 15px 10px 15px;
            }
        """)
        self.title.hide()
        self.returnButton.hide()

        # 将按钮的点击信号连接到槽函数
        self.minButton.clicked.connect(self.window().showMinimized)
        self.maxButton.clicked.connect(self.__showRestoreWindow)
        self.closeButton.clicked.connect(self.window().close)

        # 给返回按钮安装事件过滤器
        self.returnButton.installEventFilter(self)
        self.title.installEventFilter(self)

    def resizeEvent(self, e: QResizeEvent):
        """ 尺寸改变时移动按钮 """
        self.title.move(self.returnButton.isVisible() * 60, 0)
        self.closeButton.move(self.width() - 57, 0)
        self.maxButton.move(self.width() - 2 * 57, 0)
        self.minButton.move(self.width() - 3 * 57, 0)

    def mouseDoubleClickEvent(self, e):
        """ 双击最大化/缩小窗口 """
        self.__showRestoreWindow()

    def mousePressEvent(self, e):
        """ 移动窗口 """
        if self.childAt(e.pos()):
            return

        ReleaseCapture()
        SendMessage(
            self.window().winId(),
            win32con.WM_SYSCOMMAND,
            win32con.SC_MOVE + win32con.HTCAPTION,
            0,
        )
        e.ignore()

    def __showRestoreWindow(self):
        """ 复原窗口并更换最大化按钮的图标 """
        if self.window().isMaximized():
            self.window().showNormal()
            self.maxButton.setMaxState(False)
        else:
            self.window().showMaximized()
            self.maxButton.setMaxState(True)

    def setWhiteIcon(self, isWhiteIcon: bool):
        """ 设置图标颜色 """
        for button in self.buttons:
            button.setWhiteIcon(isWhiteIcon)

    def eventFilter(self, obj, e: QEvent):
        """ 过滤事件 """
        if obj == self.returnButton:
            if e.type() == QEvent.Hide:
                cond = self.title.parent() is not self
                self.title.move(15 * cond, 10 * cond)
            elif e.type() == QEvent.Show:
                self.title.move(
                    self.returnButton.width() + self.title.x(), self.title.y())
        elif obj == self.title:
            if e.type() == QEvent.Show and self.returnButton.isVisible():
                self.title.move(
                    self.returnButton.width() + self.title.y(), self.title.y())

        return super().eventFilter(obj, e)
