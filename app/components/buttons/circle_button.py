# coding:utf-8
from PyQt5.QtCore import Qt, QEvent
from PyQt5.QtGui import QPainter, QPixmap, QBrush, QColor
from PyQt5.QtWidgets import QToolButton


class CircleButton(QToolButton):
    """ 圆形按钮 """

    def __init__(self, iconPath, parent=None, iconSize: tuple = (47, 47), buttonSize: tuple = (47, 47)):
        super().__init__(parent)
        self.iconWidth, self.iconHeight = iconSize
        self.buttonSize_tuple = buttonSize
        self.iconPath = iconPath
        self.iconPixmap = QPixmap(iconPath)
        # 标志位
        self.isEnter = False
        self.isPressed = False
        # 控制绘图位置
        self._pixPos_list = [(1, 0), (2, 2)]
        # 初始化
        self.__initWidget()

    def __initWidget(self):
        """ 初始化小部件 """
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setFixedSize(self.buttonSize_tuple[0], self.buttonSize_tuple[1])
        self.setStyleSheet(
            "QToolButton{border:none;margin:0;background:transparent}")
        # 安装事件过滤器
        self.installEventFilter(self)

    def eventFilter(self, obj, e: QEvent):
        """ 根据鼠标动作更新标志位和图标 """
        if obj == self:
            if e.type() == QEvent.Enter:
                self.isEnter = True
                self.update()
                return False
            elif e.type() == QEvent.Leave:
                self.isEnter = False
                self.update()
                return False
            elif e.type() in [
                QEvent.MouseButtonPress,
                QEvent.MouseButtonDblClick,
                QEvent.MouseButtonRelease,
            ]:
                self.isPressed = not self.isPressed
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
        painter.setPen(Qt.NoPen)
        # 鼠标按下时绘制圆形背景，pressed的优先级比hover的优先级高
        if self.isPressed:
            brush = QBrush(QColor(255, 255, 255, 70))
            painter.setBrush(brush)
            painter.drawEllipse(0, 0, self.iconWidth, self.iconHeight)
            iconPixmap = self.iconPixmap.scaled(
                self.iconPixmap.width() - 4,
                self.iconPixmap.height() - 4,
                Qt.KeepAspectRatio,
                Qt.SmoothTransformation,
            )
            px, py = self._pixPos_list[1]
        # 鼠标进入时更换图标透明度
        elif self.isEnter:
            painter.setOpacity(0.5)
        # 绘制图标
        painter.drawPixmap(px, py, iconPixmap.width(),
                           iconPixmap.height(), iconPixmap)
