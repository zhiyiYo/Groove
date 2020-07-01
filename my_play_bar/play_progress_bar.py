import sys

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QApplication, QLabel, QWidget, QSlider, QHBoxLayout


class PlayProgressBar(QWidget):
    """ 歌曲播放进度条 """
    def __init__(self, duration:str,parent=None):
        super().__init__(parent)
        # 创建两个标签和一个进度条
        self.progressSlider = QSlider(Qt.Horizontal, self)
        self.currentTimeLabel = QLabel('0:00', self)
        self.totalTimeLabel = QLabel(duration, self)
        # 创建布局
        self.h_layout = QHBoxLayout()
        # 初始化界面
        self.initUI()
        #self.setQss()

    def initUI(self):
        """ 初始化小部件 """
        self.setFixedSize(438,30)
        self.progressSlider.setObjectName('progressSlider')
        self.currentTimeLabel.setObjectName('timeLabel')
        self.totalTimeLabel.setObjectName('timeLabel')
        # 将小部件添加到布局中
        self.h_layout.addWidget(self.currentTimeLabel,0,Qt.AlignHCenter)
        self.h_layout.addWidget(self.progressSlider,0,Qt.AlignHCenter)
        self.h_layout.addWidget(self.totalTimeLabel, 0, Qt.AlignHCenter)
        self.h_layout.setContentsMargins(0, 0, 0, 0)
        self.h_layout.setSpacing(0)
        self.setLayout(self.h_layout)

        
    def setQss(self):
        """ 设置层叠样式 """
        with open('resource\\css\\playBar.qss',encoding='utf-8') as f:
            self.setStyleSheet(f.read())

        
if __name__ == "__main__":
    app = QApplication(sys.argv)
    demo = PlayProgressBar('3:50')
    demo.show()
    sys.exit(app.exec_())
