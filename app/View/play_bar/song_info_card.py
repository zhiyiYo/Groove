# coding:utf-8
import re

from common.cover import Cover
from common.database.entity import SongInfo
from components.widgets.label import FadeInLabel
from components.widgets.perspective_widget import PerspectiveWidget
from PyQt5.QtCore import Qt, QTimer, pyqtSignal
from PyQt5.QtGui import QFont, QFontMetrics, QPainter, QPixmap
from PyQt5.QtWidgets import QWidget


class SongInfoCard(PerspectiveWidget):
    """ Song information card """

    clicked = pyqtSignal()
    albumChanged = pyqtSignal(str)
    MAXWIDTH = 405

    def __init__(self, songInfo: SongInfo, parent=None):
        super().__init__(parent, True)
        self.__setSongInfo(songInfo)
        self.coverPath = ""

        self.albumCoverLabel = FadeInLabel(self)
        self.windowMask = WindowMask(self, (0, 0, 0, 25))
        self.textWindow = ScrollTextWindow(songInfo, self)

        self.__initWidget()

    def __initWidget(self):
        """ initialize widgets """
        self.resize(115 + 15 + self.textWindow.width() + 25, 115)
        self.setAttribute(Qt.WA_StyledBackground | Qt.WA_TranslucentBackground)
        self.textWindow.move(130, 0)
        self.albumCoverLabel.resize(115, 115)

        self.__setAlbumCover()

        if not self.songInfo:
            self.hide()

    def __setSongInfo(self, songInfo: SongInfo):
        """ set song information """
        self.songInfo = songInfo
        self.songName = self.songInfo.title or ''
        self.singer = self.songInfo.singer or ''

    def updateWindow(self, songInfo: SongInfo):
        """ update song information card """
        self.setVisible(bool(songInfo))
        if not songInfo:
            return

        self.show()
        self.__setSongInfo(songInfo)
        self.textWindow.updateWindow(songInfo)
        self.setFixedWidth(115 + 15 + self.textWindow.width() + 25)
        self.__setAlbumCover()

    def enterEvent(self, e):
        super().enterEvent(e)
        self.windowMask.show()

    def leaveEvent(self, e):
        self.windowMask.hide()

    def mouseReleaseEvent(self, e):
        super().mouseReleaseEvent(e)
        self.clicked.emit()

    def adjustSize(self):
        self.textWindow.adjustSize()
        self.setFixedWidth(115 + 15 + self.textWindow.width() + 25)

    def __setAlbumCover(self):
        """ set album cover """
        if self.songInfo.album is None:
            self.hide()
            return

        coverPath = Cover(self.singer, self.songInfo.album).path()
        if coverPath == self.coverPath:
            return

        self.albumChanged.emit(coverPath)
        self.coverPath = coverPath
        self.albumCoverLabel.setPixmap(QPixmap(coverPath).scaled(
            115, 115, Qt.KeepAspectRatioByExpanding, Qt.SmoothTransformation))


