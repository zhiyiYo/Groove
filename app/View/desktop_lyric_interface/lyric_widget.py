# coding:utf-8
from common.config import config
from PyQt5.QtCore import Qt, pyqtSignal, QPropertyAnimation, pyqtProperty, QRectF
from PyQt5.QtGui import QPainter, QColor, QPen, QFont, QFontMetrics
from PyQt5.QtWidgets import QWidget


class LyricWidget(QWidget):
    """ Lyric widget """

    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.lyric = []
        self.duration = 0
        self.__colorPos = 0
        self.__originTextPos = 0
        self.__translationTextPos = 0
        self.colorAni = QPropertyAnimation(self, b'colorPos', self)
        self.originTextPosAni = QPropertyAnimation(self, b'originTextPos', self)
        self.translationTextPosAni = QPropertyAnimation(
            self, b'translationTextPos', self)

    def paintEvent(self, e):
        if not self.lyric:
            return

        painter = QPainter(self)
        painter.setRenderHints(QPainter.Antialiasing |
                               QPainter.TextAntialiasing)

        # set font family and size
        painter.setFont(self.lyricFont)

        # TODO:描边

        # 绘制底部文字
        painter.setPen(Qt.white)
        painter.drawText(self.originTextPos, 40, self.lyric[0])

        # 绘制前景色
        painter.setPen(QColor(*config['lyric.color']))
        rect = QRectF(self.originTextPos, -2, self.colorPos, self.lyricFont.pixelSize()+10)
        painter.drawText(rect, self.lyric[0])

    def setLyric(self, lyric: list, duration: int):
        """ set lyric

        Parameters
        ----------
        lyric: list
            list contains original lyric and translation lyric

        duration: int
            lyric duration in milliseconds
        """
        self.lyric = lyric
        self.duration = duration

        self.__colorPos = 0

        # start scroll animation if text is too long
        fontMetrics = QFontMetrics(self.lyricFont)
        originalWidth = fontMetrics.width(lyric[0])
        if originalWidth > self.width():
            x = self.width() - originalWidth
            self.startAnimation(self.originTextPosAni, x, 0)
        else:
            self.__originTextPos = self.width()/2 - originalWidth/2

        # start foreground color animation
        self.startAnimation(self.colorAni, 0, originalWidth)

    def getColorPos(self):
        return self.__colorPos

    def getOriginTextPos(self):
        return self.__originTextPos

    def getTranslationTextPos(self):
        return self.__translationTextPos

    def setColorPos(self, pos: int):
        self.__colorPos = pos
        self.update()

    def setOriginTextPos(self, pos: int):
        self.__originTextPos = pos
        self.update()

    def setTranslationTextPos(self, pos):
        self.__translationTextPos = pos
        self.update()

    def startAnimation(self, ani: QPropertyAnimation, start, end):
        ani.setStartValue(start)
        ani.setEndValue(end)
        ani.setDuration(self.duration)
        ani.start()

    @property
    def lyricFont(self):
        font = QFont("Microsoft YaHei")
        font.setPixelSize(config["lyric.font-size"])
        return font

    colorPos = pyqtProperty(float, getColorPos, setColorPos)
    originTextPos = pyqtProperty(float, getOriginTextPos, setOriginTextPos)
    translationTextPos = pyqtProperty(
        float, getTranslationTextPos, setTranslationTextPos)
