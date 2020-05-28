from PyQt5.QtCore import QEvent, QSize, Qt
from PyQt5.QtGui import QContextMenuEvent, QFont, QIcon, QRegExpValidator
from PyQt5.QtWidgets import (QAction, QHBoxLayout, QLineEdit, QMenu,
                             QToolButton, QToolTip)


class LineEdit(QLineEdit):
    """ 定义一个被点击就全选文字的单行输入框 """

    def __init__(self, string=None, parent=None):
        super().__init__(string, parent)

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
        self.clearButton.installEventFilter(self)

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
        self.menu = QMenu(self)
        self.cutAct = QAction('剪切', self, shortcut='Ctrl+X')
        self.copyAct = QAction('复制', self, shortcut='Ctrl+C')
        self.pasteAct = QAction('粘贴', self, shortcut='Ctrl+V')
        self.menu.addActions([self.cutAct, self.copyAct, self.pasteAct])

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

    def eventFilter(self, obj, e):
        """ 当鼠标进入或离开按钮时改变按钮的图片 """
        if e.type() == QEvent.Enter:
            self.clearButton.setIcon(
                QIcon('resource\\images\\clearInfo_cross_hover.png'))
        elif e.type() == QEvent.Leave:
            self.clearButton.setIcon(
                QIcon('resource\\images\\clearInfo_cross.png'))
        return False
