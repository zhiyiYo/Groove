import sys

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QBitmap, QPainter, QPixmap
from PyQt5.QtWidgets import QApplication, QPushButton


class SongerAddToButton(QPushButton):

    def __init__(self, parent=None):
        super().__init__(parent)

        self.setWindowFlags(Qt.FramelessWindowHint)
        self.mask = QBitmap('resource\\images\\play_button_mask2.svg')
        self.resize(self.mask.size())
        self.setMask(self.mask)

    def paintEvent(self, e):
        painter = QPainter(self)
        # painter.setRenderHint(QPainter.Antialiasing)
        pix = QPixmap('resource\\images\\歌手添加到按钮.png')
        painter.drawPixmap(0, 0, self.width(), self.height(), pix)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    demo = SongerAddToButton()
    demo.show()
    sys.exit(app.exec_())
