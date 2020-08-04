import sys

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QApplication, QLabel, QWidget, QHBoxLayout

from my_widget.my_slider import Slider


class PlayProgressBar(QWidget):
    """ 歌曲播放进度条 """

    def __init__(self, duration: str='0:00', parent=None):
        super().__init__(parent)
        # 创建两个标签和一个进度条
        self.progressSlider = Slider(Qt.Horizontal, self)
        self.currentTimeLabel = QLabel('0:00', self)
        self.totalTimeLabel = QLabel(duration, self)
        # 初始化界面
        self.__initWidget()
        self.__setQss()

    def __initWidget(self):
        """ 初始化小部件 """
        self.setFixedHeight(38)
        self.progressSlider.move(73, 0)
        self.currentTimeLabel.move(33, 9)
        self.progressSlider.setObjectName('progressSlider')
        self.currentTimeLabel.setObjectName('timeLabel')
        self.totalTimeLabel.setObjectName('timeLabel')

    def setCurrentTime(self, currentTime):
        """ 更新当前时间标签，currentTime的单位为ms """
        seconds, minutes = self.getSecondMinute(currentTime)
        self.currentTimeLabel.setText(f'{minutes}:{str(seconds).rjust(2,"0")}')
        self.currentTimeLabel.move(33 - 9 * (len(self.totalTimeLabel.text()) - 4), 9)

    def setTotalTime(self, totalTime):
        """ 更新总时长标签，totalTime的单位为ms """
        seconds, minutes = self.getSecondMinute(totalTime)
        self.totalTimeLabel.setText(f'{minutes}:{str(seconds).rjust(2,"0")}')

    def getSecondMinute(self, time):
        """ 将毫秒转换为分和秒 """
        seconds = int(time / 1000)
        minutes = seconds // 60
        seconds -= minutes * 60
        return seconds, minutes

    def __setQss(self):
        """ 设置层叠样式 """
        with open('resource\\css\\playProgressBar.qss', encoding='utf-8') as f:
            self.setStyleSheet(f.read())

    def resizeEvent(self, e):
        """ 改变尺寸时拉伸进度条 """
        self.progressSlider.resize(self.width() - 146, 38)
        self.totalTimeLabel.move(self.width() - 57, 10)
        super().resizeEvent(e)
        

