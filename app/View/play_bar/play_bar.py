# coding:utf-8
from app.common.image_process_utils import DominantColor
from app.View.play_bar.central_button_group import CentralButtonGroup
from app.View.play_bar.more_actions_menu import MoreActionsMenu
from app.View.play_bar.play_progress_bar import PlayProgressBar
from app.View.play_bar.right_widget_group import RightWidgetGroup
from app.View.play_bar.song_info_card import SongInfoCard
from PyQt5.QtCore import QPoint, Qt, pyqtSignal, QPropertyAnimation, QEasingCurve, pyqtProperty
from PyQt5.QtGui import QColor, QPalette
from PyQt5.QtMultimedia import QMediaPlaylist
from PyQt5.QtWidgets import QWidget


class PlayBar(QWidget):
    """ 底部播放栏 """

    nextSongSig = pyqtSignal()
    lastSongSig = pyqtSignal()
    fullScreenSig = pyqtSignal()
    savePlaylistSig = pyqtSignal()
    showPlaylistSig = pyqtSignal()
    clearPlaylistSig = pyqtSignal()
    volumeChanged = pyqtSignal(int)
    togglePlayStateSig = pyqtSignal()
    muteStateChanged = pyqtSignal(bool)
    randomPlayChanged = pyqtSignal(bool)
    progressSliderMoved = pyqtSignal(int)
    showPlayingInterfaceSig = pyqtSignal()
    showSmallestPlayInterfaceSig = pyqtSignal()
    loopModeChanged = pyqtSignal(QMediaPlaylist.PlaybackMode)

    def __init__(self, songInfo: dict, color: QColor, parent=None):
        super().__init__(parent)
        self.originWidth = 1280
        self.__color = color
        self.colorAni = QPropertyAnimation(self, b'color', self)
        self.dominantColor = DominantColor()
        # 记录移动次数
        self.moveTime = 0
        self.resizeTime = 0
        # 实例化小部件
        self.playProgressBar = PlayProgressBar(
            songInfo.get("duration", "0:00"), self)
        self.songInfoCard = SongInfoCard(songInfo, self)
        self.centralButtonGroup = CentralButtonGroup(self)
        self.rightWidgetGroup = RightWidgetGroup(self)
        self.moreActionsMenu = MoreActionsMenu(self)
        # 初始化小部件
        self.__initWidget()
        self.__setQss()

    def __initWidget(self):
        """ 初始化小部件 """
        self.resize(1312, 115)
        self.setFixedHeight(115)
        # 设置背景色
        self.setAutoFillBackground(True)
        self.setColor(self.__color)
        # 引用小部件
        self.referenceWidgets()
        # 连接槽函数
        self.__connectSignalToSlot()
        # 设置小部件位置
        self.__setWidgetPos()

    def __setWidgetPos(self):
        """ 初始化布局 """
        self.playProgressBar.move(
            int(self.width() / 2 - self.playProgressBar.width() / 2),
            self.centralButtonGroup.height(),
        )
        self.centralButtonGroup.move(
            int(self.width() / 2 - self.centralButtonGroup.width() / 2), 0)
        self.rightWidgetGroup.move(
            self.width() - self.rightWidgetGroup.width(), 0)

    def __setQss(self):
        """ 设置层叠样式 """
        with open(r"app\resource\css\play_bar.qss", encoding="utf-8") as f:
            self.setStyleSheet(f.read())

    def resizeEvent(self, e):
        """ 调整歌曲信息卡宽度 """
        deltaWidth = self.width() - self.originWidth
        # 调整进度条的宽度
        self.playProgressBar.resize(
            self.playProgressBar.width() + int(deltaWidth / 3),
            self.playProgressBar.height(),
        )
        # 调整歌曲信息卡宽度和部件位置
        if deltaWidth < 0:
            self.__setWidgetPos()
            self.__adjustSongInfoCardWidth()
        elif deltaWidth > 0:
            if (
                self.playProgressBar.x() <= self.songInfoCard.width() + 20
                or self.songInfoCard.scrollTextWindow.maxWidth != 250
            ):
                self.__setWidgetPos()
                if deltaWidth + self.songInfoCard.width() >= self.songInfoCard.MAXWIDTH:
                    self.songInfoCard.setFixedWidth(
                        min(self.songInfoCard.MAXWIDTH, self.playProgressBar.x() - 20))
                else:
                    self.songInfoCard.setFixedWidth(
                        min(self.songInfoCard.width() + deltaWidth, self.playProgressBar.x() - 20))
                self.songInfoCard.scrollTextWindow.maxWidth = self.songInfoCard.width() - 155
                self.songInfoCard.scrollTextWindow.initFlagsWidth()
            else:
                self.__setWidgetPos()
        self.originWidth = self.width()

    def showMoreActionsMenu(self):
        """ 显示更多操作菜单 """
        globalPos = self.rightWidgetGroup.mapToGlobal(
            self.moreActionsButton.pos())
        x = globalPos.x() + self.moreActionsButton.width() + 30
        y = int(globalPos.y() + self.moreActionsButton.height() / 2 - 152 / 2)
        self.moreActionsMenu.exec(QPoint(x, y))

    def referenceWidgets(self):
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
        # 引用方法
        self.setCurrentTime = self.playProgressBar.setCurrentTime
        self.setTotalTime = self.playProgressBar.setTotalTime

    def updateSongInfoCard(self, songInfo: dict):
        """ 更新歌曲信息卡 """
        self.songInfoCard.updateSongInfoCard(songInfo)
        self.__adjustSongInfoCardWidth()

    def __adjustSongInfoCardWidth(self):
        """ 调整歌曲信息卡宽度 """
        if self.songInfoCard.width() + 20 >= self.playProgressBar.x():
            self.songInfoCard.setFixedWidth(self.playProgressBar.x() - 20)
            self.songInfoCard.scrollTextWindow.maxWidth = self.songInfoCard.width() - 155
            self.songInfoCard.scrollTextWindow.initFlagsWidth()

    def setRandomPlay(self, isRandomPlay: bool):
        """ 设置随机播放 """
        self.randomPlayButton.setRandomPlay(isRandomPlay)

    def setMute(self, isMute: bool):
        """ 设置静音 """
        self.volumeButton.setMute(isMute)

    def setVolume(self, volume: int):
        """ 设置音量 """
        self.volumeSlider.setValue(volume)
        self.volumeButton.setVolumeLevel(volume)

    def setPlay(self, isPlay: bool):
        """ 设置播放状态 """
        self.playButton.setPlay(isPlay)

    def __connectSignalToSlot(self):
        """ 信号连接到槽 """
        self.nextSongButton.clicked.connect(self.nextSongSig)
        self.lastSongButton.clicked.connect(self.lastSongSig)
        self.playButton.clicked.connect(self.togglePlayStateSig)
        self.volumeSlider.valueChanged.connect(self.volumeChanged)
        self.progressSlider.clicked.connect(self.progressSliderMoved)
        self.songInfoCard.clicked.connect(self.showPlayingInterfaceSig)
        self.songInfoCard.albumChanged.connect(self.updateDominantColor)
        self.moreActionsButton.clicked.connect(self.showMoreActionsMenu)
        self.progressSlider.sliderMoved.connect(self.progressSliderMoved)
        self.volumeButton.muteStateChanged.connect(self.muteStateChanged)
        self.loopModeButton.loopModeChanged.connect(self.loopModeChanged)
        self.randomPlayButton.randomPlayChanged.connect(self.randomPlayChanged)
        self.smallPlayModeButton.clicked.connect(
            self.showSmallestPlayInterfaceSig)
        self.moreActionsMenu.fullScreenAct.triggered.connect(
            self.fullScreenSig)
        self.moreActionsMenu.savePlayListAct.triggered.connect(
            self.savePlaylistSig)
        self.moreActionsMenu.showPlayListAct.triggered.connect(
            self.showPlaylistSig)
        self.moreActionsMenu.clearPlayListAct.triggered.connect(
            self.clearPlaylistSig)

    def updateDominantColor(self, albumPath: str):
        """ 更新主色调 """
        r, g, b = self.dominantColor.getDominantColor(albumPath, tuple)
        self.colorAni.setStartValue(self.getColor())
        self.colorAni.setEndValue(QColor(r, g, b))
        self.colorAni.setEasingCurve(QEasingCurve.OutQuart)
        self.colorAni.setDuration(100)
        self.colorAni.start()

    def setColor(self, color: QColor):
        """ 设置背景颜色 """
        self.__color = color
        palette = QPalette()
        palette.setColor(self.backgroundRole(), color)
        self.setPalette(palette)

    def getColor(self):
        return self.__color

    color = pyqtProperty(QColor, getColor, setColor)
