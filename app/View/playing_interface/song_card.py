# coding:utf-8
from common.database.entity import SongInfo
from components.buttons.tooltip_button import TooltipButton
from components.widgets.label import ClickableLabel
from PyQt5.QtCore import (QAbstractAnimation, QEasingCurve, QEvent,
                          QParallelAnimationGroup, QPoint, QPropertyAnimation,
                          QRect, QSize, Qt, pyqtSignal)
from PyQt5.QtGui import QFont, QFontMetrics, QIcon, QMouseEvent, QPixmap
from PyQt5.QtWidgets import (QApplication, QCheckBox, QLabel, QToolButton,
                             QWidget)

from .menu import AddToMenu


class SongCard(QWidget):
    """ 歌曲卡 """

    clicked = pyqtSignal(int)                               # 歌曲卡点击
    aniStartSig = pyqtSignal()                              # 反弹动画开始
    checkedStateChanged = pyqtSignal(int, bool)             # 歌曲卡选中状态改变
    switchToSingerInterfaceSig = pyqtSignal(str)            # 切换到歌手界面
    switchToAlbumInterfaceSig = pyqtSignal(str, str)        # 切换到专辑界面
    addSongToNewCustomPlaylistSig = pyqtSignal(SongInfo)    # 添加歌曲到新建的播放列表
    addSongToCustomPlaylistSig = pyqtSignal(str, SongInfo)  # 添加歌曲到已存在的播放列表

    def __init__(self, songInfo: SongInfo, parent=None):
        super().__init__(parent=parent)
        self.__getInfo(songInfo)
        self.__resizeTime = 0
        # 初始化标志位
        self.isPlaying = False
        self.isChecked = False
        self.isInSelectionMode = False

        # 处理每个小部件所占的最大宽度
        self.__maxSongNameCardWidth = 420
        self.__maxSingerWidth = 284
        self.__maxAlbumWidth = 284

        # 对应的 item 的下标
        self.itemIndex = None

        # 创建小部件
        self.songNameCard = SongNameCard(self.songName, self)
        self.singerLabel = ClickableLabel(self.singer, self, False)
        self.albumLabel = ClickableLabel(self.album, self, False)
        self.yearLabel = QLabel(self.year, self)
        self.durationLabel = QLabel(self.duration, self)
        self.songNameLabel = self.songNameCard.songNameLabel
        self.buttonGroup = self.songNameCard.buttonGroup
        self.playButton = self.songNameCard.playButton
        self.addToButton = self.songNameCard.addToButton
        self.checkBox = self.songNameCard.checkBox
        self.labels = [
            self.songNameLabel, self.singerLabel,
            self.albumLabel, self.yearLabel, self.durationLabel
        ]
        self.__createAnimations()
        self.__initWidget()

    def __initWidget(self):
        """ 初始化小部件 """
        self.__getLabelWidth()
        self.resize(1234, 60)
        self.resize(1234, 60)
        self.setFixedHeight(60)
        self.albumLabel.setCursor(Qt.PointingHandCursor)
        self.singerLabel.setCursor(Qt.PointingHandCursor)
        self.setAttribute(Qt.WA_StyledBackground)

        # 分配ID和属性
        self.setObjectName("songCard")
        self.songNameLabel.setObjectName('songNameLabel')
        self.albumLabel.setObjectName("clickableLabel")
        self.singerLabel.setObjectName("clickableLabel")
        self.setState(False, False, False, False)

        # 安装事件过滤器
        self.installEventFilter(self)
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
        self.buttonGroup.setProperty('state', bgState)
        self.checkBox.setProperty('state', checkBoxState)
        self.songNameCard.playingLabel.setProperty('state', checkedState)

        for label in self.labels:
            label.setProperty('state', labelState)

        self.setStyle(QApplication.style())

    def __getInfo(self, songInfo: SongInfo):
        """ 从歌曲信息中分离信息 """
        self.songInfo = songInfo
        self.songName = songInfo.title
        self.singer = songInfo.singer
        self.album = songInfo.album
        self.year = str(songInfo.year or '')
        self.duration = f"{int(songInfo.duration//60)}:{int(songInfo.duration%60):02}"

    def __createAnimations(self):
        """ 创建动画 """
        self.aniGroup = QParallelAnimationGroup(self)
        self.__deltaXs = [13, 5, -3, -11, -13]
        self.__aniWidgets = [
            self.songNameCard, self.singerLabel, self.albumLabel,
            self.yearLabel, self.durationLabel,
        ]
        self.__anis = [
            QPropertyAnimation(w, b"pos") for w in self.__aniWidgets]

        for ani in self.__anis:
            ani.setDuration(400)
            ani.setEasingCurve(QEasingCurve.OutQuad)
            self.aniGroup.addAnimation(ani)

        # 记录下移动目标位置
        self.__getAniTargetXs()

    def __getAniTargetXs(self):
        """ 计算动画的初始值 """
        self.__aniTargetXs = []
        for deltaX, widget in zip(self.__deltaXs, self.__aniWidgets):
            self.__aniTargetXs.append(deltaX + widget.x())

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
            for dx, w in zip(self.__deltaXs, self.__aniWidgets):
                w.move(w.x() + dx, w.y())
        else:
            self.aniGroup.stop()
            for x, w in zip(self.__aniTargetXs, self.__aniWidgets):
                w.move(x, w.y())

    def mouseReleaseEvent(self, e: QMouseEvent):
        """ 鼠标松开时开始动画 """
        for ani, w, dx in zip(self.__anis, self.__aniWidgets, self.__deltaXs):
            ani.setStartValue(w.pos())
            ani.setEndValue(QPoint(w.x() - dx, w.y()))

        self.checkBox.setVisible(self.isInSelectionMode)

        if e.button() == Qt.LeftButton:
            if not self.isInSelectionMode:
                self.aniGroup.finished.connect(self.__onAniFinished)
                self.aniStartSig.emit()  # 发信号给songListWidget要求取消当前歌曲卡的播放状态
                self.setPlay(True)
            else:
                self.setChecked(not self.isChecked)

        self.aniGroup.start()

    def __onAniFinished(self):
        """ 动画完成时更新样式 """
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
            self.__maxSingerWidth = int(
                (width - self.__maxSongNameCardWidth) / 2)
            self.__maxAlbumWidth = self.__maxSingerWidth

            # 如果实际尺寸大于可分配尺寸，就调整大小
            self.__adjustWidgetWidth()

        elif self.__resizeTime > 1:
            deltaWidth = self.width() - self.originalWidth
            self.originalWidth = self.width()

            # 分配多出来的宽度
            threeEqualWidth = int(deltaWidth / 3)
            self.__maxSongNameCardWidth += threeEqualWidth
            self.__maxSingerWidth += threeEqualWidth
            self.__maxAlbumWidth += deltaWidth - 2 * threeEqualWidth
            self.__adjustWidgetWidth()

        # 移动标签
        self.durationLabel.move(self.width() - 45, 20)
        self.yearLabel.move(self.width() - 190, 20)
        self.singerLabel.move(self.__maxSongNameCardWidth + 26, 20)
        self.albumLabel.move(self.singerLabel.x() +
                             self.__maxSingerWidth + 15, 20)
        # 更新动画目标移动位置
        self.__getAniTargetXs()

    def __adjustWidgetWidth(self):
        """ 调整小部件宽度 """
        self.songNameCard.resize(self.__maxSongNameCardWidth, 60)
        self.singerLabel.setFixedWidth(
            min(self.singerWidth, self.__maxSingerWidth))
        self.albumLabel.setFixedWidth(
            min(self.albumWidth, self.__maxAlbumWidth))

    def __getLabelWidth(self):
        """ 计算标签的长度 """
        fontMetrics = QFontMetrics(QFont("Microsoft YaHei", 9))
        self.singerWidth = fontMetrics.width(self.singer)
        self.albumWidth = fontMetrics.width(self.album)

    def updateSongCard(self, songInfo: SongInfo):
        """ 更新歌曲卡信息 """
        self.resize(self.size())
        self.__getInfo(songInfo)
        self.songNameCard.setSongName(self.songName)
        self.singerLabel.setText(self.singer)
        self.albumLabel.setText(self.album)
        self.yearLabel.setText(self.year)
        self.durationLabel.setText(self.duration)
        # 调整宽度
        self.__getLabelWidth()
        self.__adjustWidgetWidth()

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

    def setSelectionModeOpen(self, isOpen: bool):
        """ 设置是否进入选择模式，选择模式下复选框一直可见，按钮不可见 """
        if self.isInSelectionMode == isOpen:
            return

        self.isInSelectionMode = isOpen
        self.checkBox.setVisible(isOpen)
        self.buttonGroup.setHidden(True)

    def __showAddToMenu(self):
        """ 显示添加到菜单 """
        menu = AddToMenu(parent=self)
        pos = self.mapToGlobal(
            QPoint(self.addToButton.x()+self.buttonGroup.x(), 0))
        x = pos.x()+self.addToButton.width()+5
        y = pos.y()+self.addToButton.height()//2-(13+38*menu.actionCount()//2)

        menu.newPlaylistAct.triggered.connect(
            lambda: self.addSongToNewCustomPlaylistSig.emit(self.songInfo))
        menu.addSongsToPlaylistSig.connect(
            lambda name: self.addSongToCustomPlaylistSig.emit(name, self.songInfo))
        menu.exec_(QPoint(x, y))

    def __connectSignalToSlot(self):
        """ 信号连接到槽 """
        self.playButton.clicked.connect(
            lambda: self.clicked.emit(self.itemIndex))
        self.singerLabel.clicked.connect(
            lambda: self.switchToSingerInterfaceSig.emit(self.singer))
        self.albumLabel.clicked.connect(
            lambda: self.switchToAlbumInterfaceSig.emit(self.album, self.singer))
        self.checkBox.stateChanged.connect(self.onCheckedStateChanged)
        self.addToButton.clicked.connect(self.__showAddToMenu)


