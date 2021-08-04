# coding:utf-8
from app.components.label import ClickableLabel
from PyQt5.QtCore import (QAbstractAnimation, QEasingCurve, QEvent,
                          QParallelAnimationGroup, QPropertyAnimation, QRect,
                          Qt, pyqtSignal, QSize, QPoint)
from PyQt5.QtGui import QFont, QFontMetrics, QMouseEvent, QIcon, QPixmap
from PyQt5.QtWidgets import QApplication, QLabel, QWidget, QCheckBox, QToolButton

from .menu import AddToMenu


class SongCard(QWidget):
    """ 歌曲卡 """

    clicked = pyqtSignal(int)
    aniStartSig = pyqtSignal()
    checkedStateChanged = pyqtSignal(int, bool)
    switchToAlbumInterfaceSig = pyqtSignal(str, str)
    addSongToNewCustomPlaylistSig = pyqtSignal(dict)  # 添加歌曲到新建的播放列表
    addSongToCustomPlaylistSig = pyqtSignal(str, dict)# 添加歌曲到已存在的播放列表

    def __init__(self, songInfo: dict, parent=None):
        super().__init__(parent=parent)
        self.__getInfo(songInfo)
        self.__resizeTime = 0
        # 初始化标志位
        self.isPlaying = False
        self.isChecked = False
        self.isInSelectionMode = False
        # 处理每个小部件所占的最大宽度
        self.__maxSongNameCardWidth = 420
        self.__maxSongerLabelWidth = 284
        self.__maxAlbumLabelWidth = 284
        # 对应的 item 的下标
        self.itemIndex = None
        # 创建小部件
        self.songNameCard = SongNameCard(self.songName, self)
        self.songerLabel = ClickableLabel(self.songer, self, False)
        self.albumLabel = ClickableLabel(self.album, self, False)
        self.yearLabel = QLabel(self.year, self)
        self.durationLabel = QLabel(self.duration, self)
        self.songNameLabel = self.songNameCard.songNameLabel
        self.buttonGroup = self.songNameCard.buttonGroup
        self.playButton = self.songNameCard.playButton
        self.addToButton = self.songNameCard.addToButton
        self.checkBox = self.songNameCard.checkBox
        self.label_list = [
            self.songNameLabel,
            self.songerLabel,
            self.albumLabel,
            self.yearLabel,
            self.durationLabel
        ]
        # 创建动画
        self.__createAnimations()
        # 初始化
        self.__initWidget()

    def __initWidget(self):
        """ 初始化小部件 """
        self.__getLabelWidth()
        self.resize(1234, 60)
        self.resize(1234, 60)
        self.setFixedHeight(60)
        self.albumLabel.setCursor(Qt.PointingHandCursor)
        self.songerLabel.setCursor(Qt.PointingHandCursor)
        self.setAttribute(Qt.WA_StyledBackground)
        # 分配ID和属性
        self.setObjectName("songCard")
        self.songNameLabel.setObjectName('songNameLabel')
        self.albumLabel.setObjectName("clickableLabel")
        self.songerLabel.setObjectName("clickableLabel")
        self.setState(False, False, False, False)
        # 安装事件过滤器
        self.installEventFilter(self)
        # 信号连接到槽
        self.__connectSignalToSlot()

    def setState(self, isPlay: bool, isEnter: bool, isChecked: bool, isPressed: bool):
        """ 设置窗口和小部件的状态

        Parameters
        ----------
        isPlay: bool
            歌曲卡是否处于播放状态

        isEnter: bool
            鼠标是否进入歌曲卡

        isChecked: bool
            歌曲卡是否被选中，在选择模式下为 `True`

        isPressed: bool
            歌曲卡是否被按下
        """
        playState = 'play' if isPlay else 'notPlay'
        enterState = 'enter' if isEnter else 'leave'
        checkedState = 'checked' if isChecked else 'notChecked'
        bgState = f'{checkedState}-{enterState}' if not isPressed else f'{checkedState}-pressed'
        labelState = f'notChecked-{playState}-{enterState}' if not isChecked else 'checked'
        checkBoxState = f'notChecked-{playState}' if not isChecked else 'checked'
        self.setProperty('state', bgState)
        self.checkBox.setProperty('state', checkBoxState)
        self.songNameCard.playingLabel.setProperty('state', checkedState)
        for label in self.label_list:
            label.setProperty('state', labelState)
        self.setStyle(QApplication.style())

    def __getInfo(self, songInfo: dict):
        """ 从歌曲信息中分离信息 """
        self.songInfo = songInfo
        self.year = songInfo["year"]  # type:str
        self.songer = songInfo["songer"]  # type:str
        self.album = songInfo["album"]  # type:str
        self.duration = songInfo["duration"]  # type:str
        self.songName = songInfo["songName"]  # type:str

    def __createAnimations(self):
        """ 创建动画 """
        self.aniGroup = QParallelAnimationGroup(self)
        self.__deltaX_list = [13, 5, -3, -11, -13]
        self.__aniWidget_list = [
            self.songNameCard,
            self.songerLabel,
            self.albumLabel,
            self.yearLabel,
            self.durationLabel,
        ]
        self.__ani_list = [
            QPropertyAnimation(widget, b"geometry") for widget in self.__aniWidget_list]
        for ani in self.__ani_list:
            ani.setDuration(400)
            ani.setEasingCurve(QEasingCurve.OutQuad)
            self.aniGroup.addAnimation(ani)
        # 记录下移动目标位置
        self.__getAniTargetX_list()

    def __getAniTargetX_list(self):
        """ 计算动画的初始值 """
        self.__aniTargetX_list = []
        for deltaX, widget in zip(self.__deltaX_list, self.__aniWidget_list):
            self.__aniTargetX_list.append(deltaX + widget.x())

    def eventFilter(self, obj, e: QEvent):
        """ 更新样式 """
        if obj is self:
            if e.type() == QEvent.Enter:
                self.checkBox.show()
                self.buttonGroup.setVisible(not self.isInSelectionMode)
                self.setState(self.isPlaying, True, self.isChecked, False)
            elif e.type() == QEvent.Leave:
                self.checkBox.setVisible(self.isInSelectionMode)
                self.buttonGroup.hide()
                self.setState(self.isPlaying, False, self.isChecked, False)
            elif e.type() == QEvent.MouseButtonPress:
                self.setState(self.isPlaying, False, self.isChecked, True)
            elif e.type() == QEvent.MouseButtonRelease:
                self.setState(True, False, self.isChecked, False)
        return super().eventFilter(obj, e)

    def mousePressEvent(self, e):
        """ 鼠标按下时移动小部件 """
        super().mousePressEvent(e)
        # 移动小部件
        if self.aniGroup.state() == QAbstractAnimation.Stopped:
            for deltaX, widget in zip(self.__deltaX_list, self.__aniWidget_list):
                widget.move(widget.x() + deltaX, widget.y())
        else:
            self.aniGroup.stop()
            for targetX, widget in zip(self.__aniTargetX_list, self.__aniWidget_list):
                widget.move(targetX, widget.y())

    def mouseReleaseEvent(self, e: QMouseEvent):
        """ 鼠标松开时开始动画 """
        for ani, widget, deltaX in zip(self.__ani_list, self.__aniWidget_list, self.__deltaX_list):
            ani.setStartValue(
                QRect(widget.x(), widget.y(), widget.width(), widget.height()))
            ani.setEndValue(
                QRect(widget.x() - deltaX, widget.y(), widget.width(), widget.height()))

        self.checkBox.setVisible(self.isInSelectionMode)
        if e.button() == Qt.LeftButton:
            self.aniGroup.finished.connect(self.__onAniFinished)
            if not self.isInSelectionMode:
                self.aniStartSig.emit()  # 发信号给songListWidget要求取消当前歌曲卡的播放状态
                self.setPlay(True)
            else:
                self.setChecked(not self.isChecked)
        self.aniGroup.start()

    def __onAniFinished(self):
        """ 动画完成时更新样式 """
        # 如果不处于选择模式，发出点击信号
        if not self.isInSelectionMode:
            self.clicked.emit(self.itemIndex)
        # 动画完成后需要断开连接，为下一次样式更新做准备
        self.aniGroup.disconnect()

    def resizeEvent(self, e):
        """ 改变窗口大小时移动标签 """
        self.__resizeTime += 1
        if self.__resizeTime == 1:
            self.originalWidth = self.width()
            width = self.width() - 246
            # 计算各个标签所占的最大宽度
            self.__maxSongNameCardWidth = int(42 / 99 * width)
            self.__maxSongerLabelWidth = int(
                (width - self.__maxSongNameCardWidth) / 2)
            self.__maxAlbumLabelWidth = self.__maxSongerLabelWidth
            # 如果实际尺寸大于可分配尺寸，就调整大小
            self.__adjustWidgetWidth()
        elif self.__resizeTime > 1:
            deltaWidth = self.width() - self.originalWidth
            self.originalWidth = self.width()
            # 分配多出来的宽度
            threeEqualWidth = int(deltaWidth / 3)
            self.__maxSongNameCardWidth += threeEqualWidth
            self.__maxSongerLabelWidth += threeEqualWidth
            self.__maxAlbumLabelWidth += deltaWidth - 2 * threeEqualWidth
            self.__adjustWidgetWidth()
        # 移动标签
        self.durationLabel.move(self.width() - 45, 20)
        self.yearLabel.move(self.width() - 190, 20)
        self.songerLabel.move(self.__maxSongNameCardWidth + 26, 20)
        self.albumLabel.move(self.songerLabel.x() +
                             self.__maxSongerLabelWidth + 15, 20)
        # 更新动画目标移动位置
        self.__getAniTargetX_list()

    def __adjustWidgetWidth(self):
        """ 调整小部件宽度 """
        self.songNameCard.resize(self.__maxSongNameCardWidth, 60)
        if self.songerWidth > self.__maxSongerLabelWidth:
            self.songerLabel.setFixedWidth(self.__maxSongerLabelWidth)
        else:
            self.songerLabel.setFixedWidth(self.songerWidth)
        if self.albumWidth > self.__maxAlbumLabelWidth:
            self.albumLabel.setFixedWidth(self.__maxAlbumLabelWidth)
        else:
            self.albumLabel.setFixedWidth(self.albumWidth)

    def __getLabelWidth(self):
        """ 计算标签的长度 """
        fontMetrics = QFontMetrics(QFont("Microsoft YaHei", 9))
        self.songerWidth = fontMetrics.width(self.songInfo["songer"])
        self.albumWidth = fontMetrics.width(self.songInfo["album"])

    def updateSongCard(self, songInfo: dict):
        """ 更新歌曲卡信息 """
        self.resize(self.size())
        self.__getInfo(songInfo)
        self.songNameCard.setSongName(songInfo["songName"])
        self.songerLabel.setText(songInfo["songer"])
        self.albumLabel.setText(songInfo["album"])
        self.yearLabel.setText(songInfo["year"])
        self.durationLabel.setText(songInfo["duration"])
        # 调整宽度
        self.__getLabelWidth()
        songerWidth = (
            self.songerWidth
            if self.songerWidth <= self.__maxSongerLabelWidth
            else self.__maxSongerLabelWidth
        )
        albumWidth = (
            self.albumWidth
            if self.albumWidth <= self.__maxAlbumLabelWidth
            else self.__maxAlbumLabelWidth
        )
        self.songerLabel.setFixedWidth(songerWidth)
        self.albumLabel.setFixedWidth(albumWidth)

    def setPlay(self, isPlay: bool):
        """ 设置歌曲卡播放状态 """
        if self.isPlaying == isPlay:
            return
        self.isPlaying = isPlay
        self.songNameCard.setPlay(isPlay)
        self.setState(isPlay, False, self.isChecked, False)

    def setChecked(self, isChecked: bool):
        """ 设置复选状态 """
        self.checkBox.setChecked(isChecked)

    def onCheckedStateChanged(self):
        """ 复选框选中状态改变槽函数 """
        self.isChecked = self.checkBox.isChecked()
        self.setState(self.isPlaying, False, self.isChecked, False)
        # 只要点击了复选框就进入选择模式，由父级控制退出选择模式
        self.checkBox.show()
        self.setSelectionModeOpen(True)
        self.checkedStateChanged.emit(self.itemIndex, self.isChecked)

    def setSelectionModeOpen(self, isOpenSelectionMode: bool):
        """ 设置是否进入选择模式，选择模式下复选框一直可见，按钮不可见 """
        if self.isInSelectionMode == isOpenSelectionMode:
            return
        self.isInSelectionMode = isOpenSelectionMode
        self.checkBox.setVisible(isOpenSelectionMode)
        self.buttonGroup.setHidden(True)

    def __showAddToMenu(self):
        """ 显示添加到菜单 """
        menu = AddToMenu(parent=self)
        pos = self.mapToGlobal(
            QPoint(self.addToButton.x()+self.buttonGroup.x(), 0))
        x = pos.x()+self.addToButton.width()+5
        y = pos.y()+self.addToButton.height()//2-(13+38*menu.actionCount()//2)
        menu.newPlaylist.triggered.connect(
            lambda: self.addSongToNewCustomPlaylistSig.emit(self.songInfo))
        menu.addSongsToPlaylistSig.connect(
            lambda name: self.addSongToCustomPlaylistSig.emit(name, self.songInfo))
        menu.exec_(QPoint(x, y))

    def __connectSignalToSlot(self):
        """ 信号连接到槽 """
        self.playButton.clicked.connect(
            lambda: self.clicked.emit(self.itemIndex))
        self.albumLabel.clicked.connect(
            lambda: self.switchToAlbumInterfaceSig.emit(
                self.albumLabel.text(), self.songerLabel.text()))
        self.checkBox.stateChanged.connect(self.onCheckedStateChanged)
        self.addToButton.clicked.connect(self.__showAddToMenu)


