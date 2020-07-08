import sys

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QRegion, QPainter, QPixmap, QBitmap, QColor, QBrush,QPen
from PyQt5.QtWidgets import QWidget, QApplication, QPushButton, QGraphicsBlurEffect, QLabel


class Demo(QWidget):
    def __init__(self):
        super().__init__()
        self.resize(400, 400)
        #self.setWindowFlags(Qt.FramelessWindowHint)
        self.image=QPixmap('resource\\Album Cover\\Attention\\Attention.jpg').scaled(
                self.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation)

        self.blurButton = BlurButton(self)
        self.blurButton.move(200,175)

    def paintEvent(self, e):
        painter = QPainter(self)
        painter.setRenderHints(
            QPainter.Antialiasing | QPainter.SmoothPixmapTransform)
        brush = QBrush(self.image)
        painter.setPen(Qt.cyan)
        painter.setBrush(brush)
        painter.drawRect(self.rect())


class BlurButton(QWidget):
    def __init__(self,parent):
        super().__init__(parent)
        self.resize(65,65)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.image = QLabel(self)
        self.image.setPixmap(self.parent().image)
        self.image.resize(self.parent().image.size())
        # 添加磨砂效果
        self.effect = QGraphicsBlurEffect(self)
        self.effect.setBlurRadius(30)
        self.image.setGraphicsEffect(self.effect)
        self.image.hide()
        # 获取磨砂后的pixmap
        self.pix = self.image.grab()
        

    def paintEvent(self, QPaintEvent):

        painter = QPainter(self)
        painter.setRenderHints(QPainter.Antialiasing | QPainter.SmoothPixmapTransform)
        # 原点平移到父级的原点
        painter.translate(-self.x(), -self.y())
        # 设置裁剪区域
        region = QRegion(self.x(), self.y(), self.width(), self.height(), QRegion.Ellipse)
        #painter.setClipRegion(region)
        # 设置画刷
        brush = QBrush(self.pix)
        painter.setBrush(brush)
        painter.drawRect(0, 0, self.pix.width(), self.pix.height())
        # 恢复现场
        painter.end()
        # 设置遮罩
        mask = QBitmap(self.size())
        mask.fill()
        painter = QPainter(mask)
        painter.setBrush(Qt.black)
        painter.setPen(Qt.NoPen)
        painter.drawRoundedRect(mask.rect(), self.width(),self.height())
        self.setMask(mask)
        


if __name__ == "__main__":
    app = QApplication(sys.argv)
    demo = Demo()
    demo.show()
    sys.exit(app.exec_())
