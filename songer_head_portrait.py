import sys

from PyQt5.QtCore import Qt, QEvent
from PyQt5.QtGui import QBitmap, QPainter, QPixmap
from PyQt5.QtWidgets import QApplication, QPushButton, QWidget

from my_button import SongerPlayButton,SongerAddToButton


class SongerHeadPortrait(QWidget):

    def __init__(self, songer_pic_path):
        super().__init__()

        # 隐藏边框
        self.setWindowFlags(Qt.FramelessWindowHint)

        # 实例化播放按钮和添加到按钮
        self.playButton = SongerPlayButton(self)
        self.addToButton = SongerAddToButton(self)

        # 设置遮罩
        self.mask = QBitmap('resource\\images\\mask.svg')
        self.songer_pic_path = songer_pic_path
        self.resize(self.mask.size())
        self.setMask(self.mask)

        # 初始化布局
        self.initWidget()

    def initWidget(self):
        """ 初始化小部件 """
        self.playButton.move(int(0.5 * self.width() - 36 - 0.5 * self.playButton.width()),
                             int(0.5*self.height() - 0.5*self.playButton.height()+1))

        self.addToButton.move(int(0.5*self.width()+36-0.5*self.playButton.width()),
                              int(0.5*self.height() - 0.5*self.playButton.height()+1))

        self.addToButton.setToolTip('添加到')
        self.playButton.setToolTip('播放')

        # 隐藏按钮
        self.playButton.setHidden(True)
        self.addToButton.setHidden(True)

        # 安装监听
        self.installEventFilter(self)

    def paintEvent(self, e):
        painter = QPainter(self)
        pix = QPixmap(self.songer_pic_path).scaled(
            200, 200, Qt.KeepAspectRatio, Qt.SmoothTransformation)
        painter.drawPixmap(0, 0, self.width(), self.height(), pix)

    def eventFilter(self, obj, event):
        """ 鼠标移入时显示按钮，移出时隐藏按钮 """
        if obj == self:
            if event.type() == QEvent.Enter:
                self.playButton.show()
                self.addToButton.show()
            elif event.type() == QEvent.Leave:
                self.playButton.setHidden(True)
                self.addToButton.setHidden(True)
                
        return False

if __name__ == "__main__":
    app = QApplication(sys.argv)
    demo = SongerHeadPortrait(
        'resource\\Songer Photos\\Carpenters\\Carpenters.jpg')
    demo.show()
    sys.exit(app.exec_())
