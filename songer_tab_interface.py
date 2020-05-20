import re
import sys

import pinyin
from PyQt5.QtCore import QPoint, Qt, QEvent,QSize
from PyQt5.QtGui import QBitmap, QPainter, QPixmap, QIcon
from PyQt5.QtWidgets import (QApplication, QHBoxLayout, QLabel, QVBoxLayout, QPushButton,
                             QWidget)

from songer_head_portrait_viewer import SongerHeadPortraitViewer


class SongerTabInterface(QWidget):
    """ 定义专辑标签界面 """

    def __init__(self):
        super().__init__()

        # 实例化歌手头像视图
        self.songerHeadPortraitViewer = SongerHeadPortraitViewer()
        # 实例化随机播放按钮
        self.randomPlayButton = QPushButton(
            QIcon('resource\\images\\无序播放所有_130_17.png'), '', self)
        self.randomPlayButton.setIconSize(QSize(130,17))

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
        self.resize(1267, 684)

        songer_num=len(self.songerHeadPortraitViewer.songerInfo_list)
        self.randomPlayButton.setText(f'({songer_num})')
        

        # 设置无序播放按钮上的鼠标光标
        self.randomPlayButton.setCursor(Qt.PointingHandCursor)

        # 安装监听
        self.randomPlayButton.installEventFilter(self)

        # 分配ID
        self.setObjectName('songerTabInterface')
        self.randomPlayButton.setObjectName('randomPlayBt')
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

        self.v_layout.addSpacing(6)
        self.v_layout.addLayout(self.h_layout)
        self.v_layout.addSpacing(6)
        self.v_layout.addWidget(self.songerHeadPortraitViewer)
        self.v_layout.setContentsMargins(0,15,0,0)
        self.setLayout(self.v_layout)

    def eventFilter(self, obj, e):
        """ 当鼠标移入或移出按钮时更换图标 """
        if obj == self.randomPlayButton :
            if e.type() == QEvent.Enter or e.type() == QEvent.HoverMove:
                self.randomPlayButton.setIcon(
                    QIcon('resource\\images\\无序播放所有_hover_130_17.png'))
            elif e.type() == QEvent.Leave:
                self.randomPlayButton.setIcon(
                    QIcon('resource\\images\\无序播放所有_130_17.png'))

        return False

    def setQss(self):
        """ 设置层叠样式表 """
        with open('resource\\css\\songerTabInterface.qss') as f:
            qss = f.read()
            self.setStyleSheet(qss)


if __name__ == "__main__":
    app = QApplication(sys.argv)
    demo = SongerTabInterface()
    demo.show()
    sys.exit(app.exec_())
