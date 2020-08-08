import sys

from PyQt5.QtCore import Qt, QEvent, QTimer
from PyQt5.QtGui import QEnterEvent
from PyQt5.QtWidgets import QApplication, QScrollBar, QWidget


class ScrollBar(QWidget):
    """ 定义一个可以变换样式的滚动条 """

    def __init__(self, externalScrollBar=None, parent=None):
        super().__init__(parent)
        self.externalScrollBar = externalScrollBar
        # 实例化两个滚动条
        self.minScrollBar = QScrollBar(Qt.Vertical, self)
        # 初始化
        self.initWidget()
        self.associateScrollBar()
        self.setQss()

    def initWidget(self):
        """ 初始化小部件 """
        self.setFixedWidth(20)
        self.minScrollBar.move(15, 0)
        self.setAttribute(Qt.WA_TranslucentBackground)
        # 分配ID
        self.setObjectName('father')
        self.minScrollBar.setObjectName('minScrollBar')

    def adjustSrollBarHeight(self):
        """ 根据父级窗口的高度调整滚动条高度 """
        if self.parent():
            self.minScrollBar.setFixedHeight(self.parent().height()-156)

    def setQss(self):
        """ 设置层叠样式 """
        with open(r'resource\css\my_scrollBar.qss', encoding='utf-8') as f:
            self.setStyleSheet(f.read())

    def associateScrollBar(self):
        """ 关联滚动条 """
        if self.externalScrollBar:
            # 设置最大值
            self.minScrollBar.setMaximum(self.externalScrollBar.maximum())
            # 关联滚动条
            self.externalScrollBar.valueChanged.connect(
                lambda: self.minScrollBar.setValue(self.externalScrollBar.value()))
            self.minScrollBar.valueChanged.connect(
                lambda: self.externalScrollBar.setValue(self.minScrollBar.value()))


if __name__ == "__main__":
    app = QApplication(sys.argv)
    demo = ScrollBar()
    demo.show()
    sys.exit(app.exec_())
