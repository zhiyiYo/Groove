# coding:utf-8
from typing import List, Dict
import bisect

from common.auto_wrap import autoWrap
from components.widgets.scroll_area import ScrollArea
from PyQt5.QtCore import Qt, QTimer, QFile, QPropertyAnimation, QEasingCurve
from PyQt5.QtWidgets import QApplication, QLabel, QVBoxLayout, QWidget


class LyricWidget(ScrollArea):

    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.lyric = None
        self.times = []
        self.currentIndex = -1
        self.lyricLabels = []  # type:List[LyricLabel]

        self.timer = QTimer(self)
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
        self.vBoxLayout.setContentsMargins(0, 260, 0, 260)
        self.vBoxLayout.setSpacing(45)
        self.__setQss()

        self.timer.setSingleShot(True)
        self.timer.timeout.connect(self.__scrollLyric)

        self.scrollAni.setEasingCurve(QEasingCurve.Linear)

    def setLyric(self, lyric: Dict[str, List[str]]):
        """ 设置歌词 """
        self.lyric = lyric
        self.times = list(self.lyric.keys())
        self.currentIndex = -1

        # 刷新歌词
        N = len(self.lyricLabels)
        N_ = len(self.times)

        if N < N_:
            for t in self.times[N:]:
                label = LyricLabel(self.lyric[t], self.scrollWidget)
                self.lyricLabels.append(label)
                self.vBoxLayout.addWidget(label, 0, Qt.AlignHCenter)
        elif N > N_:
            for i in range(N - N_):
                label = self.lyricLabels.pop()
                self.vBoxLayout.removeWidget(label)
                label.deleteLater()

        n = min(N, N_)
        for label, t in zip(self.lyricLabels[:n], self.times[:n]):
            label.setLyric(self.lyric[t])

        self.setStyle(QApplication.style())
        self.scrollWidget.adjustSize()

    def start(self):
        """ 从头开始歌词滚动 """
        t = float(self.times[0])*1000
        self.timer.start(t)

    def pause(self):
        """ 暂停歌词滚动 """
        self.timer.stop()

    def resume(self):
        """ 恢复歌词的滚动 """
        if not self.timer.isActive():
            self.timer.start()

    def setCurrentTime(self, time: int):
        """ 设置当前时间

        Parameters
        ----------
        time: int
            以毫秒为单位的时间
        """
        time = str(time/1000)

        # 确定索引
        times = [float(i) for i in self.times]
        i = bisect.bisect_left(times, float(time))
        if float(time) < times[i]:
            i -= 1

        self.currentIndex = i

    def __scrollLyric(self):
        """ 滚动歌词 """
        self.currentIndex += 1
        index = self.currentIndex

        if index > len(self.times)-1:
            return

        # 更新歌词样式
        if index >= 1:
            self.lyricLabels[index-1].setPlay(False)

        label = self.lyricLabels[index]
        label.setPlay(True)
        self.scrollWidget.adjustSize()

        # 滚动歌词
        y = label.y() - self.verticalScrollBar().value()
        dy = y - self.height()//2 + label.height()//2
        self.scrollAni.setStartValue(self.verticalScrollBar().value())
        self.scrollAni.setEndValue(dy+self.verticalScrollBar().value())

        # 更新定时器
        if index < len(self.times)-1:
            t = float(self.times[index+1])-float(self.times[index])
            self.scrollAni.setDuration(min(t*1000-10, 400))
            self.scrollAni.start()
            self.timer.start(t*1000)
        else:
            self.scrollAni.setDuration(400)
            self.scrollAni.start()

    def resizeEvent(self, e):
        """ 调整窗口大小 """
        self.scrollWidget.setFixedWidth(self.width())

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
        self.maxCharacters = 40
        self.setAlignment(Qt.AlignCenter)
        self.setLyric(lyric)

    def setLyric(self, lyric: List[str]):
        """ 设置歌词 """
        self.lyric = lyric
        wrapLyric = [autoWrap(i, self.maxCharacters)[0] for i in lyric]
        self.setText('\n'.join(wrapLyric))

        # 更新正在播放属性
        self.isPlay = False
        self.setProperty('isPlay', 'false')

    def setPlay(self, isPlay: bool):
        """ 设置歌词是否正在播放 """
        if self.isPlay == isPlay:
            return

        self.isPlay = isPlay
        self.setProperty('isPlay', 'true' if isPlay else 'false')
        self.setStyle(QApplication.style())
        self.adjustSize()
