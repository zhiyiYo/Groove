# coding:utf-8

from PyQt5.QtCore import QSize, Qt
from PyQt5.QtGui import QFont, QFontMetrics, QIcon, QPixmap
from PyQt5.QtWidgets import QApplication, QCheckBox, QLabel, QToolButton, QWidget


class ToolButton(QToolButton):
    """ 按钮 """

    def __init__(self, iconPath_list, parent=None):
        super().__init__(parent)
        self.iconPath_list = iconPath_list
        # 设置正在播放标志位
        self.isPlaying = False
        self.setFixedSize(60, 60)
        self.setIconSize(QSize(60, 60))
        self.setIcon(QIcon(self.iconPath_list[self.isPlaying]))
        self.setStyleSheet("QToolButton{border:none;margin:0}")

    def setPlay(self, isPlay: bool):
        """ 设置播放状态，更新按钮图标 """
        self.isPlaying = isPlay
        self.setIcon(QIcon(self.iconPath_list[self.isPlaying]))


class ButtonGroup(QWidget):
    """ 按钮组 """

    def __init__(self, parent=None):
        super().__init__(parent)
        # 创建按钮
        self.playButton = ToolButton(
            [
                r"app\resource\images\playing_interface\播放按钮_white_60_60.png",
                r"app\resource\images\playing_interface\播放按钮_green_60_60.png",
            ],
            self,
        )
        self.addToButton = ToolButton(
            [
                r"app\resource\images\playing_interface\添加到按钮_white_60_60.png",
                r"app\resource\images\playing_interface\添加到按钮_green_60_60.png",
            ],
            self,
        )
        # 初始化
        self.__initWidget()

    def __initWidget(self):
        """ 初始化小部件 """
        self.setAttribute(Qt.WA_StyledBackground)
        self.setFixedSize(140, 60)
        # 设置按钮的绝对坐标
        self.addToButton.move(80, 0)
        self.playButton.move(20, 0)
        # 分配ID
        self.setObjectName("buttonGroup")
        # 按钮窗口的state有3种状态:
        # leave,hover,pressed
        self.setProperty("state", "leave")
        # 隐藏按钮
        self.playButton.hide()
        self.addToButton.hide()

    def setPlay(self, isPlay: bool):
        """ 根据播放状态更换按钮图标 """
        self.playButton.setPlay(isPlay)
        self.addToButton.setPlay(isPlay)

    def setButtonHidden(self, isHidden: bool):
        """ 设置按钮是否可见 """
        self.playButton.setHidden(isHidden)
        self.addToButton.setHidden(isHidden)


class SongNameCard(QWidget):
    """ 歌名卡 """

    def __init__(self, songName, parent=None):
        super().__init__(parent)
        self.songName = songName
        # 创建小部件
        self.checkBox = QCheckBox(self)
        self.playingLabel = QLabel(self)
        self.songNameLabel = QLabel(songName, self)
        self.buttonGroup = ButtonGroup(self)
        self.playButton = self.buttonGroup.playButton
        self.addToButton = self.buttonGroup.addToButton
        # 初始化
        self.__initWidget()

    def __initWidget(self):
        """ 初始化小部件 """
        self.setFixedHeight(60)
        self.resize(390, 60)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.playingLabel.setPixmap(
            QPixmap(r"app\resource\images\playing_interface\正在播放_16_16.png")
        )
        # 隐藏小部件
        self.checkBox.hide()
        self.playingLabel.hide()
        # 分配属性和ID
        self.setObjectName("songNameCard")
        self.songNameLabel.setObjectName("songNameLabel")
        self.checkBox.setProperty("isPlay", "False")
        self.songNameLabel.setProperty("isPlay", "False")
        # 计算歌名的长度
        self.__getSongNameWidth()
        self.__initLayout()
        # self.__setQss()

    def __initLayout(self):
        """ 初始化布局 """
        self.checkBox.move(8, 17)
        self.playingLabel.move(43, 22)
        self.songNameLabel.move(41, 20)
        self.__moveButtonGroup()

    def __getSongNameWidth(self):
        """ 计算歌名的长度 """
        fontMetrics = QFontMetrics(QFont("Microsoft YaHei", 9))
        self.songNameWidth = sum([fontMetrics.width(i) for i in self.songName])

    def __setQss(self):
        """ 初始化样式 """
        with open(r"app\resource\css\playInterfaceSongCard.qss", encoding="utf-8") as f:
            self.setStyleSheet(f.read())

    def setPlay(self, isPlay: bool):
        """ 设置播放状态并移动小部件 """
        self.buttonGroup.setPlay(isPlay)
        self.checkBox.setProperty("isPlay", str(isPlay))
        self.songNameLabel.setProperty("isPlay", str(isPlay))
        # 显示/隐藏正在播放图标并根据情况移动歌名标签
        self.playingLabel.setHidden(not isPlay)
        if isPlay:
            self.songNameLabel.move(68, self.songNameLabel.y())
        else:
            self.songNameLabel.move(41, self.songNameLabel.y())
        # 更新按钮位置
        self.__moveButtonGroup()
        # 更新样式
        self.setStyle(QApplication.style())

    def resizeEvent(self, e):
        """ 改变尺寸时移动按钮 """
        super().resizeEvent(e)
        self.__moveButtonGroup()

    def setWidgetHidden(self, isHidden: bool):
        """ 显示/隐藏小部件 """
        self.buttonGroup.setButtonHidden(isHidden)
        self.checkBox.setHidden(isHidden)

    def __moveButtonGroup(self):
        """ 移动按钮组 """
        if self.songNameWidth + self.songNameLabel.x() >= self.width() - 140:
            x = self.width() - 140
        else:
            x = self.songNameWidth + self.songNameLabel.x()
        self.buttonGroup.move(x, 0)

    def setSongName(self, songName: str):
        """ 更新歌手名标签的文本并调整宽度 """
        self.songName = songName
        self.songNameLabel.setText(songName)
        # 重新计算歌名宽度并移动按钮
        self.__getSongNameWidth()
        self.__moveButtonGroup()
        self.songNameLabel.setFixedWidth(self.songNameWidth)
