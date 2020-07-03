import sys

from PyQt5.QtCore import Qt,QPoint
from PyQt5.QtGui import QPainter, QBrush, QColor, QPixmap,QPolygon,QFont
from PyQt5.QtWidgets import QApplication, QDialog, QLabel, QPushButton, QWidget, QGraphicsDropShadowEffect


class Demo(QWidget):
    """ 删除文件夹卡对话框 """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.resize(240, 240)

    def paintEvent(self, e):
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing)
        #painter.setPen(Qt.NoPen)
        painter.setFont(QFont('Microsoft YaHei',12))
        painter.shear(-0.2, 0)
        painter.drawText(50, 50, '这是一个测试')
        painter.setBrush(Qt.NoBrush)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    demo = Demo()
    demo.show()
    sys.exit(app.exec_())
