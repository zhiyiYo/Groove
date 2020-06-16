import json
import re
import sys
from ctypes import cdll, c_bool
from ctypes.wintypes import HWND

from PyQt5.QtCore import QRect, QSize, Qt, QEvent
from PyQt5.QtGui import QColor, QPainter, QPen, QPixmap
from PyQt5.QtWidgets import (QAction, QApplication, QDialog, QHBoxLayout,
                             QLabel, QPushButton)


class PropertyPanel(QDialog):
    """ 创建属性面板类 """

    def __init__(self, songInfo):
        super().__init__()

        self.songInfo = songInfo
        self.resize(942, 590)
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.pen = QPen(QColor(0, 153, 188))

        # 实例化标签
        self.yearLabel = QLabel('年', self)
        self.diskLabel = QLabel('光盘', self)
        self.tconLabel = QLabel('类型', self)
        self.durationLabel = QLabel('时长', self)
        self.propertyLabel = QLabel('属性', self)
        self.songerLabel = QLabel('歌曲歌手', self)
        self.songNameLabel = QLabel('歌曲名', self)
        self.trackNumberLabel = QLabel('曲目', self)
        self.songPathLabel = QLabel('文件位置', self)
        self.albumNameLabel = QLabel('专辑标题', self)
        self.albumSongerLabel = QLabel('专辑歌手', self)

        self.disk = QLabel('1', self)
        self.year = QLabel(songInfo['year'], self)
        self.tcon = QLabel(songInfo['tcon'], self)
        self.songer = QLabel(songInfo['songer'], self)
        self.albumName = QLabel(songInfo['album'][0], self)
        self.duration = QLabel(songInfo['duration'], self)
        self.songName = QLabel(songInfo['songname'], self)
        self.albumSonger = QLabel(songInfo['songer'], self)
        self.songPath = QLabel(songInfo['song_path'], self)
        if songInfo['suffix'] in ['.flac', '.mp3']:
            self.trackNumber = QLabel(songInfo['tracknumber'], self)
        elif songInfo['suffix'] == '.m4a':
            trackNUm = str(eval(songInfo['tracknumber'])[0])
            self.trackNumber = QLabel(trackNUm, self)

        # 实例化关闭按钮
        self.closeButton = QPushButton('关闭', self)

        self.label_list_1 = [self.albumName, self.songName,
                             self.songPath, self.songer, self.albumSonger]
        self.label_list_2 = [self.trackNumberLabel, self.trackNumber, self.diskLabel,
                             self.disk, self.albumNameLabel, self.albumName, self.albumSongerLabel,
                             self.albumSonger, self.tconLabel, self.tcon, self.durationLabel, self.duration,
                             self.yearLabel, self.year, self.songPathLabel, self.songPath, self.closeButton]

        # 初始化小部件的位置
        self.initWidget()
        self.adjustHeight()
        self.setDropShadowEffect()

        # 设置层叠样式
        self.setQss()

    def initWidget(self):
        """ 初始化小部件的属性 """
        self.tconLabel.move(28, 330)
        self.diskLabel.move(584, 168)
        self.yearLabel.move(652, 330)
        self.songerLabel.move(584, 90)
        self.propertyLabel.move(28, 27)
        self.songNameLabel.move(28, 90)
        self.songPathLabel.move(28, 408)
        self.albumNameLabel.move(28, 252)
        self.durationLabel.move(584, 330)
        self.trackNumberLabel.move(28, 168)
        self.albumSongerLabel.move(584, 252)

        self.tcon.move(28, 362)
        self.year.move(652, 362)
        self.disk.move(584, 202)
        self.songer.move(584, 122)
        self.songName.move(28, 122)
        self.songPath.move(28, 442)
        self.albumName.move(28, 282)
        self.duration.move(584, 362)
        self.trackNumber.move(28, 202)
        self.albumSonger.move(584, 282)
        self.closeButton.move(732, 535)

        # 设置按钮的大小
        self.closeButton.setFixedSize(170, 40)

        # 将关闭信号连接到槽函数
        self.closeButton.clicked.connect(self.close)

        # 设置自动折叠
        for label in self.label_list_1:
            label.setWordWrap(True)
            label.setScaledContents(True)
            if label in [self.songer, self.albumSonger]:
                label.setFixedWidth(291)
            elif label in [self.albumName, self.songName]:
                label.setFixedWidth(500)
            elif label == self.songPath:
                label.setFixedWidth(847)

        # 分配ID
        self.year.setObjectName('songer')
        self.songer.setObjectName('songer')
        self.duration.setObjectName('songer')
        self.songPath.setObjectName('songPath')
        self.albumSonger.setObjectName('songer')
        self.propertyLabel.setObjectName('propertyLabel')

    def adjustHeight(self):
        """ 如果有换行的发生就调整高度 """
        rex = r'[\)\.a-zA-Z、\d\(\s]+$'
        Match_1 = re.match(rex, self.songName.text())
        Match_2 = re.match(rex, self.songer.text())
        Match_3 = re.match(rex, self.albumName.text())
        Match_4 = re.match(rex, self.albumSonger.text())
        # 如果歌名或者歌手名不是全由英文和数字构成，只要长度大于16就会换行
        if not Match_1 or not Match_2:
            if len(self.songName.text()) > 16 or len(self.songer.text()) > 16:
                # 后面的所有标签向下平移25px
                for label in self.label_list_2:
                    label.move(label.geometry().x(), label.geometry().y() + 25)
                self.resize(self.width(), self.height() + 25)
        if not Match_3 or not Match_4:
            if len(self.albumName.text()) > 16 or len(self.albumSonger.text()) > 16:
                # 后面的所有标签向下平移25px
                for label in self.label_list_2[8:]:
                    label.move(label.geometry().x(), label.geometry().y() + 25)
                self.resize(self.width(), self.height() + 25)

    def setQss(self):
        """ 设置层叠样式表 """
        with open('resource\\css\\propertyPanel.qss', 'r', encoding='utf-8') as f:
            qss = f.read()
            self.setStyleSheet(qss)

    def paintEvent(self, event):
        """ 绘制背景和阴影 """
        painter = QPainter(self)
        # 绘制边框
        painter.setPen(self.pen)
        painter.drawRect(0, 0, self.width()-1, self.height()-1)

    def setDropShadowEffect(self):
        """ 添加阴影 """
        dll = cdll.LoadLibrary('acrylic_dll\\acrylic.dll')
        self.class_amanded = c_bool(False)
        self.hWnd = HWND(int(self.winId()))
        dll.addWindowShadow(c_bool(1), self.hWnd)


if __name__ == "__main__":
    with open('Data\\songInfo.json', 'r', encoding='utf-8') as f:
        songInfo_list = json.load(f)
    songInfo = songInfo_list[0]
    app = QApplication(sys.argv)
    demo = PropertyPanel(songInfo)
    demo.show()
    sys.exit(app.exec_())
