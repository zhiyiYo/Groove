# coding:utf-8

from PyQt5.QtCore import Qt, QEvent
from PyQt5.QtGui import QPainter, QColor, QPen, QPixmap
from PyQt5.QtWidgets import QToolButton


class SmallestPlayModeButton(QToolButton):
    """ 最小播放模式界面按钮 """

    def __init__(self, iconPath, parent=None, buttonSize: tuple = (45, 45)):
        super().__init__(parent)
        self.__iconPath = iconPath
        self.__buttonSize = buttonSize
        self.__isEnter = False
        self.__isPressed = False
        # 控制绘图位置
        self._pixPos_list = [(1, 0), (2, 2)]
        self.iconPixmap = QPixmap(iconPath)
        self.__initWidget()

    def __initWidget(self):
        """ 初始化小部件 """
        self.resize(self.__buttonSize[0], self.__buttonSize[1])
        self.setStyleSheet(
            "QToolButton{border:none;margin:0;background:transparent}")
        # 安装事件过滤器
        self.installEventFilter(self)

    def eventFilter(self, obj, e: QEvent):
        """ 根据鼠标动作更新标志位和图标 """
        if obj == self:
            if e.type() == QEvent.Enter:
                self.__isEnter = True
                self.update()
                return False
            elif e.type() == QEvent.Leave:
                self.__isEnter = False
                self.update()
                return False
            elif e.type() in [QEvent.MouseButtonPress, QEvent.MouseButtonDblClick, QEvent.MouseButtonRelease]:
                self.__isPressed = not self.__isPressed
                self.update()
                return False
        return super().eventFilter(obj, e)

    def paintEvent(self, e):
        """ 绘制图标 """
        iconPixmap = self.iconPixmap
        px, py = self._pixPos_list[0]
        painter = QPainter(self)
        painter.setRenderHints(QPainter.Antialiasing |
                               QPainter.SmoothPixmapTransform)
        pen = Qt.NoPen
        if self.__isPressed:
            pen = QPen(QColor(255, 255, 255, 30))
            pen.setWidth(2)
            iconPixmap = self.iconPixmap.scaled(
                self.iconPixmap.width() - 4, self.iconPixmap.height() - 4,
                Qt.KeepAspectRatio, Qt.SmoothTransformation)
            px, py = self._pixPos_list[1]
        elif self.__isEnter:
            pen = QPen(QColor(255, 255, 255, 96))
            pen.setWidth(2)
        painter.setPen(pen)
        # 绘制圆环
        painter.drawEllipse(1, 1, self.width()-2, self.height()-2)
        # 绘制图标
        painter.drawPixmap(px, py, iconPixmap.width(),
                           iconPixmap.height(), iconPixmap)


class PlayButton(SmallestPlayModeButton):
    """ 播放按钮 """

    def __init__(self, iconPath_list: list, parent=None, buttonSize=(45, 45), isPause=True):
        super().__init__(iconPath_list[isPause], parent, buttonSize)
        self.__isPause = isPause
        self.pixmap_list = [QPixmap(iconPath)
                            for iconPath in iconPath_list]
        self._pixPos_list = [(0, 0), (2, 2)]

    def mouseReleaseEvent(self, e):
        """ 鼠标松开时更换图标 """
        self.setPlay(self.__isPause)
        super().mouseReleaseEvent(e)

    def setPlay(self, isPlay: bool):
        """ 设置播放状态 """
        self.__isPause = not isPlay
        self.iconPixmap = self.pixmap_list[self.__isPause]
        self.update()