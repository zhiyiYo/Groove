# coding:utf-8
from typing import List, Dict
import bisect

from common.auto_wrap import autoWrap
from components.widgets.scroll_area import ScrollArea
from PyQt5.QtCore import Qt, QFile, QPropertyAnimation
from PyQt5.QtGui import QColor, QLinearGradient, QPalette, QBrush
from PyQt5.QtWidgets import QApplication, QLabel, QVBoxLayout, QWidget


class LyricWidget(ScrollArea):

    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.lyric = None
        self.times = []
        self.currentIndex = -1
        self.lyricLabels = []  # type:List[LyricLabel]
        self.__unusedlyricLabels = []  # type:List[LyricLabel]

        self.scrollAni = QPropertyAnimation(
            self.verticalScrollBar(), b'value', self)
        self.scrollWidget = QWidget(self)
        self.vBoxLayout = QVBoxLayout(self.scrollWidget)

        self.__initWidget()

    def __initWidget(self):
        """ 初始化小部件 """
        self.resize(800, 800)
        self.setWidget(self.scrollWidget)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setVerticalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        self.scrollWidget.resize(800, 800)
        self.vBoxLayout.setContentsMargins(0, 160, 0, 160)
        self.vBoxLayout.setSpacing(45)
        self.__setQss()

        self.verticalScrollBar().valueChanged.connect(self.__adjustTextColor)

    def setLyric(self, lyric: Dict[str, List[str]]):
        """ 设置歌词 """
        if self.lyric == lyric:
            return

        self.lyric = lyric
        self.times = list(self.lyric.keys())
        self.currentIndex = -1
        self.scrollAni.stop()
        self.verticalScrollBar().setValue(0)

        # 刷新歌词
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
        elif N > N_:
            for i in range(N - N_):
                label = self.lyricLabels.pop()
                self.vBoxLayout.removeWidget(label)
                self.__unusedlyricLabels.append(label)
                label.hide()

        n = min(N, N_)
        for label, t in zip(self.lyricLabels[:n], self.times[:n]):
            label.setLyric(self.lyric[t])

        self.setStyle(QApplication.style())
        self.scrollWidget.adjustSize()
        self.__adjustTextColor()

    def setCurrentTime(self, time: int):
        """ 设置当前时间

        Parameters
        ----------
        time: int
            以毫秒为单位的时间
        """
        time = str(time/1000)
        if not self.times:
            return

        # 确定索引
        times = [float(i) for i in self.times]
        i = bisect.bisect_left(times, float(time))
        i = min(len(self.times)-1, i)
        if float(time) < times[i]:
            i -= 1

        if i == self.currentIndex:
            return

        # 更新歌词样式
        if self.currentIndex >= 0:
            self.lyricLabels[self.currentIndex].setPlay(False)

        self.currentIndex = i
        label = self.lyricLabels[i]
        label.setPlay(True)
        self.scrollWidget.adjustSize()

        # 滚动歌词
        y = label.y() - self.verticalScrollBar().value()
        dy = y - self.height()//2 + label.height()//2
        self.scrollAni.setStartValue(self.verticalScrollBar().value())
        self.scrollAni.setEndValue(dy+self.verticalScrollBar().value())
        self.scrollAni.setDuration(350)
        self.scrollAni.start()

    def __adjustTextColor(self):
        """ 调整字体颜色 """
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
                # 判断是上面被隐藏还是下面被隐藏
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
        """ 调整窗口大小 """
        self.scrollWidget.setFixedWidth(self.width())
        self.__adjustTextColor()

    def __setQss(self):
        """ 设置层叠样式 """
        f = QFile(":/qss/lyric_widget.qss")
        f.open(QFile.ReadOnly)
        self.setStyleSheet(str(f.readAll(), encoding='utf-8'))
        f.close()


class LyricLabel(QLabel):
    """ 歌词标签 """

    def __init__(self, lyric: List[str], parent=None):
        """
        Parameters
        ----------
        lyric: List[str]
            歌词

        parent:
            父级窗口
        """
        super().__init__(parent=parent)
        self.maxCharacters = 50
        self.setAlignment(Qt.AlignCenter)
        self.setLyric(lyric)

    def setLyric(self, lyric: List[str]):
        """ 设置歌词 """
        self.lyric = lyric
        wrapLyric = [autoWrap(i, self.maxCharacters)[0] for i in lyric]
        self.setText('\n'.join(wrapLyric))
        self.setPlay(False)

    def setPlay(self, isPlay: bool):
        """ 设置歌词是否正在播放 """
        self.isPlay = isPlay

        # 改变字体颜色
        palette = QPalette()
        self.setForegroundRole(QPalette.Text)
        alpha = 255 if isPlay else 255*0.6
        palette.setBrush(QPalette.Text, QColor(255, 255, 255, alpha))
        self.setPalette(palette)

        # 改变字号
        self.setProperty('isPlay', 'true' if isPlay else 'false')
        self.setStyle(QApplication.style())
        self.adjustSize()