class ToolButton(QToolButton):
    """ 工具按钮 """

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
                r"app\resource\images\playing_interface\Play_60_60.png",
                r"app\resource\images\playing_interface\Play_green_60_60.png",
            ],
            self,
        )
        self.addToButton = ToolButton(
            [
                r"app\resource\images\playing_interface\Add.png",
                r"app\resource\images\playing_interface\Add_green.png",
            ],
            self,
        )
        # 初始化
        self.setAttribute(Qt.WA_StyledBackground)
        self.setFixedSize(140, 60)
        # 设置按钮的绝对坐标
        self.addToButton.move(80, 0)
        self.playButton.move(20, 0)

    def setPlay(self, isPlay: bool):
        """ 根据播放状态更换按钮图标 """
        self.playButton.setPlay(isPlay)
        self.addToButton.setPlay(isPlay)


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
            QPixmap(r"app\resource\images\playing_interface\正在播放_green_16_16.png"))
        self.playingLabel.setObjectName('playingLabel')
        # 隐藏小部件
        self.checkBox.hide()
        self.buttonGroup.hide()
        self.playingLabel.hide()
        # 计算歌名的长度
        self.__getSongNameWidth()
        self.__initLayout()

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

    def setPlay(self, isPlay: bool):
        """ 设置播放状态并移动小部件 """
        self.buttonGroup.setPlay(isPlay)
        # 显示/隐藏正在播放图标并根据情况移动歌名标签
        self.playingLabel.setHidden(not isPlay)
        self.songNameLabel.move(68 if isPlay else 41, self.songNameLabel.y())
        # 更新按钮位置
        self.__moveButtonGroup()

    def resizeEvent(self, e):
        """ 改变尺寸时移动按钮 """
        super().resizeEvent(e)
        self.__moveButtonGroup()

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
