# coding:utf-8
from typing import List
import bisect

from common.lyric import Lyric
from common.config import config
from common.signal_bus import signalBus
from common.auto_wrap import TextWrap
from common.style_sheet import setStyleSheet
from components.widgets.scroll_area import ScrollArea
from PyQt5.QtCore import Qt, QPropertyAnimation, QEventLoop
from PyQt5.QtGui import QColor, QLinearGradient, QPalette, QBrush, QFont
from PyQt5.QtWidgets import QApplication, QLabel, QVBoxLayout, QWidget


class LyricWidget(ScrollArea):
    """ Lyrics widget """

    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.lyric = None  # type:Lyric
        self.times = []
        self.currentIndex = -1
        self.lyricLabels = []  # type:List[LyricLabel]
        self.__unusedlyricLabels = []  # type:List[LyricLabel]
        self.__isUpdating = False

        self.scrollAni = QPropertyAnimation(
            self.verticalScrollBar(), b'value', self)
        self.scrollWidget = QWidget(self)
        self.vBoxLayout = QVBoxLayout(self.scrollWidget)
        self.loadingLabel = QLabel(self.tr('Loading lyrics...'), self)

        self.__initWidget()

    def __initWidget(self):
        """ initialize widgets """
        self.resize(800, 800)
        self.setWidget(self.scrollWidget)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.scrollWidget.resize(800, 800)
        self.vBoxLayout.setContentsMargins(0, 160, 0, 160)
        self.vBoxLayout.setSpacing(45)
        self.loadingLabel.hide()
        self.__setQss()

        signalBus.lyricFontChanged.connect(self.__onLyricFontChanged)
        self.verticalScrollBar().valueChanged.connect(self.__adjustTextColor)

    def setLyric(self, lyric: Lyric):
        """ set lyrics """
        if self.lyric == lyric:
            self.setLoadingState(False)
            return

        self.__isUpdating = True
        self.scrollAni.stop()

        self.lyric = lyric
        self.times = self.lyric.times()
        self.currentIndex = -1

        # update lyrics
        N = len(self.lyricLabels)
        N_ = len(self.times)

        if N < N_:
            for t in self.times[N:]:
                if self.__unusedlyricLabels:
                    label = self.__unusedlyricLabels.pop()
                    label.setLyric(self.lyric[t])
                    label.show()
                else:
                    label = LyricLabel(self.lyric[t], self.scrollWidget)

                self.lyricLabels.append(label)
                self.vBoxLayout.addWidget(label, 0, Qt.AlignHCenter)
                QApplication.processEvents(QEventLoop.ExcludeUserInputEvents)
        elif N > N_:
            for i in range(N - N_):
                label = self.lyricLabels.pop()
                self.vBoxLayout.removeWidget(label)
                self.__unusedlyricLabels.append(label)
                label.hide()
                QApplication.processEvents(QEventLoop.ExcludeUserInputEvents)

        n = min(N, N_)
        for label, t in zip(self.lyricLabels[:n], self.times[:n]):
            label.setLyric(self.lyric[t])

        self.setStyle(QApplication.style())
        QApplication.processEvents()
        self.scrollWidget.adjustSize()
        self.verticalScrollBar().setValue(0)
        self.setLoadingState(False)

        self.__isUpdating = False

    def setCurrentTime(self, time: int):
        """ set current time

        Parameters
        ----------
        time: int
            time in milliseconds
        """
        if self.__isUpdating:
            return

        time = str(time/1000)
        if not self.times:
            return

        # get index of time
        times = [float(i) for i in self.times]
        i = bisect.bisect_left(times, float(time))
        i = min(len(self.times)-1, i)
        if float(time) < times[i]:
            i -= 1

        if i == self.currentIndex:
            return

        # update the style of lyrics
        if self.currentIndex >= 0:
            self.lyricLabels[self.currentIndex].setPlay(False)

        self.currentIndex = i
        label = self.lyricLabels[i]
        label.setPlay(True)
        self.scrollWidget.adjustSize()

        # scroll lyrics
        y = label.y() - self.verticalScrollBar().value()
        dy = y - self.height()//2 + label.height()//2
        self.scrollAni.setStartValue(self.verticalScrollBar().value())
        self.scrollAni.setEndValue(dy+self.verticalScrollBar().value())
        self.scrollAni.setDuration(350)
        self.scrollAni.start()

    def __adjustTextColor(self):
        """ adjust text color """
        hideBottom = False
        for label in self.lyricLabels:
            vh = label.visibleRegion().boundingRect().height()
            h = label.height()

            alpha = 255 if label.isPlay else 255*0.6
            color = QColor(255, 255, 255, alpha)

            palette = QPalette()

            if vh == h:
                label.setForegroundRole(QPalette.Text)
                palette.setBrush(QPalette.Text, color)
                label.setPalette(palette)

            elif vh > 0 and vh < h:
                hideBottom = label.y() - self.verticalScrollBar().value() > 0

                label.setForegroundRole(QPalette.Text)
                gradient = QLinearGradient(0, 0, 0, h)

                if not hideBottom:
                    gradient.setColorAt(1-vh/h, QColor(255, 255, 255, 0))
                    gradient.setColorAt(1, color)
                else:
                    gradient.setColorAt(0, color)
                    gradient.setColorAt(vh/h, QColor(255, 255, 255, 0))

                palette.setBrush(QPalette.Text, QBrush(gradient))
                label.setPalette(palette)
                hideBottom = True

            if vh == 0 and hideBottom:
                break

    def resizeEvent(self, e):
        self.scrollWidget.setFixedWidth(self.width())
        self.loadingLabel.move(
            self.width()//2-self.loadingLabel.width()//2, 160)
        self.__adjustTextColor()

    def __setQss(self):
        """ set style sheet """
        self.loadingLabel.setObjectName('loadingLabel')
        setStyleSheet(self, 'lyric_widget')
        self.loadingLabel.adjustSize()
        self.loadingLabel.move(
            self.width()//2-self.loadingLabel.width()//2, 160)

    def setLoadingState(self, isLoading: bool):
        """ set the loading state of lyrics """
        self.loadingLabel.setVisible(isLoading)
        self.scrollWidget.setVisible(not isLoading)

    def __onLyricFontChanged(self):
        """ lyric font changed slot """
        font = config.lyricFont
        for label in self.lyricLabels:
            label.setFont(font)

        for label in self.__unusedlyricLabels:
            label.setFont(font)


class LyricLabel(QLabel):
    """ lyric label """

    def __init__(self, lyric: List[str], parent=None):
        """
        Parameters
        ----------
        lyric: List[str]
            lyric list, including original lyric and translated lyrics (optional)

        parent:
            parent window
        """
        super().__init__(parent=parent)
        self.maxCharacters = 50
        self.setAlignment(Qt.AlignCenter)
        self.setLyric(lyric)

    def setLyric(self, lyric: List[str]):
        """ set lyric """
        self.lyric = lyric
        wrapLyric = [TextWrap.wrap(i, self.maxCharacters)[0] for i in lyric]
        self.setText('\n'.join(wrapLyric))
        self.setPlay(False)

    def setPlay(self, isPlay: bool):
        """ set the play state of lyric """
        self.isPlay = isPlay

        # change font color
        palette = QPalette()
        self.setForegroundRole(QPalette.Text)
        alpha = 255 if isPlay else 255*0.6
        palette.setBrush(QPalette.Text, QColor(255, 255, 255, alpha))
        self.setPalette(palette)

        # change font size
        font = config.lyricFont  # type:QFont
        if isPlay:
            font.setPixelSize(int(font.pixelSize()*1.25))

        self.setFont(font)
        self.adjustSize()
