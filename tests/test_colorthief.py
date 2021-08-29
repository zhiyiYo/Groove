import sys

from colorthief import ColorThief

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPainter, QBrush, QColor
from PyQt5.QtWidgets import QWidget, QApplication


class ImagePalette(QWidget):
    def __init__(self, imgPath: str, quality=10):
        super().__init__()
        self.imgPath = imgPath
        self.resize(500, 500)
        thief = ColorThief(imgPath)
        self.imgPalette = thief.get_palette(10, quality)

    def paintEvent(self, e):
        """ 绘制调色板 """
        painter = QPainter(self)
        painter.setPen(Qt.NoPen)
        height = int(self.height() / len(self.imgPalette))
        for i, rgb in enumerate(self.imgPalette):
            painter.setBrush(QBrush(QColor(*rgb)))
            painter.drawRect(0, i * height, self.width(), height)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    demo = ImagePalette("Album_Cover/風に吹かれて/風に吹かれて.png", 5)
    demo.show()
    sys.exit(app.exec_())
