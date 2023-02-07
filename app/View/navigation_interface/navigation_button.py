# coding:utf-8
from common.config import config, Theme
from common.icon import getIconColor, drawSvgIcon
from PyQt5.QtCore import QPoint, Qt, QRectF, QSize
from PyQt5.QtGui import QBrush, QColor, QPainter, QPolygon, QPixmap
from PyQt5.QtWidgets import QPushButton

from common.get_pressed_pos import getPressedPos, Position


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
    def path(cls, iconType: str):
        """ create icon """
        path = f":/images/navigation_interface/{iconType}_{getIconColor()}.svg"
        return path


NIF = NavigationIconFactory


class NavigationButton(QPushButton):
    """ Navigation push button """

    def __init__(self, iconPath: str, text="", buttonSize: tuple = (60, 60), iconSize=(20, 20), parent=None):
        """
        Parameters
        ----------
        iconPath: str
            icon path

        text: str
            button text

        buttonSize: tuple
            button size

        iconSize: tuple
            icon size

        parent:
            parent window
        """
        super().__init__(text, parent)
        self.iconPath = iconPath
        self.setIconSize(QSize(*iconSize))
        self.setFixedSize(*buttonSize)
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

    def __init__(self, iconPath, buttonSize=(60, 60), iconSize=(20, 20), parent=None):
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
        super().__init__(iconPath, "", buttonSize, iconSize, parent)

    def paintEvent(self, e):
        """ paint button """
        super().paintEvent(e)
        painter = QPainter(self)
        painter.setPen(Qt.NoPen)
        painter.setRenderHints(QPainter.Antialiasing |
                               QPainter.SmoothPixmapTransform)

        if self.isSelected == True:
            if not self.pressedPos:
                brush = QBrush(QColor(0, 153, 188))
                painter.setBrush(brush)
                painter.drawRect(0, 1, 4, self.height() - 2)
            elif self.pressedPos in [Position.TOP_LEFT, Position.BOTTOM_RIGHT, Position.TOP]:
                # 绘制选中标志
                self.drawLine(
                    painter, 2, 2, 6, 2, 4, self.height() - 2, 0, self.height() - 2)
            elif self.pressedPos in [Position.BOTTOM_LEFT, Position.TOP_RIGHT, Position.BOTTOM]:
                self.drawLine(
                    painter, 0, 1, 4, 1, 6, self.height() - 2, 2, self.height() - 2)
            elif self.pressedPos in [Position.LEFT, Position.RIGHT, Position.CENTER]:
                self.drawLine(
                    painter, 1, 2, 5, 2, 5, self.height() - 2, 1, self.height() - 2)

        # paint icon
        if not self.pressedPos:
            self.drawIcon(painter)
        elif self.pressedPos in [Position.TOP_LEFT, Position.BOTTOM_RIGHT, Position.TOP]:
            self.drawIcon(painter, -0.05, 0)
        elif self.pressedPos in [Position.BOTTOM_LEFT, Position.TOP_RIGHT, Position.BOTTOM]:
            self.drawIcon(painter, 0.05, 0)
        elif self.pressedPos in [Position.LEFT, Position.RIGHT, Position.CENTER]:
            self.drawIcon(painter, 0, 0, 0, 0, 1)

    def drawIcon(self, painter, shearX=0, shearY=0, x=0, y=0, ds=0):
        """ draw icon """
        painter.shear(shearX, shearY)
        ds = y/2 if not ds else ds
        iw, ih = self.iconSize().width()-ds, self.iconSize().height()-ds
        rect = QRectF((60-iw)/2+x, (self.height()-ih)/2+y, iw, ih)
        drawSvgIcon(self.iconPath, painter, rect)

    def drawLine(self, painter, x1, y1, x2, y2, x3, y3, x4, y4):
        """ draw selected line """
        painter.setPen(Qt.NoPen)
        painter.setBrush(QColor(0, 153, 188))
        points = [QPoint(x1, y1), QPoint(x2, y2),
                  QPoint(x3, y3), QPoint(x4, y4)]
        painter.drawPolygon(QPolygon(points), 4)


