# coding:utf-8
from PyQt5.QtCore import Qt, QTimer
from PyQt5.QtGui import QEnterEvent
from PyQt5.QtWidgets import QScrollBar, QWidget


class ScrollBar(QWidget):
    """ 定义一个可以变换样式的滚动条 """

    def __init__(self, externalScrollBar=None, parent=None):
        super().__init__(parent)
        self.externalScrollBar = externalScrollBar
        # 实例化两个滚动条
        self.minScrollBar = QScrollBar(Qt.Vertical, self)
        self.maxScrollBar = QScrollBar(Qt.Vertical, self)
        # 实例化一个控制滚动条显示的计时器
        self.timer = QTimer(self)
        # 初始化
        self.initWidget()
        self.associateScrollBar()
        self.setQss()

    def initWidget(self):
        """ 初始化小部件 """
        self.setFixedWidth(20)
        self.minScrollBar.move(15, 0)
        self.maxScrollBar.hide()
        self.timer.setInterval(2000)
        self.timer.timeout.connect(self.showMinScrollBar)
        self.setAttribute(Qt.WA_TranslucentBackground)
        # 分配ID
        self.setObjectName("father")
        self.minScrollBar.setObjectName("minScrollBar")
        self.maxScrollBar.setObjectName("maxScrollBar")

    def adjustSrollBarHeight(self):
        """ 根据父级窗口的高度调整滚动条高度 """
        if self.parent():
            self.minScrollBar.setFixedHeight(self.parent().height() - 153)
            self.maxScrollBar.setFixedHeight(self.parent().height() - 153)

    def enterEvent(self, e: QEnterEvent):
        """ 鼠标进入界面时显示大滚动条并停止秒表 """
        self.maxScrollBar.show()
        self.minScrollBar.hide()
        self.timer.stop()

    def leaveEvent(self, e):
        """ 鼠标离开打开秒表 """
        self.timer.start()

    def showMinScrollBar(self):
        """ 定时溢出时隐藏大滚动条 """
        self.timer.stop()
        self.maxScrollBar.hide()
        self.minScrollBar.show()

    def setQss(self):
        """ 设置层叠样式 """
        with open(r"app\resource\css\my_scrollBar.qss", encoding="utf-8") as f:
            self.setStyleSheet(f.read())

    def associateScrollBar(self):
        """ 关联滚动条 """
        if self.externalScrollBar:
            # 设置最大值
            self.minScrollBar.setMaximum(self.externalScrollBar.maximum())
            self.maxScrollBar.setMaximum(self.externalScrollBar.maximum())

            # 关联滚动条
            self.externalScrollBar.valueChanged.connect(
                lambda: self.minScrollBar.setValue(self.externalScrollBar.value())
            )
            self.minScrollBar.valueChanged.connect(self.__minScrollBarChanged)
            self.maxScrollBar.valueChanged.connect(
                lambda: self.minScrollBar.setValue(self.maxScrollBar.value())
            )

    def __minScrollBarChanged(self):
        """ minScrollBar改变时同时改变另外两个滚动条的值 """
        self.maxScrollBar.setValue(self.minScrollBar.value())
        self.externalScrollBar.setValue(self.minScrollBar.value())
