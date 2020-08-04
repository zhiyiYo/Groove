import sys

from PyQt5.QtCore import Qt, QPropertyAnimation, QEasingCurve
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QApplication, QGraphicsBlurEffect, QLabel, QWidget, QGraphicsOpacityEffect


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
        self.pic.setPixmap(QPixmap(pic_path).scaled(200, 202))


class AlbumBlurBackground(QWidget):
    def __init__(self, parent=None):
        super().__init__(parent)
        self.subWindow = SubWindow(self)
        self.opacityEffect = QGraphicsOpacityEffect(self)
        self.subWindowOpacityEffect = QGraphicsOpacityEffect(self)
        self.showAni = QPropertyAnimation(self.opacityEffect, b'opacity')
        self.initWidget()

    def initWidget(self):
        """ 初始化小部件 """
        self.resize(260, 303)
        # 设置子窗口透明度
        self.subWindowOpacityEffect.setOpacity(0.7)
        self.subWindow.setGraphicsEffect(self.subWindowOpacityEffect)
        # 设置动画
        self.showAni.setDuration(100)
        self.showAni.setStartValue(0)
        self.showAni.setEndValue(1)
        self.showAni.setEasingCurve(QEasingCurve.InQuad)

    def show(self):
        """ 淡入 """
        self.opacityEffect.setOpacity(0)
        super().show()
        self.showAni.start()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    demo = AlbumBlurBackground()
    pic_path = r'resource\Album_Cover\流星ダイアリー\流星ダイアリー.jpg'
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
