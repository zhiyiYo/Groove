import sys

from PyQt5.QtCore import QEvent, QSize, Qt, pyqtSignal
from PyQt5.QtGui import QIcon
from PyQt5.QtWidgets import (QApplication, QHBoxLayout, QLabel, QPushButton,
                             QVBoxLayout, QWidget)

from my_widget.my_button import RandomPlayButton

from .songer_card_viewer import SongerCardViewer


class SongerTabInterface(QWidget):
    """ 定义专辑标签界面 """
    randomPlayAllSig = pyqtSignal()

    def __init__(self,parent=None):
        super().__init__(parent)

        # 实例化歌手头像视图
        self.songerHeadPortraitViewer = SongerCardViewer(parent)
        # 实例化随机播放按钮
        self.randomPlayButton = RandomPlayButton(slot=self.randomPlay,parent=self)
        # 实例化排序依据标签
        self.sortModeLabel_1 = QLabel('排序依据:', self)
        self.sortModeLabel_2 = QLabel('A到Z', self)
        # 实例化布局
        self.h_layout = QHBoxLayout()
        self.v_layout = QVBoxLayout()

        # 初始化小部件
        self.initWidget()
        # 初始化布局
        self.init_layout()
        #设置层叠样式
        self.setQss()

    def initWidget(self):
        """ 初始化小部件 """
        self.resize(1267, 827-23)

        songer_num = len(self.songerHeadPortraitViewer.songerInfo_list)
        self.randomPlayButton.setText(f'({songer_num})')
        # 分配ID
        self.setObjectName('songerTabInterface')
        self.sortModeLabel_1.setObjectName('sortMode')
        self.sortModeLabel_2.setObjectName('AToZ')

    def init_layout(self):
        """ 初始化布局 """
        self.h_layout.addWidget(self.randomPlayButton,0, Qt.AlignLeft)
        self.h_layout.addSpacing(34)
        self.h_layout.addWidget(self.sortModeLabel_1, 0, Qt.AlignLeft)
        self.h_layout.addWidget(self.sortModeLabel_2, 0, Qt.AlignLeft)
        # 不给按钮和标签分配多余的空间
        self.h_layout.addStretch(1)
        # 设置垂直布局
        self.v_layout.addSpacing(6)
        self.v_layout.addLayout(self.h_layout)
        self.v_layout.addSpacing(6)
        self.v_layout.addWidget(self.songerHeadPortraitViewer)
        self.v_layout.setContentsMargins(0,15,0,0)
        self.setLayout(self.v_layout)

    def randomPlay(self):
        """ 刷新并随机排列播放列表 """
        self.randomPlayAllSig.emit()

    def setQss(self):
        """ 设置层叠样式表 """
        with open('resource\\css\\songerTabInterface.qss') as f:
            qss = f.read()
            self.setStyleSheet(qss)