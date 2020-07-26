import sys

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QApplication, QLabel, QWidget, QHBoxLayout

sys.path.append('..')
from Groove.my_widget.my_slider import Slider

class PlayProgressBar(QWidget):
    """ 歌曲播放进度条 """
    def __init__(self, duration: str, parent=None):
        super().__init__(parent)
        # 创建两个标签和一个进度条
        self.progressSlider = Slider(Qt.Horizontal, self)
        self.currentTimeLabel = QLabel('0:00', self)
        self.totalTimeLabel = QLabel(duration, self)
        # 创建布局
        self.h_layout = QHBoxLayout()
        # 初始化界面
        self.initUI()
        #self.setQss()

    def initUI(self):
        """ 初始化小部件 """
        self.setFixedSize(438, 30)
        self.progressSlider.setObjectName('progressSlider')
        self.currentTimeLabel.setObjectName('timeLabel')
        self.totalTimeLabel.setObjectName('timeLabel')
        # 将小部件添加到布局中
        self.h_layout.addWidget(self.currentTimeLabel, 0, Qt.AlignHCenter)
        self.h_layout.addWidget(self.progressSlider, 0, Qt.AlignHCenter)
        self.h_layout.addWidget(self.totalTimeLabel, 0, Qt.AlignHCenter)
        self.h_layout.setContentsMargins(0, 0, 0, 0)
        self.h_layout.setSpacing(0)
        self.setLayout(self.h_layout)

    def setCurrentTime(self, currentTime):
        """ 更新当前时间标签，currentTime的单位为ms """
        seconds, minutes = self.getSecondMinute(currentTime)
        self.currentTimeLabel.setText(f'{minutes}:{str(seconds).rjust(2,"0")}')

    def setTotalTime(self, totalTime):
        """ 更新总时长标签，totalTime的单位为ms """
        seconds, minutes = self.getSecondMinute(totalTime)
        self.totalTimeLabel.setText(f'{minutes}:{str(seconds).rjust(2,"0")}')

    def getSecondMinute(self, time):
        """ 将毫秒转换为分和秒 """
        seconds = int(time / 1000)
        minutes = seconds // 60
        seconds -= minutes * 60
        return seconds,minutes

    def setQss(self):
        """ 设置层叠样式 """
        with open('resource\\css\\playBar.qss', encoding='utf-8') as f:
            self.setStyleSheet(f.read())


if __name__ == "__main__":
    app = QApplication(sys.argv)
    demo = PlayProgressBar('3:50')
    demo.show()
    sys.exit(app.exec_())
