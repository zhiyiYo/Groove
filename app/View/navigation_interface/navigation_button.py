# coding:utf-8

from PyQt5.QtCore import QPoint, Qt
from PyQt5.QtGui import QBrush, QColor, QPainter, QPen, QPolygon, QPixmap, QFont
from PyQt5.QtWidgets import QPushButton

from app.common.get_pressed_pos import getPressedPos


class NavigationButton(QPushButton):
    """ 侧边导航栏按钮 """

    def __init__(self, iconPath: str, text="", buttonSize: tuple = (60, 60), parent=None):
        """
        Parameters
        ----------
        iconPath: str
            图标路径

        text: str
            按钮文本

        buttonSize: tuple
            按钮大小

        parent:
            父级窗口
        """
        super().__init__(text, parent)
        # 保存数据
        self.image = QPixmap(iconPath)
        self.buttonSizeTuple = buttonSize
        self.initWidget()

    def initWidget(self):
        """ 初始化小部件 """
        # 设置按钮的图标
        self.setFixedSize(*self.buttonSizeTuple)
        # 设置属性防止qss不起作用
        self.setAttribute(Qt.WA_StyledBackground | Qt.WA_TranslucentBackground)
        # 初始化标志位
        self.isEnter = False
        self.isSelected = False
        self.pressedPos = None

    def enterEvent(self, e):
        """ 鼠标进入时更新样式 """
        self.isEnter = True
        self.update()

    def leaveEvent(self, e):
        """ 鼠标离开时更新样式 """
        self.isEnter = False
        self.update()

    def mousePressEvent(self, e):
        """ 鼠标点击时更新样式 """
        self.pressedPos = getPressedPos(self, e)
        self.update()
        super().mousePressEvent(e)

    def mouseReleaseEvent(self, e):
        """ 鼠标松开时更新样式 """
        super().mouseReleaseEvent(e)
        self.pressedPos = None
        self.update()

    def paintEvent(self, e):
        """ 选中时在左边绘制选中标志 """
        painter = QPainter(self)
        painter.setPen(Qt.NoPen)
        if self.isEnter:
            brush = QBrush(QColor(0, 0, 0, 20))
            painter.setBrush(brush)
            painter.drawRect(self.rect())

    def setSelected(self, isSelected: bool):
        """ 设置选中情况 """
        self.isSelected = isSelected
        self.update()


class ToolButton(NavigationButton):
    """ 工具按钮 """

    def __init__(self, iconPath, buttonSize=(60, 60), parent=None):
        """
        Parameters
        ----------
        iconPath: str
            图标路径

        parent:
            父级窗口

        buttonSize: tuple
            按钮大小
        """
        super().__init__(iconPath, "", buttonSize, parent)

    def paintEvent(self, e):
        """ 绘制背景 """
        super().paintEvent(e)
        painter = QPainter(self)
        painter.setPen(Qt.NoPen)
        painter.setRenderHints(QPainter.Antialiasing |
                               QPainter.SmoothPixmapTransform)

        if self.isSelected == True:
            # 已选中且再次点击时根据点击方位的不同更新左边选中标志的形状
            if not self.pressedPos:
                brush = QBrush(QColor(0, 107, 133))
                painter.setBrush(brush)
                painter.drawRect(0, 1, 4, self.height() - 2)
            elif self.pressedPos in ["left-top", "right-bottom", "top"]:
                # 绘制选中标志
                self.drawLine(
                    painter, 2, 2, 6, 2, 4, self.height() - 2, 0, self.height() - 2
                )
            elif self.pressedPos in ["left-bottom", "right-top", "bottom"]:
                self.drawLine(
                    painter, 0, 1, 4, 1, 6, self.height() - 2, 2, self.height() - 2
                )
            elif self.pressedPos in ["left", "right", "center"]:
                self.drawLine(
                    painter, 1, 2, 5, 2, 5, self.height() - 2, 1, self.height() - 2
                )
        # 绘制图标
        if not self.pressedPos:
            self.drawIcon(painter, self.image)
        elif self.pressedPos in ["left-top", "right-bottom", "top"]:
            self.drawIcon(painter, self.image, -0.05, 0)
        elif self.pressedPos in ["left-bottom", "right-top", "bottom"]:
            self.drawIcon(painter, self.image, 0.05, 0)
        elif self.pressedPos in ["left", "right", "center"]:
            image = self.image.scaled(
                self.image.width() - 4,
                self.image.height() - 4,
                Qt.KeepAspectRatio,
                Qt.SmoothTransformation,
            )
            self.drawIcon(painter, image, 0, 0, 2, 2)

    def drawIcon(
        self, painter, image: QPixmap, shearX: float = 0, shearY: float = 0, x=0, y=0
    ):
        """ 绘制图标 """
        painter.shear(shearX, shearY)
        painter.drawPixmap(x, y, image.width(), image.height(), image)

    def drawLine(self, painter, x1, y1, x2, y2, x3, y3, x4, y4):
        """ 绘制选中标志 """
        painter.setPen(Qt.NoPen)
        brush = QBrush(QColor(0, 107, 133))
        painter.setBrush(brush)
        points = [QPoint(x1, y1), QPoint(x2, y2),
                  QPoint(x3, y3), QPoint(x4, y4)]
        painter.drawPolygon(QPolygon(points), 4)


