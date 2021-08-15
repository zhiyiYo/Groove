# coding:utf-8
from PyQt5.QtCore import (QEasingCurve, QPropertyAnimation, Qt, QTimer,
                          pyqtSignal)
from PyQt5.QtGui import QPainter, QPixmap
from PyQt5.QtWidgets import QLabel, QToolButton, QWidget


class StateTooltip(QWidget):
    """ 进度提示框 """

    closedSignal = pyqtSignal()

    def __init__(self, title="", content="", parent=None):
        """
        Parameters
        ----------
        title: str
            状态气泡标题

        content: str
            状态气泡内容

        parant:
            父级窗口
        """
        super().__init__(parent)
        self.title = title
        self.content = content
        # 实例化小部件
        self.titleLabel = QLabel(self.title, self)
        self.contentLabel = QLabel(self.content, self)
        self.rotateTimer = QTimer(self)
        self.closeTimer = QTimer(self)
        self.animation = QPropertyAnimation(self, b"windowOpacity")
        self.busyImage = QPixmap(
            "app/resource/images/state_tooltip/running.png")
        self.doneImage = QPixmap(
            "app/resource/images/state_tooltip/completed.png")
        self.closeButton = QToolButton(self)
        # 初始化参数
        self.isDone = False
        self.rotateAngle = 0
        self.deltaAngle = 20
        # 初始化
        self.__initWidget()

    def __initWidget(self):
        """ 初始化小部件 """
        self.setAttribute(Qt.WA_StyledBackground)
        self.rotateTimer.setInterval(50)
        self.closeTimer.setInterval(1000)
        self.contentLabel.setMinimumWidth(200)
        # 将信号连接到槽函数
        self.closeButton.clicked.connect(self.hide)  # 点击关闭按钮只是隐藏了提示条
        self.rotateTimer.timeout.connect(self.__rotateTimerFlowSlot)
        self.closeTimer.timeout.connect(self.__slowlyClose)
        self.__setQss()
        self.__initLayout()
        # 打开定时器
        self.rotateTimer.start()

    def __initLayout(self):
        """ 初始化布局 """
        self.titleLabel.adjustSize()
        self.contentLabel.adjustSize()
        self.setFixedSize(max(self.titleLabel.width(),
                          self.contentLabel.width()) + 70, 64)
        self.titleLabel.move(40, 11)
        self.contentLabel.move(15, 34)
        self.closeButton.move(self.width() - 30, 23)

    def __setQss(self):
        """ 设置层叠样式 """
        self.titleLabel.setObjectName("titleLabel")
        self.contentLabel.setObjectName("contentLabel")
        with open("app/resource/css/state_tooltip.qss", encoding="utf-8") as f:
            self.setStyleSheet(f.read())
        self.titleLabel.adjustSize()
        self.contentLabel.adjustSize()

    def setTitle(self, title: str):
        """ 设置提示框的标题 """
        self.title = title
        self.titleLabel.setText(title)
        self.titleLabel.adjustSize()

    def setContent(self, content: str):
        """ 设置提示框内容 """
        self.content = content
        self.contentLabel.setText(content)
        self.contentLabel.adjustSize()

    def setState(self, isDone=False):
        """ 设置运行状态 """
        self.isDone = isDone
        self.update()
        # 运行完成后主动关闭窗口
        if self.isDone:
            self.closeTimer.start()

    def __onCloseButtonClicked(self):
        """ 关闭按钮点击槽函数 """
        self.closedSignal.emit()
        self.hide()  # 只隐藏，不删除

    def __slowlyClose(self):
        """ 缓慢关闭窗口 """
        self.rotateTimer.stop()
        self.animation.setEasingCurve(QEasingCurve.Linear)
        self.animation.setDuration(500)
        self.animation.setStartValue(1)
        self.animation.setEndValue(0)
        self.animation.finished.connect(self.deleteLater)
        self.animation.start()

    def __rotateTimerFlowSlot(self):
        """ 定时器溢出时旋转箭头 """
        self.rotateAngle = (self.rotateAngle + self.deltaAngle) % 360
        self.update()

    def paintEvent(self, e):
        """ 绘制背景 """
        super().paintEvent(e)
        # 绘制旋转箭头
        painter = QPainter(self)
        painter.setRenderHints(QPainter.SmoothPixmapTransform)
        painter.setPen(Qt.NoPen)
        if not self.isDone:
            painter.translate(24, 23)  # 原点平移到旋转中心
            painter.rotate(self.rotateAngle)  # 坐标系旋转
            painter.drawPixmap(
                -int(self.busyImage.width() / 2),
                -int(self.busyImage.height() / 2),
                self.busyImage,
            )
        else:
            painter.drawPixmap(
                14, 13, self.doneImage.width(), self.doneImage.height(), self.doneImage
            )