class ToolButton(QToolButton):
    """ 工具按钮 """

    def __init__(self, iconPaths: dict, parent=None):
        super().__init__(parent)
        self.iconPaths = iconPaths
        self.isPlaying = False
        self.setFixedSize(60, 60)
        self.setIconSize(QSize(60, 60))
        self.setIcon(QIcon(self.iconPaths[self.isPlaying]))
        self.setStyleSheet("QToolButton{border:none;margin:0}")
        # self.setDarkToolTip(True)

    def setPlay(self, isPlay: bool):
        """ 设置播放状态，更新按钮图标 """
        self.isPlaying = isPlay
        self.setIcon(QIcon(self.iconPaths[self.isPlaying]))


class ButtonGroup(QWidget):
    """ 按钮组 """

    def __init__(self, parent=None):
        super().__init__(parent)
        # 创建按钮
        self.playButton = ToolButton(
            [
                ":/images/playing_interface/Play_60_60.png",
                ":/images/playing_interface/Play_green_60_60.png",
            ],
            self,
        )
        self.addToButton = ToolButton(
            [
                ":/images/playing_interface/Add.png",
                ":/images/playing_interface/Add_green.png",
            ],
            self,
        )
        self.setAttribute(Qt.WA_StyledBackground)
        self.setFixedSize(140, 60)

        self.addToButton.move(80, 0)
        self.playButton.move(20, 0)
        # self.addToButton.setToolTip(self.tr('Add to'))
        # self.playButton.setToolTip(self.tr('Play'))

    def setPlay(self, isPlay: bool):
        """ 根据播放状态更换按钮图标 """
        self.playButton.setPlay(isPlay)
        self.addToButton.setPlay(isPlay)


