# coding:utf-8

from app.common.get_cover_path import getCoverPath
from app.common.is_not_leave import isNotLeave
from app.components.buttons.three_state_button import ThreeStateButton
from app.components.slider import Slider
from PyQt5.QtCore import (
    QAbstractAnimation,
    QEasingCurve,
    QPropertyAnimation,
    Qt,
    QTimer,
)
from PyQt5.QtGui import QBrush, QFont, QFontMetrics, QPainter, QPixmap
from PyQt5.QtWidgets import QLabel, QWidget

from .play_button import PlayButton
from .system_volume import SystemVolume


class SubPlayWindow(QWidget):
    """ 桌面左上角子播放窗口 """

    def __init__(self, parent=None, songInfo: dict = None):
        super().__init__(parent)
        self.songInfo = {}
        if songInfo:
            self.songInfo = songInfo
        self.__lastSongIconPath = {
            "normal": r"app\resource\images\sub_play_window\lastSong_50_50_normal.png",
            "hover": r"app\resource\images\sub_play_window\lastSong_50_50_hover.png",
            "pressed": r"app\resource\images\sub_play_window\lastSong_50_50_pressed.png",
        }
        self.__nextSongIconPath = {
            "normal": r"app\resource\images\sub_play_window\nextSong_50_50_normal.png",
            "hover": r"app\resource\images\sub_play_window\nextSong_50_50_hover.png",
            "pressed": r"app\resource\images\sub_play_window\nextSong_50_50_pressed.png",
        }
        # 创建小部件
        self.volumeSlider = Slider(Qt.Vertical, self)
        self.volumeLabel = QLabel(self)
        self.lastSongButton = ThreeStateButton(self.__lastSongIconPath, self, (50, 50))
        self.playButton = PlayButton(self)
        self.nextSongButton = ThreeStateButton(self.__nextSongIconPath, self, (50, 50))
        self.albumPic = QLabel(self)
        self.songNameLabel = QLabel(self)
        self.songerNameLabel = QLabel(self)
        self.ani = QPropertyAnimation(self, b"windowOpacity")
        self.timer = QTimer(self)
        # 系统音量控制类
        self.systemVolume = SystemVolume()
        # 初始化
        self.__initWidget()

    def __initWidget(self):
        """ 初始化小部件 """
        self.resize(635, 175)
        self.__initLayout()
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.setWindowFlags(
            Qt.FramelessWindowHint | Qt.Window | Qt.WindowStaysOnTopHint
        )
        # 初始化音量滑块
        self.volumeSlider.setRange(0, 100)
        self.volumeSlider.setSingleStep(1)
        # 初始化动画和定时器
        self.timer.setInterval(3000)
        self.ani.setEasingCurve(QEasingCurve.Linear)
        self.ani.setDuration(700)
        self.ani.setStartValue(1)
        self.ani.setEndValue(0)
        # 分配ID
        self.volumeLabel.setObjectName("volumeLabel")
        self.songNameLabel.setObjectName("songNameLabel")
        self.songerNameLabel.setObjectName("songerNameLabel")
        # 设置层叠样式
        self.__setQss()
        # 将信号连接到槽
        self.__connectSignalToSlot()
        self.volumeSlider.setValue(self.systemVolume.getVolume())
        # 设置封面和标签
        self.updateWindow(self.songInfo)
        # 引用方法
        self.setPlay = self.playButton.setPlay

    def __initLayout(self):
        """ 初始化布局 """
        self.move(62, 75)
        self.albumPic.move(478, 25)
        self.playButton.move(222, 26)
        self.volumeLabel.move(32, 140)
        self.volumeSlider.move(34, 25)
        self.songNameLabel.move(122, 93)
        self.lastSongButton.move(122, 26)
        self.nextSongButton.move(322, 26)
        self.songerNameLabel.move(122, 135)
        self.albumPic.setFixedSize(125, 125)
        self.songNameLabel.setFixedWidth(285)
        self.songerNameLabel.setFixedWidth(290)
        self.volumeLabel.setFixedWidth(65)

    def updateWindow(self, songInfo: dict):
        """ 设置窗口内容 """
        self.songInfo = songInfo
        self.songName = self.songInfo.get("songName", "未知歌曲")
        self.songerName = self.songInfo.get("songer", "未知歌手")
        # 调整长度
        self.__adjustText()
        # 更新标签和专辑封面
        self.songNameLabel.setText(self.songName)
        self.songerNameLabel.setText(self.songerName)
        self.__setAlbumCover()

    def timerSlot(self):
        """ 定时器溢出时间 """
        self.timer.stop()
        self.ani.start()

    def enterEvent(self, e):
        """ 鼠标进入时停止动画并重置定时器 """
        self.timer.stop()
        if self.ani.state() == QAbstractAnimation.Running:
            self.ani.stop()
            self.setWindowOpacity(1)

    def leaveEvent(self, e):
        """ 鼠标离开窗口时打开计时器 """
        # 判断事件发生的位置发生在自己所占的rect内
        notLeave = isNotLeave(self)
        if not notLeave:
            self.timer.start()

    def show(self):
        """ show()时重置透明度并根据鼠标位置决定是否打开计时器 """
        self.setWindowOpacity(1)
        self.volumeSlider.setValue(self.systemVolume.getVolume())
        super().show()
        notLeave = isNotLeave(self)
        if not notLeave:
            self.timer.start()

    def paintEvent(self, e):
        """ 绘制背景色 """
        painter = QPainter(self)
        painter.setRenderHints(QPainter.Antialiasing)
        painter.setPen(Qt.NoPen)
        brush = QBrush(Qt.black)
        painter.setBrush(brush)
        # 绘制音量滑动条的背景
        painter.drawRect(0, 0, 81, 175)
        # 绘制控制面板的背景
        painter.drawRect(86, 0, 549, 175)

    def __connectSignalToSlot(self):
        """ 将信号连接到槽 """
        self.ani.finished.connect(self.hide)
        self.timer.timeout.connect(self.timerSlot)
        self.volumeSlider.valueChanged.connect(self.sliderValueChangedSlot)

    def __setQss(self):
        """ 设置层叠样式 """
        with open(r"app\resource\css\subPlayWindow.qss", encoding="utf-8") as f:
            self.setStyleSheet(f.read())

    def __setAlbumCover(self):
        """ 设置封面 """
        # 如果专辑信息为空就直接隐藏
        self.coverPath = getCoverPath(self.songInfo.get("modifiedAlbum"))
        self.albumPic.setPixmap(
            QPixmap(self.coverPath).scaled(
                125, 125, Qt.KeepAspectRatio, Qt.SmoothTransformation
            )
        )

    def __adjustText(self):
        """ 根据文本长度决定是否显示省略号 """
        fontMetrics_1 = QFontMetrics(QFont("Microsoft YaHei", 17, 63))
        self.songName = fontMetrics_1.elidedText(self.songName, Qt.ElideRight, 285)
        fontMetrics_2 = QFontMetrics(QFont("Microsoft YaHei", 9))
        self.songerName = fontMetrics_2.elidedText(self.songerName, Qt.ElideRight, 290)

    def __adjustVolumeLabelPos(self):
        """ 调整音量标签的位置 """
        if 10 <= int(self.volumeLabel.text()) <= 99:
            self.volumeLabel.move(32, 140)
        elif 0 <= int(self.volumeLabel.text()) <= 9:
            self.volumeLabel.move(37, 140)
        else:
            self.volumeLabel.move(27, 140)

    def sliderValueChangedSlot(self, value):
        """ 音量改变时调整系统音量并更新标签 """
        self.volumeLabel.setText(str(value))
        self.__adjustVolumeLabelPos()
        self.systemVolume.setVolume(value)
