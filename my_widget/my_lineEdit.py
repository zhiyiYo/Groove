import sys

from PyQt5.QtCore import QEvent, QSize, Qt
from PyQt5.QtGui import QContextMenuEvent, QFont, QIcon
from PyQt5.QtWidgets import (QAction, QApplication, QHBoxLayout, QLineEdit,
                             QToolButton)

from my_functions.is_not_leave import isNotLeave
from my_widget.my_button import ThreeStateButton
from my_widget.my_menu import LineEditMenu, Menu


class LineEdit(QLineEdit):
    """ 定义一个被点击就全选文字的单行输入框 """

    def __init__(self, string=None, parent=None):
        super().__init__(string, parent)

        # 设置提示条和鼠标点击次数
        self.customToolTip = None
        self.clickedTime = 0
        iconPath_dict = {
            'normal': r'resource\images\lineEdit\clearInfo_cross_normal.png',
            'hover': r'resource\images\lineEdit\clearInfo_cross_hover.png',
            'pressed': r'resource\images\lineEdit\clearInfo_cross_pressed.png'}

        # 实例化一个用于清空内容的按钮
        self.clearButton = ThreeStateButton(iconPath_dict, self)
        # 实例化右击菜单
        self.menu = LineEditMenu(self)

        # 实例化布局
        self.h_layout = QHBoxLayout()
        self.initWidget()


    def initWidget(self):
        """ 初始化小部件 """
        self.resize(500,40)
        self.clearButton.hide()
        self.textChanged.connect(self.textChangedEvent)
        self.clearButton.move(self.width() - self.clearButton.width(), 0)
        self.setTextMargins(0, 0, self.clearButton.width(), 0)
        # 安装事件过滤器
        self.clearButton.installEventFilter(self)

    def mousePressEvent(self, e):
        if e.button()==Qt.LeftButton:
            # 如果已经全选了再次点击就取消全选
            if self.clickedTime == 0:
                self.selectAll()
            else:
                # 需要调用父类的鼠标点击事件，不然无法部分选中
                super().mousePressEvent(e)
            self.setFocus()
            # 如果输入框中有文本，就设置为只读并显示清空按钮
            if self.text():
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

    def enterEvent(self, e):
        """ 鼠标进入时显示提示条 """
        if self.customToolTip:
            self.customToolTip.setText(self.customToolTipText)
            self.customToolTip.move(e.globalX() - int(self.customToolTip.width() / 2),
                                    e.globalY() - 140 - self.customToolTip.isWordWrap * 30)
            self.customToolTip.show()

    def leaveEvent(self, e):
        """ 判断鼠标是否离开标签 """
        if self.parent() and self.customToolTip:
            notLeave = isNotLeave(self)
            if notLeave:
                return
            self.customToolTip.hide()

    def setCustomToolTip(self, toolTip, text: str):
        """ 设置提示条和提示条内容 """
        self.customToolTip = toolTip
        self.customToolTipText = text

    def textChangedEvent(self):
        """ 如果输入框中文本改变且此时清空按钮不可见，就显示清空按钮 """
        if self.text() and not self.clearButton.isVisible():
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
        return super().eventFilter(obj,e)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    demo = LineEdit()
    demo.show()
    sys.exit(app.exec_())
