# coding:utf-8
from common.config import config
from common.icon import getIconColor
from PyQt5.QtCore import QPoint, Qt
from PyQt5.QtGui import QBrush, QColor, QPainter, QPolygon, QPixmap
from PyQt5.QtWidgets import QPushButton

from common.get_pressed_pos import getPressedPos


class NavigationIconFactory:
    """ Navigation icon factory """

    ADD = "Add"
    ALBUM = "Album"
    GLOBAL_NAVIGATION = "GlobalNavButton"
    MUSIC_IN_COLLECTION = "MusicInCollection"
    PLAYING = "Playing"
    PLAYLIST = "Playlist"
    RECENT = "Recent"
    SEARCH = "Search"
    SETTINGS = "Settings"

    @classmethod
    def create(cls, iconType: str):
        """ create icon """
        path = f":/images/navigation_interface/{iconType}_{getIconColor()}.png"
        return path


NIF = NavigationIconFactory


class NavigationButton(QPushButton):
    """ Navigation push button """

    def __init__(self, iconPath: str, text="", buttonSize: tuple = (60, 60), parent=None):
        """
        Parameters
        ----------
        iconPath: str
            icon path

        text: str
            button text

        buttonSize: tuple
            button size

        parent:
            parent window
        """
        super().__init__(text, parent)
        self.image = QPixmap(iconPath)
        self.buttonSizeTuple = buttonSize
        self.setFixedSize(*self.buttonSizeTuple)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setStyleSheet(
            "QPushButton{font: 18px 'Segoe UI', 'Microsoft YaHei'}")
        self.isEnter = False
        self.isSelected = False
        self.pressedPos = None

    def enterEvent(self, e):
        super().enterEvent(e)
        self.isEnter = True
        self.update()

    def leaveEvent(self, e):
        super().leaveEvent(e)
        self.isEnter = False
        self.update()

    def mousePressEvent(self, e):
        self.pressedPos = getPressedPos(self, e)
        self.update()
        super().mousePressEvent(e)

    def mouseReleaseEvent(self, e):
        self.pressedPos = None
        self.update()
        super().mouseReleaseEvent(e)

    def paintEvent(self, e):
        painter = QPainter(self)
        painter.setPen(Qt.NoPen)
        if self.isEnter:
            brush = QBrush(QColor(0, 0, 0, 20))
            painter.setBrush(brush)
            painter.drawRect(self.rect())

    def setSelected(self, isSelected: bool):
        """ set selected state """
        self.isSelected = isSelected
        self.update()


class ToolButton(NavigationButton):
    """ Tool button """

    def __init__(self, iconPath, buttonSize=(60, 60), parent=None):
        """
        Parameters
        ----------
        iconPath: str
            icon path

        parent:
            parent window

        buttonSize: tuple
            button size
        """
        super().__init__(iconPath, "", buttonSize, parent)

    def paintEvent(self, e):
        """ paint button """
        super().paintEvent(e)
        painter = QPainter(self)
        painter.setPen(Qt.NoPen)
        painter.setRenderHints(QPainter.Antialiasing |
                               QPainter.SmoothPixmapTransform)

        if self.isSelected == True:
            if not self.pressedPos:
                brush = QBrush(QColor(0, 107, 133))
                painter.setBrush(brush)
                painter.drawRect(0, 1, 4, self.height() - 2)
            elif self.pressedPos in ["left-top", "right-bottom", "top"]:
                # 绘制选中标志
                self.drawLine(
                    painter, 2, 2, 6, 2, 4, self.height() - 2, 0, self.height() - 2)
            elif self.pressedPos in ["left-bottom", "right-top", "bottom"]:
                self.drawLine(
                    painter, 0, 1, 4, 1, 6, self.height() - 2, 2, self.height() - 2)
            elif self.pressedPos in ["left", "right", "center"]:
                self.drawLine(
                    painter, 1, 2, 5, 2, 5, self.height() - 2, 1, self.height() - 2)

        # paint icon
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

    def drawIcon(self, painter, image: QPixmap, shearX: float = 0, shearY: float = 0, x=0, y=0):
        """ draw icon """
        painter.shear(shearX, shearY)
        painter.drawPixmap(x, y, image.width(), image.height(), image)

    def drawLine(self, painter, x1, y1, x2, y2, x3, y3, x4, y4):
        """ draw selected line """
        painter.setPen(Qt.NoPen)
        brush = QBrush(QColor(0, 107, 133))
        painter.setBrush(brush)
        points = [QPoint(x1, y1), QPoint(x2, y2),
                  QPoint(x3, y3), QPoint(x4, y4)]
        painter.drawPolygon(QPolygon(points), 4)


