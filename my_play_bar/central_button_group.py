import sys

from PyQt5.QtCore import Qt
from PyQt5.QtWidgets import QApplication, QHBoxLayout, QWidget,QVBoxLayout

from .play_bar_buttons import (LastSongButton, LoopModeButton, NextSongButton,
                              PlayButton, RandomPlayButton)


class CentralButtonGroup(QWidget):
    """ 播放按钮组 """
    def __init__(self, parent=None):
        super().__init__(parent)
        # 创建按钮
        self.createButtons()
        # 创建布局
        self.h_layout = QHBoxLayout()
        self.all_v_layout=QVBoxLayout(self)
        # 初始化界面
        self.initUI()

    def createButtons(self):
        """ 创建按钮 """
        self.randomPlayButton = RandomPlayButton(self)
        self.lastSongButton = LastSongButton(self)
        self.playButton = PlayButton(self)
        self.nextSongButton = NextSongButton(self)
        self.loopModeButton = LoopModeButton(self)
        self.button_list = [self.randomPlayButton, self.lastSongButton,
                            self.playButton, self.nextSongButton, self.loopModeButton]

    def initUI(self):
        """ 初始化界面 """
        self.setFixedSize(317,67+8+3)
        for i in range(5):
            self.h_layout.addWidget(self.button_list[i],0,Qt.AlignCenter)
            if i != 4:
                self.h_layout.addSpacing(16)
        self.h_layout.setSpacing(0)
        self.h_layout.setContentsMargins(0, 0, 0, 0)
        self.all_v_layout.addSpacing(8)
        self.all_v_layout.setSpacing(0)
        self.all_v_layout.setContentsMargins(0, 0, 0, 0)
        self.all_v_layout.addLayout(self.h_layout)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    demo = CentralButtonGroup()
    demo.setStyleSheet('background:red')
    demo.show()
    sys.exit(app.exec_())