class SongNameCard(QWidget):
    """ 歌名卡 """

    def __init__(self, songName: str, parent=None):
        super().__init__(parent)
        self.songName = songName
        self.checkBox = QCheckBox(self)
        self.playingLabel = QLabel(self)
        self.songNameLabel = QLabel(songName, self)
        self.buttonGroup = ButtonGroup(self)
        self.playButton = self.buttonGroup.playButton
        self.addToButton = self.buttonGroup.addToButton
        self.__initWidget()

    def __initWidget(self):
        """ 初始化小部件 """
        self.setFixedHeight(60)
        self.resize(390, 60)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.playingLabel.setPixmap(
            QPixmap(":/images/playing_interface/Playing_green.png"))
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
        self.songNameWidth = fontMetrics.width(self.songName)

    def setPlay(self, isPlay: bool):
        """ 设置播放状态并移动小部件 """
        self.buttonGroup.setPlay(isPlay)
        self.playingLabel.setHidden(not isPlay)
        self.songNameLabel.move(68 if isPlay else 41, self.songNameLabel.y())
        self.__moveButtonGroup()

    def resizeEvent(self, e):
        """ 改变尺寸时移动按钮 """
        super().resizeEvent(e)
        self.__moveButtonGroup()

    def __moveButtonGroup(self):
        """ 移动按钮组 """
        if self.songNameWidth+self.songNameLabel.x() >= self.width()-140:
            x = self.width() - 140
        else:
            x = self.songNameWidth + self.songNameLabel.x()

        self.buttonGroup.move(x, 0)

    def setSongName(self, songName: str):
        """ 更新歌手名标签的文本并调整宽度 """
        self.songName = songName
        self.songNameLabel.setText(songName)
        self.__getSongNameWidth()
        self.__moveButtonGroup()
        self.songNameLabel.setFixedWidth(self.songNameWidth)