class PushButton(NavigationButton):
    """ Push button """

    def paintEvent(self, e):
        """ paint button """
        super().paintEvent(e)
        painter = QPainter(self)
        painter.setPen(Qt.NoPen)
        painter.setRenderHints(
            QPainter.Antialiasing
            | QPainter.TextAntialiasing
            | QPainter.SmoothPixmapTransform
        )

        # paint selected line
        painter.setPen(Qt.NoPen)
        if self.isSelected == True:
            if not self.pressedPos:
                brush = QBrush(QColor(0, 107, 133))
                painter.setBrush(brush)
                painter.drawRect(0, 1, 4, self.height() - 2)

            elif self.pressedPos in ["left-top", "top"]:
                self.drawLine(
                    painter, 5, 2, 9, 2, 7, self.height() - 2, 3, self.height() - 2)
            elif self.pressedPos in ["left-bottom", "bottom"]:
                self.drawLine(
                    painter, 3, 2, 7, 2, 9, self.height() - 3, 5, self.height() - 3)
            elif self.pressedPos in ["left", "center"]:
                self.drawLine(
                    painter, 5, 2, 9, 2, 9, self.height() - 2, 5, self.height() - 2)
            elif self.pressedPos == "right-top":
                self.drawLine(
                    painter, 0, 2, 4, 2, 3, self.height() - 2, 0, self.height() - 2)
            elif self.pressedPos == "right":
                self.drawLine(
                    painter, 1, 1, 5, 1, 5, self.height() - 1, 1, self.height() - 1)
            elif self.pressedPos == "right-bottom":
                self.drawLine(
                    painter, 0, 2, 3, 2, 4, self.height() - 2, 0, self.height() - 2)

        # paint icon and text
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
            self.drawTextIcon(painter, image, 0, 0, 7, 2, 63)
        elif self.pressedPos == "right-top":
            self.drawTextIcon(painter, self.image, -0.02, 0)
        elif self.pressedPos == "right":
            image = self.image.scaled(
                self.image.width() - 2,
                self.image.height() - 2,
                Qt.KeepAspectRatio,
                Qt.SmoothTransformation,
            )
            self.drawTextIcon(painter, image, 0, 0, 3, 1, 61)
        elif self.pressedPos == "right-bottom":
            image = self.image.scaled(
                self.image.width() - 2,
                self.image.height() - 2,
                Qt.KeepAspectRatio,
                Qt.SmoothTransformation,
            )
            self.drawTextIcon(painter, image, -0.02, 0, 0, 1)

    def drawTextIcon(self, painter, image, shearX=0, shearY=0, iconX=0, iconY=0, textX=60, textY=20):
        """ draw text and icon """
        painter.shear(shearX, shearY)
        painter.drawPixmap(iconX, iconY+1, image.width(),
                           image.height(), image)

        if not self.text():
            return

        color = Qt.white if config.theme == 'dark' else Qt.black
        painter.setPen(color)
        painter.setFont(self.font())
        text = painter.fontMetrics().elidedText(self.text(), Qt.ElideRight, 320)
        names = ["myMusicButton", "historyButton",
                 "playingButton", "settingButton"]
        if self.objectName() in names:
            painter.drawText(textX, textY + 14, text)
        else:
            painter.drawText(textX, textY + 18, text)

    def drawLine(self, painter, x1, y1, x2, y2, x3, y3, x4, y4):
        """ paint selected line """
        painter.setPen(Qt.NoPen)
        brush = QBrush(QColor(0, 107, 133))
        painter.setBrush(brush)
        points = [QPoint(x1, y1), QPoint(x2, y2),
                  QPoint(x3, y3), QPoint(x4, y4)]
        painter.drawPolygon(QPolygon(points), 4)


class CreatePlaylistButton(NavigationButton):
    """ Create playlist button """

    def __init__(self, parent):
        self.iconPath = NIF.create(NIF.ADD)
        super().__init__(self.iconPath, parent=parent)

    def paintEvent(self, e):
        """ paint icon """
        super().paintEvent(e)
        painter = QPainter(self)
        painter.setPen(Qt.NoPen)
        painter.setRenderHints(QPainter.Antialiasing |
                               QPainter.SmoothPixmapTransform)

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
        """ paint icon """
        painter.shear(shearX, shearY)
        painter.drawPixmap(x, y, image.width(), image.height(), image)
