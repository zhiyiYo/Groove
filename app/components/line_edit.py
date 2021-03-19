# coding:utf-8
from app.components.buttons.three_state_button import ThreeStateButton
from app.components.menu import LineEditMenu
from PyQt5.QtCore import QEvent, Qt
from PyQt5.QtGui import QContextMenuEvent
from PyQt5.QtWidgets import QHBoxLayout, QLineEdit


class LineEdit(QLineEdit):
    """ 包含清空按钮的单行输入框 """

    def __init__(self, string=None, parent=None, isNeedClearBt: bool = True):
        super().__init__(string, parent)
        self.isNeedClearBt = isNeedClearBt
        # 设置提示条和鼠标点击次数
        self.customToolTip = None
        self.clickedTime = 0
        iconPath_dict = {
            "normal": r"app\resource\images\lineEdit\clearInfo_cross_normal.png",
            "hover": r"app\resource\images\lineEdit\clearInfo_cross_hover.png",
            "pressed": r"app\resource\images\lineEdit\clearInfo_cross_pressed.png",
        }

        # 实例化一个用于清空内容的按钮
        self.clearButton = ThreeStateButton(iconPath_dict, self)
        # 实例化右击菜单
        self.menu = LineEditMenu(self)
        # 实例化布局
        self.h_layout = QHBoxLayout()
        self.initWidget()

    def initWidget(self):
        """ 初始化小部件 """
        self.resize(500, 40)
        self.clearButton.hide()
        self.textChanged.connect(self.textChangedEvent)
        self.clearButton.move(self.width() - self.clearButton.width(), 0)
        if self.isNeedClearBt:
            self.setTextMargins(0, 0, self.clearButton.width(), 0)
        # 安装事件过滤器
        self.clearButton.installEventFilter(self)

    def mousePressEvent(self, e):
        if e.button() == Qt.LeftButton:
            # 如果已经全选了再次点击就取消全选
            if self.clickedTime == 0:
                self.selectAll()
            else:
                # 需要调用父类的鼠标点击事件，不然无法部分选中
                super().mousePressEvent(e)
            self.setFocus()
            # 如果输入框中有文本，就设置为只读并显示清空按钮
            if self.text() and self.isNeedClearBt:
                self.clearButton.show()
        self.clickedTime += 1

    def contextMenuEvent(self, e: QContextMenuEvent):
        """ 设置右击菜单 """
        self.menu.exec_(e.globalPos())

    def focusOutEvent(self, e):
        """ 当焦点移到别的输入框时隐藏按钮 """
        # 调用父类的函数，消除焦点
        super().focusOutEvent(e)
        self.clickedTime = 0
        self.clearButton.hide()

    def textChangedEvent(self):
        """ 如果输入框中文本改变且此时清空按钮不可见，就显示清空按钮 """
        if self.text() and not self.clearButton.isVisible() and self.isNeedClearBt:
            self.clearButton.show()

    def resizeEvent(self, e):
        """ 改变大小时需要移动按钮的位置 """
        self.clearButton.move(self.width() - self.clearButton.width(), 0)

    def eventFilter(self, obj, e):
        """ 清空按钮按下时清空内容并隐藏按钮 """
        if obj == self.clearButton:
            if e.type() == QEvent.MouseButtonRelease and e.button() == Qt.LeftButton:
                self.clear()
                self.clearButton.hide()
                return True
        return super().eventFilter(obj, e)
