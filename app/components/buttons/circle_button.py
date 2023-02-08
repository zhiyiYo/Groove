# coding:utf-8
from common.icon import drawSvgIcon
from PyQt5.QtCore import Qt, QEvent, QRectF, QSize
from PyQt5.QtGui import QPainter, QColor

from .tool_tip_button import ToolTipButton


class CircleButton(ToolTipButton):
    """ Circle button """

    def __init__(self, iconPath: str, parent=None, iconSize=(26, 26), buttonSize=(47, 47)):
        super().__init__(parent)
        self.iconPath = iconPath
        self.isEnter = False
        self.isPressed = False
        self.setIconSize(QSize(*iconSize))
        self.setFixedSize(*buttonSize)
        self.installEventFilter(self)

    def mousePressEvent(self, e):
        super().mousePressEvent(e)
        self.hideToolTip()

    def eventFilter(self, obj, e: QEvent):
        if obj is self:
            if e.type() == QEvent.Enter:
                self.isEnter = True
                self.update()
            elif e.type() == QEvent.Leave:
                self.isEnter = False
                self.update()
            elif e.type() == QEvent.MouseButtonPress:
                self.isPressed = True
                self.hideToolTip()
                self.update()
            elif e.type() in [QEvent.MouseButtonRelease, QEvent.MouseButtonDblClick]:
                self.isPressed = False
                self.update()

        return super().eventFilter(obj, e)

    def paintEvent(self, e):
        """ paint button """
        painter = QPainter(self)
        painter.setRenderHints(QPainter.Antialiasing |
                               QPainter.SmoothPixmapTransform)
        painter.setPen(Qt.NoPen)

        ds = 0
        if self.isPressed:
            painter.setBrush(QColor(255, 255, 255, 70))
            painter.drawEllipse(0, 0, self.width(), self.height())
            ds = 3
        elif self.isEnter:
            painter.setOpacity(0.5)

        # draw icon
        self._drawIcon(painter, ds)

    def _drawIcon(self, painter: QPainter, ds: int):
        iw, ih = self.iconSize().width()-ds, self.iconSize().height()-ds
        rect = QRectF((self.width()-iw)/2, (self.height()-ih)/2, iw, ih)
        drawSvgIcon(self.iconPath, painter, rect)

    def setIcon(self, iconPath: str):
        self.iconPath = iconPath
        self.update()

    def cancelHoverState(self):
        """ cancel button hover state """
        self.isEnter = False
        self.isPressed = False
        self.update()
        self.hideToolTip()


class CircleIconFactory:
    """ Circle button icon factory """

    PLAY = "Play"
    NEXT = "Next"
    MORE = "More"
    PAUSE = "Pause"
    SHUFFLE = "Shuffle"
    DOWNLOAD = "Download"
    PREVIOUS = "Previous"
    PLAYLIST = "Playlist"
    SKIP_BACK = "SkipBack"
    CHEVRON_UP = "ChevronUp"
    REPEAT_ALL = "RepeatAll"
    REPEAT_ONE = "RepeatOne"
    FULL_SCREEN = "FullScreen"
    SKIP_FORWARD = "SkipForward"
    DESKTOP_LYRIC = "DesktopLyric"
    BACK_TO_WINDOW = "BackToWindow"
    VOLUME0_WHITE = "Volume0_white"
    VOLUME0_BLACK = "Volume0_black"
    VOLUME1_WHITE = "Volume1_white"
    VOLUME1_BLACK = "Volume1_black"
    VOLUME2_WHITE = "Volume2_white"
    VOLUME2_BLACK = "Volume2_black"
    VOLUME3_WHITE = "Volume3_white"
    VOLUME3_BLACK = "Volume3_black"
    VOLUMEX_WHITE = "Volumex_white"
    VOLUMEX_BLACK = "Volumex_black"
    SMALLEST_PLAY_MODE = "SmallestPlayMode"

    @classmethod
    def path(cls, iconType: str):
        return f":/images/circle_button/{iconType}.svg"


CIF = CircleIconFactory
