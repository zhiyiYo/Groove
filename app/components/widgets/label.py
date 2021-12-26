# coding:utf-8
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QMouseEvent, QPixmap, QPainter, QBrush
from PyQt5.QtWidgets import QLabel


class ClickableLabel(QLabel):
    """ 定义可发出点击信号的Label """

    # 创建点击信号
    clicked = pyqtSignal()

    def __init__(self, text="", parent=None, isSendEventToParent: bool = True):
        super().__init__(text, parent)
        self.isSendEventToParent = isSendEventToParent

    def mousePressEvent(self, e):
        """ 处理鼠标点击 """
        if self.isSendEventToParent:
            super().mousePressEvent(e)

    def mouseReleaseEvent(self, event: QMouseEvent):
        """ 鼠标松开时发送信号 """
        if self.isSendEventToParent:
            super().mouseReleaseEvent(event)
        if event.button() == Qt.LeftButton:
            self.clicked.emit()


class ErrorIcon(QLabel):
    def __init__(self, parent=None):
        super().__init__(parent)
        # 设置提示条
        self.customToolTip = None
        self.setPixmap(
            QPixmap(":/images/song_tab_interface/Info_red.png"))
        self.setFixedSize(19, 19)


class AvatarLabel(QLabel):
    """ 圆形头像 """

    def __init__(self, imagePath: str, parent=None):
        super().__init__(parent)
        self.__pixmap = QPixmap(imagePath)
        self.setScaledContents(True)
        self.setAttribute(Qt.WA_TranslucentBackground)

    def setPixmap(self, pixmap: QPixmap) -> None:
        self.__pixmap = pixmap
        self.update()

    def paintEvent(self, e):
        """ 绘制头像 """
        painter = QPainter(self)
        painter.setRenderHints(QPainter.Antialiasing |
                               QPainter.SmoothPixmapTransform)
        w = self.width()
        painter.setPen(Qt.NoPen)
        painter.setBrush(QBrush(self.__pixmap.scaled(
            w, w, Qt.KeepAspectRatioByExpanding, Qt.SmoothTransformation)))
        painter.drawRoundedRect(self.rect(), w//2, w//2)
