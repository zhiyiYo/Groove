import sys

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPainter,QPen,QColor
from PyQt5.QtWidgets import QApplication,QWidget


class BlackFrame(QWidget):
    """ 窗口移动时的边框 """
    def __init__(self, parent):
        super().__init__(parent)
        self.setWindowFlags(Qt.Window)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.hide()

    def paintEvent(self, e):
        """ 绘制边框 """
        painter = QPainter(self)
        pen = QPen(QColor(0,0,0,210))
        pen.setWidth(9)
        # 设置拐角处的形状
        pen.setJoinStyle(Qt.MiterJoin)
        painter.setPen(pen)
        painter.drawRect(self.rect())
    

class Demo(QWidget):
    def __init__(self):
        super().__init__()
        self.resize(500,500)
        self.frame = BlackFrame(self)
        self.frame.resize(500,500)
        self.frame.move(self.x(),self.y())
        self.frame.show()
        

if __name__ == "__main__":
    app = QApplication(sys.argv)
    demo = Demo()
    demo.show()
    sys.exit(app.exec_())
