import sys
from PyQt5.QtCore import QEvent, QSize, Qt
from PyQt5.QtGui import QContextMenuEvent, QFont, QIcon, QRegExpValidator
from PyQt5.QtWidgets import (QAction, QHBoxLayout, QLineEdit,
                             QToolButton, QToolTip)
sys.path.append('..')
from Groove.my_widget.my_menu import Menu

class LineEdit(QLineEdit):
    """ 定义一个被点击就全选文字的单行输入框 """

    def __init__(self, string=None, parent=None):
        super().__init__(string, parent)

        # 设置提示条
        self.customToolTip = None

        # 创建右击菜单
        self.createContextMenu()
        # 实例化一个用于清空内容的按钮
        self.clearButton = QToolButton(self)

        # 实例化布局
        self.h_layout = QHBoxLayout()
        self.initWidget()
        self.initLayout()

    def initWidget(self):
        """ 初始化小部件 """
        #设置焦点措施
        self.setFocusPolicy(Qt.StrongFocus)
        self.clearButton.setFixedSize(39, 39)
        self.clearButton.setFocusPolicy(Qt.NoFocus)
        self.clearButton.setCursor(Qt.ArrowCursor)
        self.clearButton.setIcon(
            QIcon('resource\\images\\clearInfo_cross.png'))
        self.clearButton.setIconSize(QSize(39, 39))
        self.clearButton.clicked.connect(self.clearText)
        self.clearButton.setHidden(True)

    def initLayout(self):
        """ 初始化布局 """
        self.h_layout.addWidget(self.clearButton, 0, Qt.AlignRight)
        self.h_layout.setContentsMargins(0, 0, 0, 0)
        self.setLayout(self.h_layout)
        self.setTextMargins(0, 0, self.clearButton.width(), 0)

    def clearText(self):
        """ 清空输入框的内容并隐藏按钮和显示光标 """
        self.clear()
        #self.setReadOnly(False)
        self.clearButton.hide()

    def createContextMenu(self):
        """ 创建右击菜单 """
        self.menu = Menu(parent=self)
        self.cutAct = QAction(QIcon('resource\\images\\黑色剪刀.png'),'剪切', self, shortcut='Ctrl+X',triggered=self.cut)
        self.copyAct = QAction(
            QIcon('resource\\images\\黑色复制.png'), '复制', self, shortcut='Ctrl+C',triggered=self.copy)
        self.pasteAct = QAction(
            QIcon('resource\\images\\黑色粘贴.png'), '粘贴', self, shortcut='Ctrl+V',triggered=self.paste)
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
        self.clearButton.setHidden(True)

    def enterEvent(self, e):
        """ 鼠标进入时显示提示条并改变按钮图片 """
        self.clearButton.setIcon(
            QIcon('resource\\images\\clearInfo_cross_hover.png'))
        if self.customToolTip:
            self.customToolTip.setText(self.customToolTipText)
            self.customToolTip.move(e.globalX() - int(self.customToolTip.width() / 2),
                                    e.globalY() - 90 - self.customToolTip.isWordWrap * 60)
            self.customToolTip.show()

    def leaveEvent(self, e):
        """ 鼠标移出时隐藏提示条并改变按钮图片 """
        self.clearButton.setIcon(
            QIcon('resource\\images\\clearInfo_cross.png'))
        if self.customToolTip:
            self.customToolTip.hide()

    def setCustomToolTip(self, toolTip, text: str):
        """ 设置提示条和提示条内容 """
        self.customToolTip = toolTip
        self.customToolTipText = text