class PushButton(NavigationButton):
    """ Push button """

    def paintEvent(self, e):
        """ paint button """
        super().paintEvent(e)
        painter = QPainter(self)
        painter.setRenderHints(
            QPainter.Antialiasing
            | QPainter.TextAntialiasing
            | QPainter.SmoothPixmapTransform
        )

        # paint selected line
        painter.setPen(Qt.NoPen)
        if self.isSelected == True:
            if not self.pressedPos:
                brush = QBrush(QColor(0, 153, 188))
                painter.setBrush(brush)
                painter.drawRect(0, 1, 4, self.height() - 2)

            elif self.pressedPos in [Position.TOP_LEFT, Position.TOP]:
                self.drawLine(
                    painter, 5, 2, 9, 2, 7, self.height() - 2, 3, self.height() - 2)
            elif self.pressedPos in [Position.BOTTOM_LEFT, Position.BOTTOM]:
                self.drawLine(
                    painter, 3, 2, 7, 2, 9, self.height() - 3, 5, self.height() - 3)
            elif self.pressedPos in [Position.LEFT, Position.CENTER]:
                self.drawLine(
                    painter, 5, 2, 9, 2, 9, self.height() - 2, 5, self.height() - 2)
            elif self.pressedPos == Position.TOP_RIGHT:
                self.drawLine(
                    painter, 0, 2, 4, 2, 3, self.height() - 2, 0, self.height() - 2)
            elif self.pressedPos == Position.RIGHT:
                self.drawLine(
                    painter, 1, 1, 5, 1, 5, self.height() - 1, 1, self.height() - 1)
            elif self.pressedPos == Position.BOTTOM_RIGHT:
                self.drawLine(
                    painter, 0, 2, 3, 2, 4, self.height() - 2, 0, self.height() - 2)

        # paint icon and text
        if not self.pressedPos:
            self.drawTextIcon(painter)
        elif self.pressedPos in [Position.TOP_LEFT, Position.TOP]:
            self.drawTextIcon(painter, -0.05, 0)
        elif self.pressedPos in [Position.BOTTOM_LEFT, Position.BOTTOM]:
            self.drawTextIcon(painter, 0.05, 0)
        elif self.pressedPos in [Position.LEFT, Position.CENTER]:
            self.drawTextIcon(painter, 0, 0, 3, 0, 63, ds=1)
        elif self.pressedPos == Position.TOP_RIGHT:
            self.drawTextIcon(painter, -0.02, 0)
        elif self.pressedPos == Position.RIGHT:
            self.drawTextIcon(painter, 0, 0, 1, 0, 61)
        elif self.pressedPos == Position.BOTTOM_RIGHT:
            self.drawTextIcon(painter, -0.02, 0, 0, 1)

    def drawTextIcon(self, painter, shearX=0, shearY=0, iconX=0, iconY=0, textX=60, textY=20, ds=0):
        """ draw text and icon """
        # draw icon
        painter.shear(shearX, shearY)
        ds = iconY/2 if not ds else ds
        iw, ih = self.iconSize().width()-ds, self.iconSize().height()-ds
        rect = QRectF((60-iw)/2+iconX, (self.height()-ih)/2+iconY+1, iw, ih)
        drawSvgIcon(self.iconPath, painter, rect)

        if not self.text():
            return

        # draw text
        color = Qt.white if config.theme == Theme.DARK else Qt.black
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
        painter.setBrush(QColor(0, 153, 188))
        points = [QPoint(x1, y1), QPoint(x2, y2),
                  QPoint(x3, y3), QPoint(x4, y4)]
        painter.drawPolygon(QPolygon(points), 4)


class CreatePlaylistButton(NavigationButton):
    """ Create playlist button """

    def __init__(self, parent):
        self.iconPath = NIF.path(NIF.ADD)
        super().__init__(self.iconPath, iconSize=(19, 19), parent=parent)

    def paintEvent(self, e):
        """ paint icon """
        super().paintEvent(e)
        painter = QPainter(self)
        painter.setPen(Qt.NoPen)
        painter.setRenderHints(QPainter.Antialiasing |
                               QPainter.SmoothPixmapTransform)

        if not self.pressedPos:
            self.drawIcon(painter)
        elif self.pressedPos in [Position.TOP_LEFT, Position.BOTTOM_RIGHT, Position.TOP]:
            self.drawIcon(painter, -0.05, 0)
        elif self.pressedPos in [Position.BOTTOM_LEFT, Position.TOP_RIGHT, Position.BOTTOM]:
            self.drawIcon(painter, 0.05, 0)
        elif self.pressedPos in [Position.LEFT, Position.RIGHT, Position.CENTER]:
            self.drawIcon(painter, 0, 0, 0, 0, 2)

    def drawIcon(self, painter, shearX=0, shearY=0, x=0, y=0, ds=0):
        """ draw icon """
        ds = y/2 if not ds else ds
        painter.shear(shearX, shearY)
        iw, ih = self.iconSize().width()-ds, self.iconSize().height()-ds
        rect = QRectF((60-iw)/2+x, (self.height()-ih)/2+y, iw, ih)
        drawSvgIcon(self.iconPath, painter, rect)
