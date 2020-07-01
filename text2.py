import sys
from ctypes.wintypes import HWND

from PyQt5.QtCore import Qt,QPoint
from PyQt5.QtGui import QIcon, QPainter, QPen, QColor
from PyQt5.QtWidgets import QApplication, QVBoxLayout, QHBoxLayout, QWidget, QPushButton, QLabel
from my_title_bar.title_bar import TitleBar
from my_widget.my_scroll_bar import ScrollBar


class Demo(QWidget):
    def __init__(self):
        super().__init__()
        self.resize(600, 600)
        self.setMouseTracking(True)
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.titleBar = TitleBar(self)
        self.scrollBar = ScrollBar(parent=self)
        self.scrollBar.move(self.width()-self.scrollBar.width()-1,40)
        #self.titleBar.setMouseTracking(True)
        self.initDrag()

    def initDrag(self):
        # 设置鼠标跟踪判断扳机默认值
        self._padding=5
        self._corner_drag = False
        self._bottom_drag = False
        self._right_drag = False
        self._top_drag=False
        
    def resizeEvent(self, e):
        self.titleBar.resize(self.width(), 40)
        self.scrollBar.move(self.width()-self.scrollBar.width()-1, 40)
        self.scrollBar.resize(self.scrollBar.width(),self.height()-40)
        
        self._right_rect = [QPoint(x, y) for x in range(self.width() - self._padding, self.width() + 1)
                            for y in range(1, self.height() - self._padding)]
        self._bottom_rect = [QPoint(x, y) for x in range(1, self.width() - self._padding)
                             for y in range(self.height() - self._padding, self.height() + 1)]
        self._corner_rect = [QPoint(x, y) for x in range(self.width() - self._padding, self.width() + 1)
                             for y in range(self.height() - self._padding, self.height() + 1)]

    def mousePressEvent(self, event):
        """ 当鼠标在允许拖拽处点击时，将相应的标志位置位 """
        if (event.button() == Qt.LeftButton) and (event.pos() in self._corner_rect):
            # 鼠标左键点击右下角边界区域
            self._corner_drag = True
        elif (event.button() == Qt.LeftButton) and (event.pos() in self._right_rect):
            # 鼠标左键点击右侧边界区域
            self._right_drag = True
        elif (event.button() == Qt.LeftButton) and (event.pos() in self._bottom_rect):
            # 鼠标左键点击下侧边界区域
            self._bottom_drag = True

    def mouseMoveEvent(self, e):
        # 判断鼠标位置切换鼠标手势
        if e.pos() in self._corner_rect:
            self.setCursor(Qt.SizeFDiagCursor)
        elif e.pos() in self._bottom_rect:
            self.setCursor(Qt.SizeVerCursor)
        elif e.pos() in self._right_rect:
            self.setCursor(Qt.SizeHorCursor)
        else:
            self.setCursor(Qt.ArrowCursor)
        # 当鼠标左键点击不放及满足点击区域的要求后，分别实现不同的窗口调整
        # 没有定义左方和上方相关的5个方向，主要是因为实现起来不难，但是效果很差，拖放的时候窗口闪烁，再研究研究是否有更好的实现
        if Qt.LeftButton and self._right_drag:
            # 右侧调整窗口宽度
            self.resize(e.pos().x(), self.height())
        elif Qt.LeftButton and self._bottom_drag:
            # 下侧调整窗口高度
            self.resize(self.width(), e.pos().y())
        elif Qt.LeftButton and self._corner_drag:
            # 右下角同时调整高度和宽度
            self.resize(e.pos().x(), e.pos().y())

    def mouseReleaseEvent(self, e):
        """ 鼠标释放后，各标志位置零"""
        self._corner_drag = False
        self._bottom_drag = False
        self._right_drag = False
    


if __name__ == "__main__":
    app = QApplication(sys.argv)
    demo = Demo()
    demo.show()
    sys.exit(app.exec_())


