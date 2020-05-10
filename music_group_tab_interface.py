import sys
import time
from PyQt5.QtCore import QPoint, QSize, Qt
from PyQt5.QtGui import QContextMenuEvent, QIcon, QFont, QResizeEvent
from PyQt5.QtWidgets import (QAction, QApplication, QHBoxLayout, QLabel,
                             QScrollBar, QVBoxLayout, QWidget)

from my_music_windows import MyMusicWindows
from getfont import onLoadFont


class MusicGroupTabInterface(QWidget):
    """ 创建一个本地音乐分组界面 """

    def __init__(self, songs_folder):
        super().__init__()

        # 实例化一个标签和一个竖直滚动条
        self.myMusicLabel = QLabel(self)
        self.scrollBar = QScrollBar(Qt.Vertical, self)

        # 实例化一个包含三个标签界面的QTabWidget
        self.myMusicWindows = MyMusicWindows(songs_folder)

        # 实例化两个布局
        self.all_h_layout = QHBoxLayout()
        self.v_layout = QVBoxLayout()

        # 初始化布局
        self.initLayout()
        self.initWidget()

        # 设置样式
        self.setQss()

    def initLayout(self):
        """ 初始化布局 """
        # self.v_layout.addSpacing(55)
        self.v_layout.addSpacing(40)
        self.v_layout.addWidget(self.myMusicLabel)
        self.v_layout.addWidget(self.myMusicWindows)

        self.all_h_layout.addSpacing(7)
        self.all_h_layout.addLayout(self.v_layout)
        self.all_h_layout.addWidget(self.scrollBar, 0, Qt.AlignRight)

        self.setLayout(self.all_h_layout)

    def initWidget(self):
        """ 初始化小部件的属性 """
        self.resize(1300, 852)
        self.setMinimumHeight(630)
        self.setMouseTracking(True)
        self.setWindowIcon(QIcon('resource\\images\\Shoko.png'))
        self.setWindowTitle('Groove')

        # 设置标签上的字
        self.myMusicLabel.setText('我的音乐')
        # 隐藏列表视图的滚动条
        self.myMusicWindows.songTag.songCardListWidget.setVerticalScrollBarPolicy(
            Qt.ScrollBarAlwaysOff)
        self.scrollBar.setMaximum(
            self.myMusicWindows.songTag.songCardListWidget.verticalScrollBar().maximum())

        # 将信号连接到槽函数
        self.scrollBar.valueChanged.connect(
            lambda: self.myMusicWindows.songTag.songCardListWidget.
            verticalScrollBar().setValue(self.scrollBar.value()))

        self.myMusicWindows.songTag.songCardListWidget.verticalScrollBar().valueChanged.connect(
            lambda: self.scrollBar.setValue(self.myMusicWindows.
            songTag.songCardListWidget.verticalScrollBar().value()))

        # 分配ID
        self.setObjectName('musicGroupTabInterface')
        self.myMusicLabel.setObjectName('myMusicLabel')
        self.scrollBar.setObjectName('musicGroupScrollBar')

    def setQss(self):
        """ 设置层叠样式表 """
        with open('resource\\css\\musicGroupTabInterface.qss', 'r', encoding='utf-8') as f:
            qss = f.read()
            self.setStyleSheet(qss)

    def resizeEvent(self, e: QResizeEvent):
        """ 当窗口大小发生改变时隐藏小部件 """
        self.myMusicWindows.songTag.songCardListWidget.setLineWidth(self.width()-33)
        

        if self.width() < 1156:
            # 窗口宽度大于956px且小于1156时显示年份标签，隐藏专辑按钮
            for song_card in self.myMusicWindows.songTag.songCardListWidget.song_card_list:
                song_card.albumButton.hide()
                song_card.yearTconDuration.durationLabel.hide()

        elif self.width() > 1156:
            # 窗口宽度大于1156时显示年份标签，显示专辑按钮
            for song_card in self.myMusicWindows.songTag.songCardListWidget.song_card_list:
                song_card.albumButton.show()
                song_card.yearTconDuration.durationLabel.show()


if __name__ == "__main__":

    app = QApplication(sys.argv)

    font = QFont(QApplication.font())
    font.setStyleStrategy(QFont.PreferAntialias)
    app.setFont(font)

    demo = MusicGroupTabInterface('D:\\KuGou')
    demo.show()
    
    sys.exit(app.exec_())
