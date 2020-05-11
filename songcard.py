import sys

from PyQt5.QtCore import QEvent, QPoint, Qt
from PyQt5.QtGui import QContextMenuEvent, QIcon, QMouseEvent, QResizeEvent
from PyQt5.QtWidgets import (QAction, QApplication, QCheckBox, QHBoxLayout,
                             QLabel, QLayout, QMenu, QPushButton, QSizePolicy,
                             QSpacerItem, QToolButton, QWidget)

from songcard_sub_unit import SongNameCard, TconYearDurationCard


class SongCard(QWidget):
    """ 定义一个歌曲卡类 """

    def __init__(self, songName, songer, album, tcon, year, duration):
        super().__init__()

        # 将形参设置为属性
        self.songer = songer
        self.album = album

        # 实例化小部件
        self.song_name_card = SongNameCard(songName)
        self.songerButton = QPushButton(self)
        self.albumButton = QPushButton(self)
        self.yearTconDuration = TconYearDurationCard(tcon, year, duration)

        # 实例化布局
        self.all_h_layout = QHBoxLayout()
        self.right_h_layout = QHBoxLayout()

        # 初始化小部件
        self.initWidget()

        # 初始化布局
        self.initLayout()
        # self.setQss()

    def initLayout(self):
        """ 初始化布局 """

        # 设置右侧的布局
        self.right_h_layout.addWidget(self.songerButton, 0, Qt.AlignLeft)
        self.right_h_layout.addSpacing(13)
        self.right_h_layout.addWidget(self.albumButton, 0, Qt.AlignLeft)
        self.right_h_layout.addWidget(self.yearTconDuration)

        # 设置全局布局
        self.all_h_layout.addWidget(self.song_name_card)
        self.all_h_layout.addLayout(self.right_h_layout)
        self.setLayout(self.all_h_layout)

        self.resizetimes = 0

    def initWidget(self):
        """ 初始化小部件 """

        self.songerButton.setFixedWidth(190)
        self.albumButton.setFixedWidth(190)
        self.songerButton.setText(self.songer)
        self.albumButton.setText(self.album)

        # 设置鼠标的光标
        self.songerButton.setCursor(Qt.PointingHandCursor)
        self.albumButton.setCursor(Qt.PointingHandCursor)

        # 分配按钮的ID
        self.songerButton.setObjectName('songerLinkBt')
        self.albumButton.setObjectName('albumLinkBt')

        # 分配标签的ID
        self.setObjectName('songCard')

        # 安装事件过滤器
        self.installEventFilter(self)

        # 将复选框状态改变的信号连接到槽函数
        """ self.song_name_card.songName.stateChanged.connect(
            self.refreshTextColor) """

    def setQss(self):
        """ 设置初始层叠样式 """
        with open('resource\\css\\initSongCard.qss', 'r', encoding='utf-8') as f:
            qss = f.read()
            self.setStyleSheet(qss)

    def setClickedQss(self):
        """ 设置点击后的样式 """
        with open('resource\\css\\clickedSongCard.qss', 'r', encoding='utf-8') as f:
            qss = f.read()
            self.setStyleSheet(qss)

    def eventFilter(self, obj, event):
        """ 当鼠标点击歌曲卡时将文本换成白色 """
        if obj == self:
            if event.type() == QEvent.Enter and not self.song_name_card.contextMenuSelecting:
                if not self.song_name_card.clicked:
                    self.song_name_card.showIndicator()
                    return False
                if self.song_name_card.clicked:
                    pass
            # 当歌曲卡不处于选择状态时使用hideIndicator.qss
            elif event.type() == QEvent.Leave and not self.song_name_card.contextMenuSelecting and not self.song_name_card.clicked:
                self.song_name_card.hideIndicator()

            if event.type() == QEvent.MouseButtonPress:
                self.song_name_card.clicked = True
                self.setClickedQss()

            # 当歌曲卡不处于选择状态时使用showIndicator.qss

        return QWidget.eventFilter(self, obj, event)

    def refreshTextColor(self):
        """ 根据复选框的状态来改变文本颜色 """
        if self.song_name_card.songName.isChecked():
            self.setClickedQss()
        else:
            self.setQss()

    def resizeEvent(self, e: QResizeEvent):
        """ 窗口大小改变时就改变专辑和歌手名标签的长度 """
        # 初始化时会改变大小
        self.resizetimes += 1

        if self.resizetimes == 2:
            self.originalWidth = self.width()
        if self.resizetimes > 2:
            deltaWidth = self.width() - self.originalWidth
            self.originalWidth = self.width()
            # 分配多出来的宽度
            self.albumButton.setFixedWidth(
                int(self.albumButton.width() + 0.7*deltaWidth))
            self.songerButton.setFixedWidth(
                int(self.songerButton.width() + 0.2*deltaWidth))


if __name__ == '__main__':
    app = QApplication(sys.argv)
    demo = SongCard('猫じゃらし', 'RADWIMPS', '泠鸢yousa、鹿乃、花丸晴琉、神楽七奈、物述有栖、白上吹雪、夏色祭',
                    'ロック', '2020', '4:02')
    demo.show()
    sys.exit(app.exec_())
