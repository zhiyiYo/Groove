# coding:utf-8
from PyQt5.QtCore import QSize, Qt, QEvent
from PyQt5.QtGui import QFont, QFontMetrics, QIcon, QPixmap
from PyQt5.QtWidgets import QCheckBox, QLabel, QToolButton, QWidget, QApplication


class ToolButton(QToolButton):
    """ 按钮 """

    def __init__(self, iconPath_dict: dict, parent=None):
        super().__init__(parent)
        self.iconPath_dict = iconPath_dict
        # 设置按钮状态标志位
        self.setFixedSize(60, 60)
        self.setIconSize(QSize(60, 60))
        self.setState("notSelected-notPlay")
        self.setStyleSheet("QToolButton{border:none;margin:0}")

    def setState(self, state: str):
        """ 设置按钮状态，更新按钮图标，状态有 notSelected-notPlay、notSelected-play、selected 这三种 """
        self.state = state
        self.setIcon(QIcon(self.iconPath_dict[state]))
        self.setProperty("state", state)

    def setIconPathDict(self, iconPath_dict: dict):
        """ 设置图标路径字典 """
        self.iconPath_dict = iconPath_dict
        self.setIcon(QIcon(iconPath_dict[self.state]))


class ButtonGroup(QWidget):
    """
    按钮组, 按钮窗口的state有6种状态:
        notSelected-leave、notSelected-enter、notSelected-pressed
        selected-leave、selected-enter、selected-pressed
    """

    def __init__(self, parent=None):
        super().__init__(parent)
        # 创建按钮
        self.playButton = ToolButton(
            {
                "notSelected-notPlay": r"app\resource\images\song_tab_interface\Play_black.png",
                "notSelected-play": r"app\resource\images\song_tab_interface\Play_green.png",
                "selected": r"app\resource\images\song_tab_interface\Play_white.png",
            },
            self,
        )
        self.addToButton = ToolButton(
            {
                "notSelected-notPlay": r"app\resource\images\song_tab_interface\Add_black.png",
                "notSelected-play": r"app\resource\images\song_tab_interface\Add_green.png",
                "selected": r"app\resource\images\song_tab_interface\Add_white.png",
            },
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
        # 分配ID并设置属性
        self.setObjectName("buttonGroup")
        self.setProperty("state", "notSelected-leave")
        # 隐藏按钮
        # self.setButtonHidden(True)
        self.installEventFilter(self)

    def setButtonHidden(self, isHidden: bool):
        """ 设置按钮是否可见 """
        self.playButton.setHidden(isHidden)
        self.addToButton.setHidden(isHidden)

    def setButtonState(self, state: str):
        """ 根据状态更换按钮图标, 状态有notSelected-notPlay、notSelected-play、selected这三种 """
        self.playButton.setState(state)
        self.addToButton.setState(state)

    def setState(self, state: str):
        """ 设置按钮组状态 """
        self.setProperty("state", state)

    def eventFilter(self, obj, e: QEvent):
        """ 过滤事件 """
        if obj == self:
            if e.type() == QEvent.Hide:
                # 隐藏按钮组时强行取消按钮的hover状态
                e = QEvent(QEvent.Leave)
                QApplication.sendEvent(self.playButton, e)
                QApplication.sendEvent(self.addToButton, e)
        return super().eventFilter(obj, e)


class SongNameCard(QWidget):
    """ 歌名卡 """

    def __init__(self, songName, parent=None):
        super().__init__(parent)
        self.songName = songName
        self.isPlay = False
        # 创建小部件
        self.checkBox = QCheckBox(self)  # type:QCheckBox
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
        # 隐藏小部件
        self.playingLabel.hide()
        self.setWidgetHidden(True)
        # 分配属性和ID
        self.setObjectName("songNameCard")
        self.songNameLabel.setObjectName("songNameLabel")
        # 计算歌名的长度
        self.__getSongNameWidth()
        self.__initLayout()

    def __initLayout(self):
        """ 初始化布局 """
        self.checkBox.move(15, 18)
        self.playingLabel.move(57, 22)
        self.songNameLabel.move(57, 18)
        self.__moveButtonGroup()

    def __getSongNameWidth(self):
        """ 计算歌名的长度 """
        fontMetrics = QFontMetrics(QFont("Microsoft YaHei", 10))
        self.songNameWidth = sum([fontMetrics.width(i) for i in self.songName])

    def __moveButtonGroup(self):
        """ 移动按钮组 """
        if self.songNameWidth + self.songNameLabel.x() >= self.width() - 140:
            x = self.width() - 140
        else:
            x = self.songNameWidth + self.songNameLabel.x()
        self.buttonGroup.move(x, 0)

    def updateSongNameCard(self, songName: str):
        """ 更新歌手名标签的文本并调整宽度 """
        self.songName = songName
        self.songNameLabel.setText(songName)
        # 重新计算歌名宽度并移动按钮
        self.__getSongNameWidth()
        self.__moveButtonGroup()
        self.songNameLabel.setFixedWidth(self.songNameWidth)

    def setWidgetHidden(self, isHidden: bool):
        """ 显示/隐藏小部件 """
        self.buttonGroup.setHidden(isHidden)
        self.checkBox.setHidden(isHidden)

    def resizeEvent(self, e):
        """ 改变尺寸时移动按钮 """
        super().resizeEvent(e)
        self.__moveButtonGroup()

    def setCheckBoxBtLabelState(self, state: str, isSongExit=True):
        """ 设置复选框、按钮和标签的状态并更新样式

        Parameters
        ----------
        state: str
            有 `notSelected-notPlay`、`notSelected-play`、`selected` 3种状态

        isSongExist: bool
            歌曲是否存在，默认为 True，当 False 时会出现报警图标
        """
        self.checkBox.setProperty("state", state)
        self.songNameLabel.setProperty("state", state)
        self.buttonGroup.setButtonState(state)
        # 根据选中状态和歌曲状态选择图标
        if isSongExit:
            color = "白" if state == "selected" else "绿"
            path = f"app/resource/images/song_tab_interface/{color}色正在播放_16_16.png"
        else:
            color = "white" if state == "selected" else "red"
            path = f"app/resource/images/song_tab_interface/Info_{color}.png"
        self.playingLabel.setPixmap(QPixmap(path))

    def setButtonGroupState(self, state: str):
        """ 设置按钮组窗口状态，按钮组状态与歌曲卡始终相同，总共6种状态 """
        self.buttonGroup.setState(state)

    def setPlay(self, isPlay: bool, isSongExist: bool = True):
        """ 设置播放状态并决定是否显示正在播放图标 """
        self.isPlay = isPlay
        self.playingLabel.setVisible(isPlay or (not isSongExist))
        self.setWidgetHidden(not isPlay)
        # 歌曲不存在时仍需显示图标
        self.songNameLabel.move(
            [57, 83][isPlay or (not isSongExist)], self.songNameLabel.y())
        # 更新按钮位置
        self.__moveButtonGroup()

    def setSongName(self, songName: str):
        """ 更新歌手名标签的文本并调整宽度 """
        self.songName = songName
        self.songNameLabel.setText(songName)
        # 重新计算歌名宽度并移动按钮
        self.__getSongNameWidth()
        self.__moveButtonGroup()
        self.songNameLabel.setFixedWidth(self.songNameWidth)


class TrackNumSongNameCard(SongNameCard):
    """ 带曲目序号的歌曲卡 """

    def __init__(self, songName: str, trackNum: str, parent=None):
        super().__init__(songName, parent)
        # 创建曲目序号标签
        self.trackNumLabel = QLabel(self)
        self.setTrackNum(trackNum)
        # 初始化
        self.__initWidget()

    def __initWidget(self):
        """ 初始化 """
        self.__adjustTrackNumLabelPos()
        self.trackNumLabel.setFixedWidth(25)
        self.trackNumLabel.setObjectName("songNameLabel")
        # 安装事件过滤器
        self.checkBox.installEventFilter(self)

    def setCheckBoxBtLabelState(self, state: str, isSongExist=True):
        """ 设置复选框、按钮和标签的状态并更新样式,有notSelected-notPlay、notSelected-play、selected这3种状态 """
        super().setCheckBoxBtLabelState(state, isSongExist)
        self.trackNumLabel.setProperty("state", state)

    def updateSongNameCard(self, songName, trackNum: str):
        """ 设置卡片的信息 """
        super().updateSongNameCard(songName)
        self.setTrackNum(trackNum)
        self.__adjustTrackNumLabelPos()

    def setTrackNum(self, trackNum: str):
        """ 设置曲目序号 """
        self.trackNum = trackNum
        # 如果是M4a需要转化一下
        if not trackNum[0].isnumeric():
            self.trackNum = str(eval(trackNum)[0])
        self.trackNumLabel.setText(self.trackNum + ".")
        if self.trackNum == "0":
            self.trackNumLabel.setText("")

    def setWidgetsHidden(self, isHidden: bool):
        """ 显示/隐藏小部件 """
        self.trackNumLabel.setHidden(not isHidden)
        super().setWidgetHidden(isHidden)

    def __adjustTrackNumLabelPos(self):
        """ 调整曲目序号标签位置 """
        if len(self.trackNum) >= 2:
            self.trackNumLabel.move(19, 18)
        else:
            self.trackNumLabel.move(28, 18)

    def setPlay(self, isPlay, isSongExist=True):
        """ 设置播放状态 """
        super().setPlay(isPlay, isSongExist)
        self.trackNumLabel.setHidden(isPlay)

    def eventFilter(self, obj, e: QEvent):
        """ 过滤事件 """
        if obj == self.checkBox:
            if e.type() == QEvent.Show:
                self.trackNumLabel.hide()
                return False
            elif e.type() == QEvent.Hide:
                self.trackNumLabel.show()
                return False
        return super().eventFilter(obj, e)


class PlaylistSongNameCard(SongNameCard):
    """ 播放列表界面歌曲名字卡 """

    def __init__(self, songName, parent):
        super().__init__(songName, parent=parent)
        self.addToButton.setIconPathDict({
            "notSelected-notPlay": r"app\resource\images\playlist_interface\Delete_black.png",
            "notSelected-play": r"app\resource\images\playlist_interface\Delete_green.png",
            "selected": r"app\resource\images\playlist_interface\Delete_white.png",
        })
