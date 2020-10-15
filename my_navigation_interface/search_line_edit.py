# coding:utf-8

from PyQt5.QtCore import QEvent, Qt
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import QLineEdit

from my_widget.my_menu import LineEditMenu
from my_widget.my_button import ThreeStateButton


class SearchLineEdit(QLineEdit):
    """ 单行搜索框 """

    def __init__(self, parent=None):
        super().__init__(parent)

        # 按钮图标位置
        clear_iconPath_dict = {
            'normal':
            r'resource\images\searchLineEdit\搜索框清空按钮_normal_45_45.png',
            'hover': r'resource\images\searchLineEdit\搜索框清空按钮_hover_45_45.png',
            'pressed':
            r'resource\images\searchLineEdit\搜索框清空按钮_pressed_45_45.png'
        }
        self.__search_iconPath_dict = {
            'normal':
            r'resource\images\searchLineEdit\搜索框透明搜索按钮_normal_46_45.png',
            'hover':
            r'resource\images\searchLineEdit\搜索框透明搜索按钮_hover_46_45.png',
            'pressed':
            r'resource\images\searchLineEdit\搜索框搜索按钮_pressed_46_45.png'
        }
        # 实例化按钮
        self.clearButton = ThreeStateButton(clear_iconPath_dict, self,
                                            (46, 45))
        self.searchButton = ThreeStateButton(self.__search_iconPath_dict, self,
                                             (46, 45))
        # 实例化右击菜单
        self.menu = LineEditMenu(self)
        # 初始化界面
        self.__initWidget()

    def __initWidget(self):
        """ 初始化小部件 """
        self.resize(370, 45)
        self.clearButton.hide()
        self.setAttribute(Qt.WA_StyledBackground)
        # 设置提示文字
        self.setPlaceholderText('搜索')
        self.textChanged.connect(self.textChangedEvent)
        self.setWindowFlags(Qt.FramelessWindowHint)
        # 设置外边距
        self.setTextMargins(0, 0, self.clearButton.width() +
                            self.searchButton.width(), 0)
        # 调整按钮位置
        self.__adjustButtonPos()
        # 安装监听
        self.clearButton.installEventFilter(self)
        self.searchButton.installEventFilter(self)

    def textChangedEvent(self):
        """ 编辑框的文本改变时选择是否显示清空按钮 """
        if self.text():
            self.clearButton.show()
        else:
            self.clearButton.hide()

    def __adjustButtonPos(self):
        """ 调整按钮的位置 """
        # 需要补上margin的位置
        self.searchButton.move(self.width() - self.searchButton.width() - 8, 0)
        self.clearButton.move(self.searchButton.x() - self.clearButton.width(),
                              0)

    def resizeEvent(self, e):
        """ 调整大小的同时改变按钮位置 """
        self.__adjustButtonPos()

    def mousePressEvent(self, e):
        if e.button() != Qt.LeftButton:
            return
        # 需要调用父类的鼠标点击事件，不然无法部分选中
        super().mousePressEvent(e)
        # 如果输入框中有文本，就设置为只读并显示清空按钮
        if self.text():
            self.clearButton.show()

    def focusOutEvent(self, e):
        """ 当焦点移到别的输入框时隐藏按钮 """
        # 调用父类的函数，消除焦点
        super().focusOutEvent(e)
        self.clearButton.hide()

    def eventFilter(self, obj, e):
        """ 过滤事件 """
        if obj == self.clearButton:
            if e.type() == QEvent.MouseButtonRelease and e.button(
            ) == Qt.LeftButton:
                self.clear()
                self.clearButton.hide()
                return True
        elif obj == self.searchButton:
            if e.type() == QEvent.MouseButtonRelease and e.button(
            ) == Qt.LeftButton:
                self.searchButton.setIcon(
                    QIcon(self.__search_iconPath_dict['hover']))
                return True
        return super().eventFilter(obj, e)

    def contextMenuEvent(self, e):
        """ 设置右击菜单 """
        self.menu.exec_(e.globalPos())
