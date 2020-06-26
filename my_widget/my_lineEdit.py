import sys
from PyQt5.QtCore import QAbstractAnimation,QEvent, QSize, Qt
from PyQt5.QtGui import QContextMenuEvent, QFont, QIcon
from PyQt5.QtWidgets import QAction, QHBoxLayout, QLineEdit, QToolButton

sys.path.append('..')
from Groove.my_widget.my_menu import Menu
from Groove.my_widget.my_button import ClearButton
from Groove.my_functions.is_not_leave import isNotLeave

class LineEdit(QLineEdit):
    """ 定义一个被点击就全选文字的单行输入框 """

    def __init__(self, string=None, parent=None):
        super().__init__(string, parent)

        # 设置提示条
        self.customToolTip = None
        self.iconPath_dict = {
            'normal': r'resource\images\lineEdit\clearInfo_cross_normal.png',
            'hover': r'resource\images\lineEdit\clearInfo_cross_hover.png',
            'selected': r'resource\images\lineEdit\clearInfo_cross_selected.png'}

        # 创建右击菜单
        self.createContextMenu()
        # 实例化一个用于清空内容的按钮
        self.clearButton = ClearButton(self.iconPath_dict, self)

        # 实例化布局
        self.h_layout = QHBoxLayout()
        self.initWidget()

    def initWidget(self):
        """ 初始化小部件 """
        self.clearButton.hide()
        self.textChanged.connect(self.textChangedEvent)
        self.clearButton.move(self.width() - self.clearButton.width(), 0)
        self.setTextMargins(0, 0, self.clearButton.width(), 0)

    def createContextMenu(self):
        """ 创建右击菜单 """
        self.menu = Menu(parent=self)
        self.cutAct = QAction(
            QIcon('resource\\images\\menu\\黑色剪刀.png'),'剪切', self, shortcut='Ctrl+X',triggered=self.cut)
        self.copyAct = QAction(
            QIcon('resource\\images\\menu\\黑色复制.png'), '复制', self, shortcut='Ctrl+C', triggered=self.copy)
        self.pasteAct = QAction(
            QIcon('resource\\images\\menu\\黑色粘贴.png'), '粘贴', self, shortcut='Ctrl+V', triggered=self.paste)
        self.menu.addActions([self.cutAct, self.copyAct, self.pasteAct])
        self.menu.setObjectName('lineEditMenu')

    def mousePressEvent(self, e):
        self.selectAll()
        self.setFocus()
        # 如果输入框中有文本，就设置为只读并显示清空按钮
        if self.text():
            #self.setReadOnly(True)
            self.clearButton.show()

    def contextMenuEvent(self, e: QContextMenuEvent):
        """ 设置右击菜单 """
        self.menu.exec_(e.globalPos())

    def focusOutEvent(self, e):
        """ 当焦点移到别的输入框时隐藏按钮 """
        # 调用父类的函数，消除焦点
        super().focusOutEvent(e)
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
        self.clearButton.move(self.width()-self.clearButton.width(), 0)


class SearchLineEdit(QLineEdit):
    """ 单行搜索框 """
    def __init__(self, parent=None):
        super().__init__(parent)
