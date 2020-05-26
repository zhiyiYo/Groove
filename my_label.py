import sys

from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QMouseEvent
from PyQt5.QtWidgets import QApplication, QLabel, QWidget


class Label(QLabel):
    """ 定义可发出点击信号的Label """
    #创建点击信号
    clicked=pyqtSignal()
    
    def __init__(self, text, parent=None):
        super().__init__(text,parent)

    def mouseReleaseEvent(self, event: QMouseEvent):
        """ 鼠标松开时发送信号 """
        if event.button() == Qt.LeftButton:
            self.clicked.emit()

class Demo(QWidget):
    def __init__(self):
        super().__init__()

        self.resize(100, 100)
        self.label=Label('这是一个自定义可点击的标签', self)
        self.label.setCursor(Qt.PointingHandCursor)
        self.label.clicked.connect(lambda: print(self.label.text()))
        
if __name__ == "__main__":
    app = QApplication(sys.argv)
    demo = Demo()
    demo.show()
    sys.exit(app.exec_())    