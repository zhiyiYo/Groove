# coding:utf-8
from components.buttons.three_state_button import ThreeStateButton
from components.menu import LineEditMenu
from PyQt5.QtCore import QEvent, Qt
from PyQt5.QtGui import QIcon, QKeyEvent
from PyQt5.QtWidgets import QLineEdit


class SearchLineEdit(QLineEdit):
    """ 单行搜索框 """

    def __init__(self, parent=None):
        super().__init__(parent)

        # 按钮图标位置
        clear_iconPath_dict = {
            "normal": ":/images/navigation_interface/clear_normal.png",
            "hover": ":/images/navigation_interface/clear_hover.png",
            "pressed": ":/images/navigation_interface/clear_pressed.png",
        }
        self.__search_iconPath_dict = {
            "normal": ":/images/navigation_interface/search_normal_46_45.png",
            "hover": ":/images/navigation_interface/search_hover_46_45.png",
            "pressed": ":/images/navigation_interface/search_pressed_46_45.png",
        }
        # 实例化按钮
        self.clearButton = ThreeStateButton(
            clear_iconPath_dict, self, (46, 45))
        self.searchButton = ThreeStateButton(
            self.__search_iconPath_dict, self, (46, 45))
        # 实例化右击菜单
        self.menu = LineEditMenu(self)
        # 初始化界面
        self.__initWidget()

    def __initWidget(self):
        """ 初始化小部件 """
        self.clearButton.hide()
        self.setAttribute(Qt.WA_StyledBackground)
        # 设置提示文字
        self.setPlaceholderText("搜索")
        self.textChanged.connect(self.__onTextChanged)
        # 设置外边距
        self.setTextMargins(
            0, 0, self.clearButton.width() + self.searchButton.width(), 0)
        # 调整按钮位置
        self.resize(370, 45)
        # 安装监听
        self.clearButton.installEventFilter(self)
        self.searchButton.installEventFilter(self)

    def __onTextChanged(self, text):
        """ 编辑框的文本改变时选择是否显示清空按钮 """
        self.clearButton.setVisible(bool(text))

    def resizeEvent(self, e):
        """ 调整大小的同时改变按钮位置 """
        self.searchButton.move(self.width() - self.searchButton.width() - 8, 0)
        self.clearButton.move(self.searchButton.x() -
                              self.clearButton.width(), 0)

    def mousePressEvent(self, e):
        if e.button() != Qt.LeftButton:
            return
        # 需要调用父类的鼠标点击事件，不然无法部分选中
        super().mousePressEvent(e)
        # 如果输入框中有文本，就设置为只读并显示清空按钮
        if self.text():
            self.clearButton.show()

    def keyPressEvent(self, e: QKeyEvent):
        super().keyPressEvent(e)
        if e.key() in [Qt.Key_Enter, Qt.Key_Return]:
            self.searchButton.click()

    def focusOutEvent(self, e):
        """ 当焦点移到别的输入框时隐藏按钮 """
        # 调用父类的函数，消除焦点
        super().focusOutEvent(e)
        self.clearButton.hide()

    def eventFilter(self, obj, e):
        """ 过滤事件 """
        if obj == self.clearButton:
            if e.type() == QEvent.MouseButtonRelease and e.button() == Qt.LeftButton:
                self.clear()
                self.clearButton.hide()
                return True
        elif obj == self.searchButton:
            if e.type() == QEvent.MouseButtonRelease and e.button() == Qt.LeftButton:
                self.searchButton.setIcon(
                    QIcon(self.__search_iconPath_dict["hover"]))
                return False
        return super().eventFilter(obj, e)

    def contextMenuEvent(self, e):
        """ 设置右击菜单 """
        self.menu.exec_(e.globalPos())