class ScrollTextWindow(QWidget):
    """ Scroll text window """

    def __init__(self, songInfo: SongInfo, parent=None):
        super().__init__(parent)
        self.maxWidth = 250
        self.setMaximumWidth(250)
        self.pattern = re.compile(
            r"""^[a-zA-Z0-9\\/:<>\?\.\*;,&#@\$~`!-'"\^\+\(\)]+$""")

        # refreshed time and moving distance
        self.timeStep = 19
        self.moveStep = 1

        # spacing between two strings
        self.spacing = 25

        # create timers
        self.songPauseTimer = QTimer(self)
        self.songNameTimer = QTimer(self)
        self.singerNameTimer = QTimer(self)
        self.singerPauseTimer = QTimer(self)

        self.__initWidget()
        self.updateWindow(songInfo)

    def __initWidget(self):
        """ initialize widgets """
        self.setFixedHeight(115)
        self.setAttribute(Qt.WA_StyledBackground)

        self.songPauseTimer.setInterval(400)
        self.singerPauseTimer.setInterval(400)
        self.songNameTimer.setInterval(self.timeStep)
        self.singerNameTimer.setInterval(self.timeStep)
        self.songNameTimer.timeout.connect(self.__updateSongIndex)
        self.singerNameTimer.timeout.connect(self.__updateSingerIndex)
        self.songPauseTimer.timeout.connect(self.__restartTextTimer)
        self.singerPauseTimer.timeout.connect(self.__restartTextTimer)

    def __setSongInfo(self, songInfo: SongInfo):
        """ set song information """
        self.songInfo = songInfo
        self.songName = self.songInfo.title or ''
        self.singer = self.songInfo.singer or ''

    def __resetFlags(self):
        """ reset flags """
        self.songCurrentIndex = 0
        self.singerCurrentIndex = 0
        self.isSongNameAllOut = False
        self.isSingerAllOut = False

    def __adjustWidth(self, maxWidth=None):
        """ adjust window width according to the length of text """
        maxWidth = maxWidth or self.maxWidth
        fonts = ["Segoe UI", "Microsoft YaHei"]

        # width of song name
        font = fonts[self.pattern.match(self.songName) is None]
        self.songFont = QFont(font, 14)
        fontMetrics = QFontMetrics(self.songFont)
        self.songNameWidth = fontMetrics.width(self.songName)

        # width of singer name
        font = fonts[self.pattern.match(self.singer) is None]
        self.singerFont = QFont(font, 12, 75)
        self.singerFont.setPixelSize(19)
        fontMetrics = QFontMetrics(self.singerFont)
        self.singerWidth = fontMetrics.width(self.singer)

        # is there a string that exceeds the maximum width of songInfoCard
        self.isSongTooLong = self.songNameWidth > maxWidth
        self.isSingerTooLong = self.singerWidth > maxWidth

        # set the width of window
        w = max(self.songNameWidth, self.singerWidth)
        self.setFixedWidth(min(w, maxWidth))

    def updateWindow(self, songInfo: SongInfo):
        """ update window """
        self.__resetFlags()
        self.__setSongInfo(songInfo)
        self.__adjustWidth()
        self.update()

    def __updateSongIndex(self):
        """ update the index of song name """
        self.update()
        self.songCurrentIndex += 1

        if self.songCurrentIndex*self.moveStep >= self.songNameWidth + self.spacing*self.isSongNameAllOut:
            self.songCurrentIndex = 0
            self.isSongNameAllOut = True

    def __updateSingerIndex(self):
        """ update the index of singer name """
        self.update()
        self.singerCurrentIndex += 1

        if self.singerCurrentIndex*self.moveStep >= self.singerWidth + self.spacing*self.isSingerAllOut:
            self.singerCurrentIndex = 0
            self.isSingerAllOut = True

    def setMaxWidth(self, width: int):
        """ set the maximun width of song information card """
        self.maxWidth = width
        self.__resetFlags()
        self.__adjustWidth()

    def adjustSize(self):
        self.__adjustWidth(float('inf'))

    def paintEvent(self, e):
        """ paint text """
        painter = QPainter(self)
        painter.setRenderHints(QPainter.Antialiasing |
                               QPainter.TextAntialiasing)
        painter.setPen(Qt.white)

        # paint song name
        painter.setFont(self.songFont)
        if self.isSongTooLong:
            # in fact, two complete strings have been drawn.

            # the first string
            x1 = self.spacing*self.isSongNameAllOut - self.moveStep*self.songCurrentIndex
            painter.drawText(x1, 54, self.songName)

            # the second string
            x2 = self.songNameWidth - self.moveStep*self.songCurrentIndex + \
                self.spacing*(1 + self.isSongNameAllOut)
            painter.drawText(x2, 54, self.songName)

            # after one loop, scrolling will stop.
            if self.isSongNameAllOut and not (x1 and x2):
                if not self.__isNotLeave():
                    self.songNameTimer.stop()
                else:
                    self.songNameTimer.stop()
                    self.songPauseTimer.start()
        else:
            painter.drawText(0, 54, self.songName)

        # paint singer name
        painter.setFont(self.singerFont)
        if self.isSingerTooLong:
            x3 = self.spacing*self.isSingerAllOut - self.moveStep*self.singerCurrentIndex
            x4 = self.singerWidth - self.moveStep*self.singerCurrentIndex + \
                self.spacing*(1 + self.isSingerAllOut)
            painter.drawText(x3, 82, self.singer)
            painter.drawText(x4, 82, self.singer)

            if self.isSingerAllOut and not (x3 and x4):
                if not self.__isNotLeave():
                    self.singerNameTimer.stop()
                else:
                    self.singerNameTimer.stop()
                    self.singerPauseTimer.start()
        else:
            painter.drawText(0, 82, self.singer)

    def enterEvent(self, e):
        if self.isSongTooLong and not self.songNameTimer.isActive():
            self.songNameTimer.start()
        if self.isSingerTooLong and not self.singerNameTimer.isActive():
            self.singerNameTimer.start()

    def __restartTextTimer(self):
        """ retart text timer """
        self.sender().stop()
        if self.sender() == self.songPauseTimer:
            self.songNameTimer.start()
        else:
            self.singerNameTimer.start()

    def __isNotLeave(self) -> bool:
        """ determine whether the mouse has left the window """
        if not self.isWindow():
            globalPos = self.parent().mapToGlobal(self.pos())
        else:
            globalPos = self.pos()

        globalX = globalPos.x()
        globalY = globalPos.y()

        x = globalX <= self.cursor().pos().x() <= globalX + self.width()
        y = globalY <= self.cursor().pos().y() <= globalY + self.height()
        return x and y


class WindowMask(QWidget):
    """ Window mask """

    def __init__(self, parent, maskColor: tuple = (255, 255, 255, 172)):
        super().__init__(parent)
        self.setWindowFlag(Qt.FramelessWindowHint)
        self.setAttribute(Qt.WA_StyledBackground)
        r, g, b, a = maskColor
        self.setStyleSheet(f'background:rgba({r},{g},{b},{a});')
        self.hide()

    def show(self):
        parent_rect = self.parent().geometry()
        self.setGeometry(0, 0, parent_rect.width(), parent_rect.height())
        self.raise_()
        super().show()
