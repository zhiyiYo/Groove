import sys

from PyQt5.QtCore import Qt
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QApplication, QGraphicsBlurEffect, QLabel, QWidget,QGraphicsOpacityEffect


class SubWindow(QWidget):
    """ 定义专辑的磨砂背景 """

    def __init__(self, parent=None):
        super().__init__(parent)

        # 实例化背景和磨砂效果
        self.pic = QLabel(self)
        self.blurEffect = QGraphicsBlurEffect(self)
        self.initWidget()

    def initWidget(self):
        """ 初始化小部件 """
        self.resize(260, 303)
        self.setStyleSheet('background:white')
        # 设置背景图的样式
        self.pic.move(30, 15)
        self.blurEffect.setBlurRadius(20)
        self.pic.setGraphicsEffect(self.blurEffect)

    def setPic(self, pic_path):
        """ 更换背景图 """
        self.pic.setPixmap(QPixmap(pic_path).scaled(200,202))
        

class AlbumBlurBackground(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.resize(260,303)
        self.op = QGraphicsOpacityEffect(self)
        self.subWindow = SubWindow(self)
        self.op.setOpacity(0.7)
        self.subWindow.setGraphicsEffect(self.op)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    demo = AlbumBlurBackground()
    pic_path = r'resource\Album Cover\流星ダイアリー\流星ダイアリー.jpg'
    demo.subWindow.setPic(pic_path)
    demo.album = QLabel(demo)
    demo.albumName = QLabel('Assortrip\nHALCA', demo)
    demo.album.setPixmap(QPixmap(pic_path).scaled(200, 200))
    demo.album.move(30, 10)
    demo.albumName.setStyleSheet(
        'background:transparent;font:19px "Microsoft YaHei";font-weight:bold')
    demo.albumName.move(30, 220)
    demo.show()

    sys.exit(app.exec_())
