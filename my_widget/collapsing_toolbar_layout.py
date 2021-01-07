# coding:utf-8

from PyQt5.QtCore import Qt, QMargins
from PyQt5.QtGui import QWheelEvent
from PyQt5.QtWidgets import QWidget,QListWidget

from my_widget.my_scrollArea import ScrollArea


class CollapsingToolbarLayout(QWidget):
    """ 可折叠工具栏布局 """

    def __init__(self, maxFolding: int = 0, parent=None):
        """ 创建可折叠工具栏布局

        Parameters
        ----------
        maxFolding : int
            工具栏最大折叠量

        parent : 父级窗口
        """
        super().__init__(parent)
        self.__maxFolding = maxFolding
        self.__toolBar = None
        self.__listWidget = None

    @property
    def maxFolding(self):
        return self.__maxFolding

    def setToolBar(self, toolBar):
        """ 设置工具栏 """
        self.__toolBar = toolBar
        # 记录工具栏原本的高度
        self.__originToolBarHeight = self.__toolBar.height()

    def setListWidget(self, listWidget):
        """ 设置列表部件 """
        self.__listWidget = listWidget
        # 记录列表控件原本的 margins
        self.__listViewportMargins = self.__listWidget.viewportMargins()  # type:QMargins
        # 将滚动信号连到槽函数
        listWidget.verticalScrollBar().valueChanged.connect(self.__collapseToolBar)

    def setmaxFolding(self, maxFolding: int = 0):
        """ 设置工具栏的最小高度 """
        self.__maxFolding = maxFolding

    def __collapseToolBar(self, value: int):
        """ 发生滚动时折叠工具栏 """
        # 如果滚动的量小于最大折叠量就折叠工具栏
        if value > self.__maxFolding:
            return
        self.__toolBar.resize(self.__toolBar.width(),
                                self.__originToolBarHeight - value)
        