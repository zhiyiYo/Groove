# coding:utf-8

import sys

from PyQt5.QtCore import QEasingCurve, QPropertyAnimation, Qt, QTimer
from PyQt5.QtGui import QBrush, QPainter, QPen, QPixmap
from PyQt5.QtWidgets import QApplication, QLabel, QWidget

from my_widget.my_button import ThreeStateButton


class StateToolTip(QWidget):
    """ 进度提示框 """
    def __init__(self, title='', content='',associatedThread=None, parent=None):
        super().__init__(parent)
        self.title = title
        self.content = content
        self.associatedThread = associatedThread
        # 实例化小部件
        self.createWidgets()
        # 初始化参数
        self.isDone = False
        self.rotateAngle = 0
        self.deltaAngle = 18
        # 初始化
        self.initWidget()
        self.initLayout()
        self.setQss()

    def createWidgets(self):
        """ 创建小部件 """
        icon_path = {
            'normal':
            r'resource\images\createPlaylistPanel\stateToolTip_closeBt_normal_14_14.png',
            'hover':
            r'resource\images\createPlaylistPanel\stateToolTip_closeBt_hover_14_14.png',
            'pressed':
            r'resource\images\createPlaylistPanel\stateToolTip_closeBt_hover_14_14.png'
        }

        self.closeButton = ThreeStateButton(icon_path, self, (14, 14))
        self.titleLabel = QLabel(self.title, self)
        self.contentLabel = QLabel(self.content, self)
        self.rotateTimer = QTimer(self)
        self.closeTimer = QTimer(self)
        self.animation = QPropertyAnimation(self, b'windowOpacity')
        self.busyImage = QPixmap(
            r'resource\images\createPlaylistPanel\running_22_22.png')
        self.doneImage = QPixmap(
            r'resource\images\createPlaylistPanel\complete_20_20.png')

    def initWidget(self):
        """ 初始化小部件 """
        self.setFixedSize(370, 60)
        self.setWindowFlags(Qt.FramelessWindowHint | Qt.Window)
        self.rotateTimer.setInterval(50)
        self.closeTimer.setInterval(3000)
        self.contentLabel.setMinimumWidth(200)
        # 分配ID
        self.titleLabel.setObjectName('titleLabel')
        self.contentLabel.setObjectName('contentLabel')
        # 将信号连接到槽函数
        self.closeButton.clicked.connect(self.closeButtonEvent)
        self.rotateTimer.timeout.connect(self.timeOutEvent)
        self.closeTimer.timeout.connect(self.slowlyClose)
        # 打开定时器
        self.rotateTimer.start()

    def initLayout(self):
        """ 初始化布局 """
        self.titleLabel.move(39, 11)
        self.contentLabel.move(15, 34)
        self.closeButton.move(self.width() - 29, 23)

    def setQss(self):
        """ 设置层叠样式 """
        with open(r'resource\css\stateToolTip.qss', encoding='utf-8') as f:
            self.setStyleSheet(f.read())

    def setTitle(self, title):
        """ 更新提示框的标题 """
        self.title = title
        self.titleLabel.setText(title)

    def setContent(self, content):
        """ 更新提示框内容 """
        self.content = content
        self.contentLabel.setText(content)

    def setState(self, isDone=False):
        """ 设置运行状态 """
        self.isDone = isDone
        self.update()
        # 运行完成后主动关闭窗口
        if self.isDone:
            self.closeTimer.start()

    def closeButtonEvent(self):
        """ 按下关闭按钮前摧毁相关线程 """
        if self.associatedThread:
            self.associatedThread.stop()
            self.associatedThread.requestInterruption()
            self.associatedThread.wait()
        self.deleteLater()


    def slowlyClose(self):
        """ 缓慢关闭窗口 """
        self.rotateTimer.stop()
        self.animation.setEasingCurve(QEasingCurve.Linear)
        self.animation.setDuration(500)
        self.animation.setStartValue(1)
        self.animation.setEndValue(0)
        self.animation.finished.connect(self.deleteLater)
        self.animation.start()

    def timeOutEvent(self):
        """ 定时器溢出时旋转箭头 """
        self.rotateAngle = (self.rotateAngle + self.deltaAngle) % 360
        self.update()

    def paintEvent(self, QPaintEvent):
        """ 绘制背景 """
        super().paintEvent(QPaintEvent)
        # 绘制旋转箭头
        painter = QPainter(self)
        painter.setRenderHints(QPainter.SmoothPixmapTransform)
        painter.setPen(Qt.NoPen)
        if not self.isDone:
            painter.translate(24, 20)  # 原点平移到旋转中心
            painter.rotate(self.rotateAngle)  # 坐标系旋转
            painter.drawPixmap(-int(self.busyImage.width() / 2),
                               -int(self.busyImage.height() / 2),
                               self.busyImage)
        else:
            painter.drawPixmap(14, 13, self.doneImage.width(),
                               self.doneImage.height(), self.doneImage)

    def show(self):
        """ 重写show()函数 """
        if self.parent():
            self.move(self.parent().x() + self.parent().width()-self.width() - 30,
                      self.parent().y() + 70)
        super().show()


if __name__ == "__main__":
    app = QApplication(sys.argv)
    demo = StateToolTip('正在添加音乐', '1 首歌曲')
    demo.show()
    sys.exit(app.exec_())
