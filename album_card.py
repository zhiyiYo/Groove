import sys

from PyQt5.QtCore import QEvent, QPoint, Qt
from PyQt5.QtGui import QBitmap, QPixmap, QBrush, QPen, QColor, QPainter
from PyQt5.QtWidgets import QApplication, QLabel, QVBoxLayout, QWidget

from my_button import SongerAddToButton, SongerPlayButton


class AlbumCard(QWidget):
    """ 定义包含专辑歌手名的窗口 """

    def __init__(self, albumInfo, parent=None):
        super().__init__(parent)

        # 实例化背景
        self.backgroundLabel = QLabel(self)

        # 实例化专辑名和歌手名
        self.albumName = QLabel(albumInfo['album'], self)
        self.songerName = QLabel(albumInfo['songer'], self)

        # 实例化专辑封面
        self.albumCover = AlbumCover(albumInfo['cover_path'], self)

        # 初始化小部件
        self.initWidget()

        # 初始化样式
        self.setQss()

    def initWidget(self):
        """ 初始化小部件 """
        self.setFixedSize(220, 290)
        self.setWindowFlags(Qt.FramelessWindowHint)

        # 设置专辑名自动折叠
        self.albumName.setWordWrap(True)

        self.albumCover.move(10, 10)
        self.albumName.move(10, 218)
        self.songerName.move(10, self.albumName.y()+26)

        # 设置背景图片
        self.backgroundLabel.setPixmap(
            QPixmap('resource\\images\\专辑封面无阴影.png'))

        # 分配ID
        self.albumName.setObjectName('albumName')
        self.songerName.setObjectName('songerName')

        # 设置监听
        self.installEventFilter(self)

    def eventFilter(self, obj, e):
        """ 鼠标进入窗口时显示阴影和按钮，否则不显示 """
        if obj == self:
            if e.type() == QEvent.Enter:
                self.backgroundLabel.setPixmap(
                    QPixmap('resource\\images\\专辑封面阴影.png'))
                self.albumCover.addToButton.show()
                self.albumCover.playButton.show()
            elif e.type() == QEvent.Leave:
                self.backgroundLabel.setPixmap(
                    QPixmap('resource\\images\\专辑封面无阴影.png'))
                self.albumCover.addToButton.hide()
                self.albumCover.playButton.hide()

        return False

    def setQss(self):
        """ 设置层叠样式 """
        with open('resource\\css\\albumCard.qss', 'r', encoding='utf-8') as f:
            qss = f.read()
            self.setStyleSheet(qss)


class AlbumCover(QWidget):
    """ 定义专辑封面 """

    def __init__(self, album_path, parent=None):
        super().__init__(parent)

        self.resize(200, 200)

        # 隐藏边框并将背景设置为透明
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_TranslucentBackground)

        # 实例化按钮
        self.playButton = SongerPlayButton(self)
        self.addToButton = SongerAddToButton(self)

        # 获取封面数据
        self.album_pic = QPixmap(album_path).scaled(
            self.size(), Qt.KeepAspectRatio, Qt.SmoothTransformation)

        # 初始化小部件
        self.initWidget()

    def initWidget(self):
        """ 初始化小部件 """
        self.playButton.move(int(0.5 * self.width() - 36 - 0.5 * self.playButton.width()),
                             int(0.5*self.height() - 0.5*self.playButton.height()+1))

        self.addToButton.move(int(0.5*self.width()+36-0.5*self.playButton.width()),
                              int(0.5*self.height() - 0.5*self.playButton.height()+1))

        # 隐藏按钮
        self.playButton.setHidden(True)
        self.addToButton.setHidden(True)

    def paintEvent(self, e):
        #super(SongerHeadPortrait, self).paintEvent(e)
        painter = QPainter(self)
        painter.setRenderHint(QPainter.Antialiasing, True)  # 设置抗锯齿

        # 设置无描边
        pen = Qt.NoPen
        painter.setPen(pen)

        # 设置画刷的内容为封面图
        brush = QBrush(self.album_pic)
        painter.setBrush(brush)

        # 在指定区域画圆
        painter.drawRect(0, 0, self.width(), self.height())


if __name__ == "__main__":
    app = QApplication(sys.argv)
    albumInfo = {'album': 'Assortrip', 'songer': 'HALCA',
                 'cover_path': 'resource\\Album Cover\\Assortrip\\Assortrip.jpg'}
    demo = AlbumCard(albumInfo)
    demo.show()
    sys.exit(app.exec_())
