import sys

from PyQt5.QtCore import QEvent, QPoint, Qt
from PyQt5.QtGui import QBitmap, QPainter, QPixmap
from PyQt5.QtWidgets import QApplication, QLabel, QVBoxLayout, QWidget

from my_button import SongerAddToButton, SongerPlayButton


class SongerCard(QWidget):
    """ 定义一个包含歌手头像和名字的类 """

    def __init__(self, songer_pic_path, songer_name):
        super().__init__()

        # 实例化歌手名标签和背景
        self.backgroundLabel = QLabel(self)
        self.songerNameLabel = SongerName(songer_name, self)

        # 实例化歌手头像
        self.songerHeadPortrait = SongerHeadPortrait(songer_pic_path, self)

        # 初始化小部件
        self.initWidget()

        # 设置层叠样式
        self.setQss()

    def initWidget(self):
        """ 初始化小部件 """
        self.resize(222, 267)

        self.setWindowFlags(Qt.FramelessWindowHint)

        # 设置小部件的绝对位置
        self.songerHeadPortrait.move(10, 8)
        self.songerNameLabel.move(1, 212)

        # 初始化背景图片
        self.backgroundLabel.setPixmap(
            QPixmap('resource\\images\\歌手头像无阴影.png'))

        # 设置监听
        self.installEventFilter(self)

    def eventFilter(self, obj, e):
        """ 鼠标进入窗口时显示阴影和按钮，否则不显示 """
        if obj == self:
            if e.type() == QEvent.Enter:
                self.backgroundLabel.setPixmap(
                    QPixmap('resource\\images\\歌手头像阴影.png'))
                self.songerHeadPortrait.addToButton.show()
                self.songerHeadPortrait.playButton.show()
            elif e.type() == QEvent.Leave:
                self.backgroundLabel.setPixmap(
                    QPixmap('resource\\images\\歌手头像无阴影.png'))
                self.songerHeadPortrait.addToButton.setHidden(True)
                self.songerHeadPortrait.playButton.setHidden(True)

        return False

    def setQss(self):
        """ 设置层叠样式 """
        with open('resource\\css\\songerCard.qss', 'r', encoding='utf-8') as f:
            qss = f.read()
            self.setStyleSheet(qss)


class SongerHeadPortrait(QWidget):

    def __init__(self, songer_pic_path, parent=None):
        super().__init__(parent)

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


class SongerName(QWidget):
    """ 歌手名标签 """

    def __init__(self, songer_name, parent=None):
        super().__init__(parent)

        self.setFixedWidth(220)

        # 实例化歌手名标签
        self.songerNameLabel = QLabel(songer_name, self)
        # 实例化布局
        self.v_layout = QVBoxLayout()

        # 初始化布局
        self.v_layout.addWidget(self.songerNameLabel, 0, Qt.AlignHCenter)
        self.setLayout(self.v_layout)

        # 设置自动换行
        # self.songerNameLabel.setWordWrap(True)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    songCard = SongerCard(
        'resource\\Songer Photos\\Backstreet Boys\\Backstreet Boys.jpg', 'Backstreet Boys')
    songCard.show()
    sys.exit(app.exec_())