class PushButton(NavigationButton):
    """ 显示图标和文字的按钮 """

    def paintEvent(self, e):
        """ 绘制背景 """
        super().paintEvent(e)
        painter = QPainter(self)
        painter.setPen(Qt.NoPen)
        painter.setRenderHints(
            QPainter.Antialiasing
            | QPainter.TextAntialiasing
            | QPainter.SmoothPixmapTransform
        )

        # 绘制选中标志
        painter.setPen(Qt.NoPen)
        if self.isSelected == True:
            # 已选中且再次点击时根据点击方位的不同更新左边选中标志的形状
            if not self.pressedPos:
                brush = QBrush(QColor(0, 107, 133))
                painter.setBrush(brush)
                painter.drawRect(0, 1, 4, self.height() - 2)

            # 左上角和顶部
            elif self.pressedPos in ["left-top", "top"]:
                self.drawLine(
                    painter, 5, 2, 9, 2, 7, self.height() - 2, 3, self.height() - 2
                )
            # 左下角和底部
            elif self.pressedPos in ["left-bottom", "bottom"]:
                self.drawLine(
                    painter, 3, 2, 7, 2, 9, self.height() - 3, 5, self.height() - 3
                )
            # 左边和中间
            elif self.pressedPos in ["left", "center"]:
                self.drawLine(
                    painter, 5, 2, 9, 2, 9, self.height() - 2, 5, self.height() - 2
                )
            # 右上角
            elif self.pressedPos == "right-top":
                self.drawLine(
                    painter, 0, 2, 4, 2, 3, self.height() - 2, 0, self.height() - 2
                )
            # 右边
            elif self.pressedPos == "right":
                self.drawLine(
                    painter, 1, 1, 5, 1, 5, self.height() - 1, 1, self.height() - 1
                )
            # 右下角
            elif self.pressedPos == "right-bottom":
                self.drawLine(
                    painter, 0, 2, 3, 2, 4, self.height() - 2, 0, self.height() - 2
                )

        # 绘制图标和文字
        if not self.pressedPos:
            self.drawTextIcon(painter, self.image)
        elif self.pressedPos in ["left-top", "top"]:
            self.drawTextIcon(painter, self.image, -0.05, 0)
        elif self.pressedPos in ["left-bottom", "bottom"]:
            self.drawTextIcon(painter, self.image, 0.05, 0)
        elif self.pressedPos in ["left", "center"]:
            image = self.image.scaled(
                self.image.width() - 4,
                self.image.height() - 4,
                Qt.KeepAspectRatio,
                Qt.SmoothTransformation,
            )
            # 图标和文字需要右移
            self.drawTextIcon(painter, image, 0, 0, 7, 2, 63, 21)
        elif self.pressedPos == "right-top":
            self.drawTextIcon(painter, self.image, -0.02, 0)
        elif self.pressedPos == "right":
            image = self.image.scaled(
                self.image.width() - 2,
                self.image.height() - 2,
                Qt.KeepAspectRatio,
                Qt.SmoothTransformation,
            )
            self.drawTextIcon(painter, image, 0, 0, 3, 1, 61, 21)
        elif self.pressedPos == "right-bottom":
            image = self.image.scaled(
                self.image.width() - 2,
                self.image.height() - 2,
                Qt.KeepAspectRatio,
                Qt.SmoothTransformation,
            )
            self.drawTextIcon(painter, image, -0.02, 0, 0, 1)

    def drawTextIcon(
        self,
        painter,
        image: QPixmap,
        shearX: float = 0,
        shearY: float = 0,
        iconX=0,
        iconY=0,
        textX=60,
        textY=21,
        fontSize=11,
    ):
        """ 绘制图标和文字 """
        painter.shear(shearX, shearY)
        # 绘制图标
        painter.drawPixmap(iconX, iconY, image.width(), image.height(), image)
        # 绘制文字
        if self.text():
            painter.setPen(QPen(Qt.black))
            painter.setFont(QFont("Microsoft YaHei", fontSize, 25))
            if self.objectName() not in ["myLoveButton", "playListButton"]:
                painter.drawText(textX, textY + 16, self.text())
            else:
                painter.drawText(textX, textY + 18, self.text())

    def drawLine(self, painter, x1, y1, x2, y2, x3, y3, x4, y4):
        """ 绘制选中标志 """
        painter.setPen(Qt.NoPen)
        brush = QBrush(QColor(0, 107, 133))
        painter.setBrush(brush)
        points = [QPoint(x1, y1), QPoint(x2, y2),
                  QPoint(x3, y3), QPoint(x4, y4)]
        painter.drawPolygon(QPolygon(points), 4)


class CreatePlaylistButton(NavigationButton):
    """ 导航栏创建播放列表按钮 """

    def __init__(self, parent):
        self.iconPath = r"app\resource\images\navigation_interface\黑色新建播放列表.png"
        super().__init__(self.iconPath, parent=parent)

    def paintEvent(self, e):
        """ 绘制背景 """
        super().paintEvent(e)
        painter = QPainter(self)
        painter.setPen(Qt.NoPen)
        painter.setRenderHints(QPainter.Antialiasing |
                               QPainter.SmoothPixmapTransform)
        # 已选中且再次点击时根据点击方位的不同更新左边选中标志的形状
        if not self.pressedPos:
            self.drawIcon(painter, self.image)
        elif self.pressedPos in ["left-top", "right-bottom", "top"]:
            self.drawIcon(painter, self.image, -0.05, 0)
        elif self.pressedPos in ["left-bottom", "right-top", "bottom"]:
            self.drawIcon(painter, self.image, 0.05, 0)
        elif self.pressedPos in ["left", "right", "center"]:
            image = self.image.scaled(
                self.image.width() - 6,
                self.image.height() - 4,
                Qt.KeepAspectRatio,
                Qt.SmoothTransformation,
            )
            self.drawIcon(painter, image, -0.01, 0, 4, 3)

    def drawIcon(self, painter, image: QPixmap, shearX: float = 0, shearY: float = 0, x=0, y=0):
        """ 绘制图标 """
        painter.shear(shearX, shearY)
        painter.drawPixmap(x, y, image.width(), image.height(), image)
