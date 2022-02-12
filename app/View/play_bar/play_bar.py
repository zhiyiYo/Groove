# coding:utf-8
from common.database.entity import SongInfo
from common.image_process_utils import DominantColor
from common.signal_bus import signalBus
from components.widgets.label import TimeLabel
from components.widgets.menu import PlayBarMoreActionsMenu
from components.widgets.slider import HollowHandleStyle, Slider
from PyQt5.QtCore import (QEasingCurve, QParallelAnimationGroup, QPoint,
                          QPropertyAnimation, Qt, pyqtProperty, pyqtSignal)
from PyQt5.QtGui import QColor, QPalette, QResizeEvent
from PyQt5.QtWidgets import QHBoxLayout, QVBoxLayout, QWidget
from View.play_bar.song_info_card import SongInfoCard

from .play_bar_buttons import (BasicButton, LoopModeButton, PlayButton,
                               RandomPlayButton, VolumeButton)


class PlayBar(QWidget):
    """ 底部播放栏 """

    savePlaylistSig = pyqtSignal()
    colorChanged = pyqtSignal(QColor)

    def __init__(self, songInfo: SongInfo, color: QColor, parent=None):
        super().__init__(parent)
        self.oldWidth = 1280
        self.__color = color
        self.aniGroup = QParallelAnimationGroup(self)
        self.colorAni = QPropertyAnimation(self, b'color', self)

        # 创建小部件
        self.playProgressBar = PlayProgressBar(songInfo.duration, self)
        self.songInfoCard = SongInfoCard(songInfo, self)
        self.centralButtonGroup = CentralButtonGroup(self)
        self.rightWidgetGroup = RightWidgetGroup(self)
        self.moreActionsMenu = PlayBarMoreActionsMenu(self)

        # 初始化小部件
        self.__initWidget()

    def __initWidget(self):
        """ 初始化小部件 """
        self.resize(1312, 115)
        self.setFixedHeight(115)

        # 将动画添加到动画组中
        self.aniGroup.addAnimation(self.colorAni)
        self.aniGroup.addAnimation(self.songInfoCard.albumCoverLabel.ani)

        # 设置背景色
        self.setAutoFillBackground(True)
        self.setColor(self.__color)

        self.__referenceWidgets()
        self.__adjustWidgetPos()
        self.__connectSignalToSlot()

    def __adjustWidgetPos(self):
        """ 调整小部件位置 """
        w = self.width()
        self.playProgressBar.move(
            int(w/2 - self.playProgressBar.width()/2), self.centralButtonGroup.height())
        self.centralButtonGroup.move(
            int(w/2 - self.centralButtonGroup.width()/2), 0)
        self.rightWidgetGroup.move(w - self.rightWidgetGroup.width(), 0)

    def resizeEvent(self, e: QResizeEvent):
        """ 调整歌曲信息卡宽度 """
        dw = self.width() - self.oldWidth

        # 调整进度条的宽度
        pBar = self.playProgressBar
        pBar.resize(pBar.width() + dw//3, pBar.height())

        self.__adjustWidgetPos()
        self.__adjustSongInfoCardWidth()

        self.oldWidth = self.width()

    def __showMoreActionsMenu(self):
        """ 显示更多操作菜单 """
        globalPos = self.rightWidgetGroup.mapToGlobal(
            self.moreActionsButton.pos())
        x = globalPos.x() + self.moreActionsButton.width() + 30
        y = int(globalPos.y() + self.moreActionsButton.height() / 2 - 152 / 2)
        self.moreActionsMenu.exec(QPoint(x, y))

    def __referenceWidgets(self):
        """ 引用小部件及其方法 """
        self.randomPlayButton = self.centralButtonGroup.randomPlayButton
        self.lastSongButton = self.centralButtonGroup.lastSongButton
        self.playButton = self.centralButtonGroup.playButton
        self.nextSongButton = self.centralButtonGroup.nextSongButton
        self.loopModeButton = self.centralButtonGroup.loopModeButton
        self.progressSlider = self.playProgressBar.progressSlider
        self.volumeButton = self.rightWidgetGroup.volumeButton
        self.volumeSlider = self.rightWidgetGroup.volumeSlider
        self.smallPlayModeButton = self.rightWidgetGroup.smallPlayModeButton
        self.moreActionsButton = self.rightWidgetGroup.moreActionsButton
        self.setCurrentTime = self.playProgressBar.setCurrentTime
        self.setTotalTime = self.playProgressBar.setTotalTime

    def updateSongInfoCard(self, songInfo: SongInfo):
        """ 更新歌曲信息卡 """
        self.songInfoCard.updateWindow(songInfo)
        self.__adjustSongInfoCardWidth()

    def __adjustSongInfoCardWidth(self):
        """ 调整歌曲信息卡宽度 """
        card = self.songInfoCard
        card.adjustSize()
        if card.width() >= self.playProgressBar.x() - 20:
            card.setFixedWidth(self.playProgressBar.x() - 20)
            card.textWindow.setMaxWidth(card.width() - 155)

    def setRandomPlay(self, isRandomPlay: bool):
        """ 设置随机播放 """
        self.randomPlayButton.setRandomPlay(isRandomPlay)

    def setMute(self, isMute: bool):
        """ 设置静音 """
        self.volumeButton.setMute(isMute)

    def setVolume(self, volume: int):
        """ 设置音量 """
        if self.volumeSlider.value() == volume:
            return

        self.volumeSlider.setValue(volume)
        self.volumeButton.setVolumeLevel(volume)

    def setPlay(self, isPlay: bool):
        """ 设置播放状态 """
        self.playButton.setPlay(isPlay)

    def __connectSignalToSlot(self):
        """ 信号连接到槽 """
        self.nextSongButton.clicked.connect(signalBus.nextSongSig)
        self.lastSongButton.clicked.connect(signalBus.lastSongSig)
        self.playButton.clicked.connect(signalBus.togglePlayStateSig)
        self.volumeSlider.valueChanged.connect(signalBus.volumeChanged)
        self.progressSlider.clicked.connect(signalBus.progressSliderMoved)
        self.songInfoCard.clicked.connect(signalBus.showPlayingInterfaceSig)
        self.songInfoCard.albumChanged.connect(self.__onAlbumChanged)
        self.moreActionsButton.clicked.connect(self.__showMoreActionsMenu)
        self.progressSlider.sliderMoved.connect(signalBus.progressSliderMoved)
        self.smallPlayModeButton.clicked.connect(
            signalBus.showSmallestPlayInterfaceSig)
        self.moreActionsMenu.fullScreenAct.triggered.connect(
            lambda: signalBus.fullScreenChanged.emit(True))
        self.moreActionsMenu.savePlayListAct.triggered.connect(
            self.savePlaylistSig)
        self.moreActionsMenu.showPlayListAct.triggered.connect(
            signalBus.showPlayingPlaylistSig)
        self.moreActionsMenu.clearPlayListAct.triggered.connect(
            signalBus.clearPlayingPlaylistSig)

    def __onAlbumChanged(self, albumPath: str):
        """ 更新专辑槽函数 """
        r, g, b = DominantColor.getDominantColor(albumPath)
        self.colorChanged.emit(QColor(r, g, b))

        self.colorAni.setStartValue(self.getColor())
        self.colorAni.setEndValue(QColor(r, g, b))
        self.colorAni.setEasingCurve(QEasingCurve.OutCubic)
        self.colorAni.setDuration(200)

        self.songInfoCard.albumCoverLabel.ani.setStartValue(0)
        self.songInfoCard.albumCoverLabel.ani.setEndValue(1)
        self.songInfoCard.albumCoverLabel.ani.setEasingCurve(
            QEasingCurve.OutCubic)
        self.songInfoCard.albumCoverLabel.ani.setDuration(200)

        self.aniGroup.start()

    def setLoopMode(self, loopMode):
        """ 设置循环模式 """
        self.loopModeButton.setLoopMode(loopMode)

    def setColor(self, color: QColor):
        """ 设置背景颜色 """
        self.__color = color
        palette = QPalette()
        palette.setColor(self.backgroundRole(), color)
        self.setPalette(palette)

    def getColor(self):
        return self.__color

    color = pyqtProperty(QColor, getColor, setColor)


class CentralButtonGroup(QWidget):
    """ 播放按钮组 """

    def __init__(self, parent=None):
        super().__init__(parent)

        # 创建按钮
        self.randomPlayButton = RandomPlayButton(self)
        self.lastSongButton = BasicButton(
            ':/images/play_bar/Previous.png', self)
        self.nextSongButton = BasicButton(':/images/play_bar/Next.png', self)
        self.playButton = PlayButton(self)
        self.loopModeButton = LoopModeButton(self)

        # 创建布局
        self.vBoxLayout = QVBoxLayout(self)
        self.__initWidgets()

    def __initWidgets(self):
        """ 初始化界面 """
        self.setFixedSize(317, 67 + 8 + 3)

        hBoxLayout = QHBoxLayout()
        hBoxLayout.setSpacing(0)
        hBoxLayout.setContentsMargins(0, 0, 0, 0)

        buttons = [self.randomPlayButton, self.lastSongButton,
                   self.playButton, self.nextSongButton, self.loopModeButton]

        for i, button in enumerate(buttons):
            hBoxLayout.addWidget(button, 0, Qt.AlignCenter)
            if i != 4:
                hBoxLayout.addSpacing(16)

        self.vBoxLayout.addSpacing(8)
        self.vBoxLayout.setSpacing(0)
        self.vBoxLayout.setContentsMargins(0, 0, 0, 0)
        self.vBoxLayout.addLayout(hBoxLayout)

        # 设置工具提示
        self.lastSongButton.setToolTip(self.tr('Previous'))
        self.nextSongButton.setToolTip(self.tr('Next'))


class RightWidgetGroup(QWidget):
    """ 播放按钮组 """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.hBoxLayout = QHBoxLayout(self)
        self.volumeButton = VolumeButton(self)
        self.volumeSlider = Slider(Qt.Horizontal, self)
        self.smallPlayModeButton = BasicButton(
            ":/images/play_bar/SmallestPlayMode.png", self)
        self.moreActionsButton = BasicButton(
            ":/images/play_bar/More.png", self)

        self.__initWidget()
        self.__initLayout()

    def __initWidget(self):
        """ 初始化小部件 """
        self.setFixedSize(301, 16 + 67)
        self.volumeSlider.setRange(0, 100)
        self.volumeSlider.setStyle(HollowHandleStyle(
            {"sub-page.color": QColor(70, 23, 180)}))
        self.volumeSlider.setFixedHeight(28)
        self.volumeSlider.setValue(20)
        self.smallPlayModeButton.setToolTip(self.tr('Smallest play mode'))
        self.moreActionsButton.setToolTip(self.tr('More actions'))

    def __initLayout(self):
        """ 初始化布局 """
        spacings = [7, 8, 8, 5, 7]
        widgets = [self.volumeButton, self.volumeSlider,
                   self.smallPlayModeButton, self.moreActionsButton]

        self.hBoxLayout.setSpacing(0)
        self.hBoxLayout.setContentsMargins(0, 0, 0, 0)

        # 将小部件添加到布局中
        for i in range(4):
            self.hBoxLayout.addSpacing(spacings[i])
            self.hBoxLayout.addWidget(widgets[i])

        self.hBoxLayout.addSpacing(spacings[-1])


class PlayProgressBar(QWidget):
    """ 歌曲播放进度条 """

    def __init__(self, duration: int, parent=None):
        """
        Parameters
        ----------
        duration: int
            时长，以秒为单位

        parent:
            父级窗口
        """
        super().__init__(parent)
        self.progressSlider = Slider(Qt.Horizontal, self)
        self.currentTimeLabel = TimeLabel(0, self)
        self.totalTimeLabel = TimeLabel(duration or 0, self)
        self.hBoxLayout = QHBoxLayout(self)
        self.__initWidget()

    def __initWidget(self):
        """ 初始化小部件 """
        self.resize(450, 30)

        # 设置样式
        self.setStyleSheet("""
            QLabel {
                color: white;
                font: 15px 'Segoe UI';
                font-weight: 500;
                background-color: transparent;
            }
        """)
        self.progressSlider.setStyle(HollowHandleStyle())
        self.progressSlider.setRange(0, 0)
        self.progressSlider.setFixedHeight(28)

        # 将小部件添加到布局中
        self.hBoxLayout.addWidget(self.currentTimeLabel, 0, Qt.AlignHCenter)
        self.hBoxLayout.addWidget(self.progressSlider, 0, Qt.AlignHCenter)
        self.hBoxLayout.addWidget(self.totalTimeLabel, 0, Qt.AlignHCenter)
        self.hBoxLayout.setContentsMargins(0, 0, 0, 0)
        self.hBoxLayout.setSpacing(10)

    def setCurrentTime(self, currentTime: int):
        """ 更新当前时间标签，单位为毫秒 """
        self.currentTimeLabel.setTime(int(currentTime/1000))

    def setTotalTime(self, totalTime: int):
        """ 更新总时长标签，单位为毫秒 """
        self.totalTimeLabel.setTime(int(totalTime/1000))

    def resizeEvent(self, e):
        """ 改变宽度时调整滑动条的宽度 """
        self.progressSlider.setFixedWidth(self.width() - 100)
        super().resizeEvent(e)
