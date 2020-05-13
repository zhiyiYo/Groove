import sys

from PyQt5.QtCore import QEvent, QPoint, Qt
from PyQt5.QtGui import QBitmap, QPainter, QPixmap, QBrush, QPen,QColor
from PyQt5.QtWidgets import QApplication, QLabel, QVBoxLayout, QWidget


class CircleImage(QWidget):
    '''绘制圆形图片'''

    def __init__(self, parent=None):
        super(CircleImage, self).__init__(parent)
        self.resize(200, 200)
        self.circle_image = None
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)

    def set_image(self, image):
        '''设置绘制的图片'''
        self.circle_image = image
        self.update()

    def paintEvent(self, event):
        '''重写绘制事件'''
        #super(CircleImage, self).paintEvent(event)
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing, True)  # 设置抗锯齿
        #pen = Qt.NoPen
        pen = QPen(QColor(255, 0, 0))
        pen.setWidth(2)
        painter.setPen(pen)                            		# 设置取消描边边框
        brush = QBrush(self.circle_image)
        painter.setBrush(brush)								# 设置绘制内容
        painter.drawEllipse(0, 0, 200, 200)


if __name__ == '__main__':
    # 控件测试程序
    app = QApplication(sys.argv)

    widget = CircleImage()
    image = QPixmap(
        'resource\\Songer Photos\\Ariana Grande\\Ariana Grande.jpg')
    widget.set_image(image.scaled(
        widget.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation))
    widget.show()

    sys.exit(app.exec_())
