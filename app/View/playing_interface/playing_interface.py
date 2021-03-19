# coding:utf-8

from copy import deepcopy

from app.components.buttons.three_state_button import ThreeStateButton
from PyQt5.QtCore import (
    QAbstractAnimation,
    QEasingCurve,
    QParallelAnimationGroup,
    QPropertyAnimation,
    QRect,
    QSize,
    Qt,
    QTimer,
    pyqtSignal,
)
from PyQt5.QtWidgets import QLabel, QWidget

from .blur_cover_thread import BlurCoverThread
from .play_bar import PlayBar
from .smallest_play_mode_interface import SmallestPlayModeInterface
from .song_info_card_chute import SongInfoCardChute
from .song_list_widget import SongListWidget


class PlayingInterface(QWidget):
    """ 正在播放界面 """

    nextSongSig = pyqtSignal()  # 点击下一首或者上一首按钮时由主界面的播放列表决定下一首的Index
    lastSongSig = pyqtSignal()
    switchPlayStateSig = pyqtSignal()
    randomPlayAllSignal = pyqtSignal()
    removeMediaSignal = pyqtSignal(int)
    # 点击歌曲卡或者滑动歌曲信息卡滑槽时直接设置新的index，index由自己决定
    currentIndexChanged = pyqtSignal(int)
    switchToAlbumInterfaceSig = pyqtSignal(str, str)
    # 发出进入最小模式的信号
    smallestModeStateChanged = pyqtSignal(bool)
    # 退出全屏信号
    exitFullScreenSig = pyqtSignal()

    def __init__(self, playlist: list = None, parent=None):
        super().__init__(parent)
        self.playlist = playlist.copy()
        self.currentIndex = 0
        self.isPlaylistVisible = False
        # 创建小部件
        self.blurPixmap = None
        self.blurBackgroundPic = QLabel(self)
        self.blurCoverThread = BlurCoverThread(self)
        self.songInfoCardChute = SongInfoCardChute(self, self.playlist)
        self.parallelAniGroup = QParallelAnimationGroup(self)
        self.songInfoCardChuteAni = QPropertyAnimation(
            self.songInfoCardChute, b"geometry"
        )
        self.playBar = PlayBar(self)
        self.songListWidget = SongListWidget(self.playlist, self)
        self.smallestModeInterface = SmallestPlayModeInterface(playlist, self)
        self.playBarAni = QPropertyAnimation(self.playBar, b"geometry")
        self.songListWidgetAni = QPropertyAnimation(self.songListWidget, b"geometry")
        self.guideLabel = QLabel("在这里，你将看到正在播放的歌曲以及即将播放的歌曲。", self)
        self.randomPlayAllButton = ThreeStateButton(
            {
                "normal": r"app\resource\images\playing_interface\全部随机播放_normal_256_39.png",
                "hover": r"app\resource\images\playing_interface\全部随机播放_hover_256_39.png",
                "pressed": r"app\resource\images\playing_interface\全部随机播放_pressed_256_39.png",
            },
            self,
            (256, 39),
        )
        # 创建定时器
        self.showPlaylistTimer = QTimer(self)
        self.hidePlaylistTimer = QTimer(self)
        # 初始化
        self.__initWidget()

    def __initWidget(self):
        """ 初始化小部件 """
        self.resize(1100, 870)
        self.currentSmallestModeSize = QSize(340, 340)
        self.setAttribute(Qt.WA_StyledBackground)
        self.guideLabel.move(45, 62)
        self.randomPlayAllButton.move(45, 117)
        self.playBar.move(0, self.height() - self.playBar.height())
        # 隐藏部件
        self.smallestModeInterface.hide()
        self.randomPlayAllButton.hide()
        self.guideLabel.hide()
        self.playBar.hide()
        # 设置层叠样式
        self.setObjectName("playingInterface")
        self.guideLabel.setObjectName("guideLabel")
        self.__setQss()
        # 开启磨砂线程
        if self.playlist:
            self.startBlurThread(self.songInfoCardChute.curSongInfoCard.albumCoverPath)
        # 将信号连接到槽
        self.__connectSignalToSlot()
        # 初始化动画
        self.playBarAni.setDuration(350)
        self.songListWidgetAni.setDuration(350)
        self.songListWidgetAni.setEasingCurve(QEasingCurve.InOutQuad)
        self.playBarAni.setEasingCurve(QEasingCurve.InOutQuad)
        self.parallelAniGroup.addAnimation(self.playBarAni)
        self.parallelAniGroup.addAnimation(self.songInfoCardChuteAni)
        # 初始化定时器
        self.showPlaylistTimer.setInterval(120)
        self.hidePlaylistTimer.setInterval(120)
        self.showPlaylistTimer.timeout.connect(self.showPlayListTimerSlot)
        self.hidePlaylistTimer.timeout.connect(self.hidePlayListTimerSlot)

    def __setQss(self):
        """ 设置层叠样式 """
        with open(r"app\resource\css\playInterface.qss", encoding="utf-8") as f:
            self.setStyleSheet(f.read())

    def setBlurPixmap(self, blurPixmap):
        """ 设置磨砂pixmap """
        self.blurPixmap = blurPixmap
        # 更新背景
        self.__resizeBlurPixmap()

    def __resizeBlurPixmap(self):
        """ 调整背景图尺寸 """
        maxWidth = max(self.width(), self.height())
        if self.blurPixmap:
            self.blurBackgroundPic.setPixmap(
                self.blurPixmap.scaled(
                    maxWidth,
                    maxWidth,
                    Qt.KeepAspectRatioByExpanding,
                    Qt.SmoothTransformation,
                )
            )

    def startBlurThread(self, albumCoverPath):
        """ 开启磨砂线程 """
        blurRadius = [6, 40][self.smallestModeInterface.isVisible()]
        self.blurCoverThread.setTargetCover(albumCoverPath, blurRadius=blurRadius)
        self.blurCoverThread.start()

    def resizeEvent(self, e):
        """ 改变尺寸时也改变小部件的大小 """
        super().resizeEvent(e)
        self.__resizeBlurPixmap()
        self.songInfoCardChute.resize(self.size())
        self.blurBackgroundPic.setFixedSize(self.size())
        self.playBar.resize(self.width(), self.playBar.height())
        self.songListWidget.resize(self.width(), self.height() - 382)
        self.smallestModeInterface.resize(self.size())
        if self.isPlaylistVisible:
            self.playBar.move(0, 190)
            self.songListWidget.move(0, 382)
            self.songInfoCardChute.move(0, 258 - self.height())
        else:
            self.playBar.move(0, self.height() - self.playBar.height())
            self.songListWidget.move(0, self.height())

    def showPlayBar(self):
        """ 显示播放栏 """
        # 只在播放栏不可见的时候显示播放栏和开启动画
        if not self.playBar.isVisible():
            self.playBar.show()
            self.songInfoCardChuteAni.setDuration(450)
            self.songInfoCardChuteAni.setEasingCurve(QEasingCurve.OutCubic)
            self.songInfoCardChuteAni.setStartValue(self.songInfoCardChute.rect())
            self.songInfoCardChuteAni.setEndValue(
                QRect(0, -self.playBar.height() + 68, self.width(), self.height())
            )
            self.songInfoCardChuteAni.start()

    def hidePlayBar(self):
        """ 隐藏播放栏 """
        if self.playBar.isVisible() and not self.isPlaylistVisible:
            self.playBar.hide()
            self.songInfoCardChuteAni.setEasingCurve(QEasingCurve.OutCirc)
            self.songInfoCardChuteAni.setStartValue(
                QRect(0, -self.playBar.height() + 68, self.width(), self.height())
            )
            self.songInfoCardChuteAni.setEndValue(
                QRect(0, 0, self.width(), self.height())
            )
            self.songInfoCardChuteAni.start()

    def showPlaylist(self):
        """ 显示播放列表 """
        if self.songListWidgetAni.state() != QAbstractAnimation.Running:
            self.songInfoCardChuteAni.setDuration(350)
            self.songInfoCardChuteAni.setEasingCurve(QEasingCurve.InOutQuad)
            self.songInfoCardChuteAni.setStartValue(
                QRect(0, self.songInfoCardChute.y(), self.width(), self.height())
            )
            self.songInfoCardChuteAni.setEndValue(
                QRect(0, 258 - self.height(), self.width(), self.height())
            )
            self.playBarAni.setStartValue(
                QRect(0, self.playBar.y(), self.width(), self.playBar.height())
            )
            self.playBarAni.setEndValue(
                QRect(0, 190, self.width(), self.playBar.height())
            )
            self.songListWidgetAni.setStartValue(
                QRect(
                    self.songListWidget.x(),
                    self.songListWidget.y(),
                    self.songListWidget.width(),
                    self.songListWidget.height(),
                )
            )
            self.songListWidgetAni.setEndValue(
                QRect(
                    self.songListWidget.x(),
                    382,
                    self.songListWidget.width(),
                    self.songListWidget.height(),
                )
            )
            if self.sender() == self.playBar.showPlaylistButton:
                self.playBar.pullUpArrowButton.timer.start()
            self.playBar.show()
            self.parallelAniGroup.start()
            self.blurBackgroundPic.hide()
            self.showPlaylistTimer.start()

    def showPlayListTimerSlot(self):
        """ 显示播放列表定时器溢出槽函数 """
        self.showPlaylistTimer.stop()
        self.songListWidgetAni.start()
        self.isPlaylistVisible = True

    def hidePlayListTimerSlot(self):
        """ 显示播放列表定时器溢出槽函数 """
        self.hidePlaylistTimer.stop()
        self.parallelAniGroup.start()

    def hidePlaylist(self):
        """ 隐藏播放列表 """
        if self.parallelAniGroup.state() != QAbstractAnimation.Running:
            self.songInfoCardChuteAni.setDuration(350)
            self.songInfoCardChuteAni.setEasingCurve(QEasingCurve.InOutQuad)
            self.songInfoCardChuteAni.setStartValue(
                QRect(0, self.songInfoCardChute.y(), self.width(), self.height())
            )
            self.songInfoCardChuteAni.setEndValue(
                QRect(0, -self.playBar.height() + 68, self.width(), self.height())
            )
            self.playBarAni.setStartValue(
                QRect(0, 190, self.width(), self.playBar.height())
            )
            self.playBarAni.setEndValue(
                QRect(
                    0,
                    self.height() - self.playBar.height(),
                    self.width(),
                    self.playBar.height(),
                )
            )
            self.songListWidgetAni.setStartValue(
                QRect(
                    self.songListWidget.x(),
                    self.songListWidget.y(),
                    self.songListWidget.width(),
                    self.songListWidget.height(),
                )
            )
            self.songListWidgetAni.setEndValue(
                QRect(
                    self.songListWidget.x(),
                    self.height(),
                    self.songListWidget.width(),
                    self.songListWidget.height(),
                )
            )
            if self.sender() == self.playBar.showPlaylistButton:
                self.playBar.pullUpArrowButton.timer.start()
            # self.parallelAniGroup.start()
            self.songListWidgetAni.start()
            self.hidePlaylistTimer.start()
            self.blurBackgroundPic.show()
            self.isPlaylistVisible = False

    def showPlaylistButtonSlot(self):
        """ 显示或隐藏播放列表 """
        if not self.isPlaylistVisible:
            self.showPlaylist()
        else:
            self.hidePlaylist()

    def setCurrentIndex(self, index):
        """ 更新播放列表下标 """
        # 下标大于等于0时才更新
        if self.currentIndex != index and index > -1:
            # 在播放列表的最后一首歌被移除时不更新样式
            if index >= len(self.playlist):
                return
            if self.smallestModeInterface.isVisible():
                self.smallestModeInterface.setCurrentIndex(index)
            self.currentIndex = index
            self.songListWidget.setCurrentIndex(index)
            self.songInfoCardChute.setCurrentIndex(index)

    def setPlaylist(self, playlist: list, isResetIndex: bool = True):
        """ 更新播放列表

        Parameters
        ----------
        playlist: list
            播放列表，每一个元素都是songInfo字典

        isResetIndex: bool
            是否将下标重置为0
        """
        self.playlist = deepcopy(playlist)
        self.currentIndex = 0 if isResetIndex else self.currentIndex
        if playlist:
            self.songInfoCardChute.setPlaylist(self.playlist, isResetIndex)
            self.smallestModeInterface.setPlaylist(self.playlist, isResetIndex)
            self.songListWidget.updateSongCards(self.playlist)
        # 如果小部件不可见就显示
        if playlist and not self.songListWidget.isVisible():
            self.__setGuideLabelHidden(True)

    def __settleDownPlayBar(self):
        """ 定住播放栏 """
        self.songInfoCardChute.stopSongInfoCardTimer()

    def __startSongInfoCardTimer(self):
        """ 重新打开歌曲信息卡的定时器 """
        if not self.playBar.volumeSlider.isVisible():
            # 只有音量滑动条不可见才打开计时器
            self.songInfoCardChute.startSongInfoCardTimer()

    def __songListWidgetCurrentChangedSlot(self, index):
        """ 歌曲列表当前下标改变插槽 """
        self.currentIndex = index
        self.songInfoCardChute.setCurrentIndex(index)
        self.currentIndexChanged.emit(index)

    def __songInfoCardChuteCurrentChangedSlot(self, index):
        """ 歌曲列表当前下标改变插槽 """
        self.currentIndex = index
        self.songListWidget.setCurrentIndex(index)
        self.currentIndexChanged.emit(index)

    def __removeSongFromPlaylist(self, index):
        """ 从播放列表中移除选中的歌曲 """
        lastSongRemoved = False
        if self.currentIndex > index:
            self.currentIndex -= 1
            self.songInfoCardChute.currentIndex -= 1
        elif self.currentIndex == index:
            # 如果被移除的是最后一首需要将当前下标-1
            if index == self.songListWidget.currentIndex + 1:
                self.currentIndex -= 1
                self.songInfoCardChute.currentIndex -= 1
                lastSongRemoved = True
            else:
                self.songInfoCardChute.setCurrentIndex(self.currentIndex)
        self.removeMediaSignal.emit(index)
        # 如果播放列表为空，隐藏小部件
        if len(self.playlist) == 0:
            self.__setGuideLabelHidden(False)
        # 如果被移除的是最后一首就将当前播放歌曲置为被移除后的播放列表最后一首
        """ if lastSongRemoved:
            self.currentIndexChanged.emit(self.currentIndex) """

    def clearPlaylist(self):
        """ 清空歌曲卡 """
        self.playlist.clear()
        self.songListWidget.clearSongCards()
        # 显示随机播放所有按钮
        self.__setGuideLabelHidden(False)

    def __setGuideLabelHidden(self, isHidden):
        """ 设置导航标签和随机播放所有按钮的可见性 """
        self.randomPlayAllButton.setHidden(isHidden)
        self.guideLabel.setHidden(isHidden)
        self.songListWidget.setHidden(not isHidden)
        if isHidden:
            # 隐藏导航标签时根据播放列表是否可见设置磨砂背景和播放栏的可见性
            self.blurBackgroundPic.setHidden(self.isPlaylistVisible)
            self.playBar.setHidden(not self.isPlaylistVisible)
        else:
            # 显示导航标签时隐藏磨砂背景
            self.blurBackgroundPic.hide()
            self.playBar.hide()
        # 最后再显示歌曲信息卡
        self.songInfoCardChute.setHidden(not isHidden)

    def updateOneSongCard(self, oldSongInfo: dict, newSongInfo):
        """ 更新一个歌曲卡 """
        self.songListWidget.updateOneSongCard(oldSongInfo, newSongInfo)
        self.playlist = self.songListWidget.playlist
        self.songInfoCardChute.playlist = self.playlist

    def updateMultiSongCards(self, oldSongInfo_list: list, newSongInfo_list: list):
        """ 更新多个歌曲卡 """
        self.songListWidget.updateMultiSongCards(oldSongInfo_list, newSongInfo_list)
        self.playlist = self.songListWidget.playlist
        self.songInfoCardChute.playlist = self.playlist

    def showSmallestModeInterface(self):
        """ 显示最小播放模式界面 """
        self.exitFullScreenSig.emit()
        # 记录下正常尺寸
        self.currentGeometry = self.window().geometry()  # type:QRect
        # 更新磨砂半径
        self.blurCoverThread.setTargetCover(
            self.blurCoverThread.albumCoverPath, 40, (350, 350)
        )
        self.blurCoverThread.start()
        self.playBar.hide()
        self.songListWidget.hide()
        self.songInfoCardChute.hide()
        self.blurBackgroundPic.show()
        # 先更新歌曲信息卡再显示界面
        self.smallestModeInterface.setCurrentIndex(self.currentIndex)
        self.smallestModeInterface.show()
        # 发出隐藏标题栏按钮的信号
        self.smallestModeStateChanged.emit(True)
        self.window().setMinimumSize(206, 197)
        self.window().setGeometry(
            self.currentGeometry.x()
            + self.currentGeometry.width()
            - self.currentSmallestModeSize.width(),
            self.currentGeometry.y(),
            self.currentSmallestModeSize.width(),
            self.currentSmallestModeSize.height(),
        )

    def __hideSmallestModeInterface(self):
        """ 隐藏最小播放模式界面 """
        # 记录下最小播放模式的尺寸
        self.currentSmallestModeSize = self.window().size()  # type:QSize
        # 更新磨砂半径
        self.blurCoverThread.setTargetCover(
            self.blurCoverThread.albumCoverPath, 6, (450, 450)
        )
        self.blurCoverThread.start()
        self.smallestModeInterface.hide()
        self.window().setMinimumSize(1030, 850)
        self.window().setGeometry(self.currentGeometry)
        # 发出显示标题栏按钮的信号
        self.smallestModeStateChanged.emit(False)
        self.blurBackgroundPic.setHidden(self.isPlaylistVisible)
        self.playBar.show()
        self.songListWidget.show()
        self.songInfoCardChute.show()

    def __connectSignalToSlot(self):
        """ 将信号连接到槽 """
        self.blurCoverThread.blurDone.connect(self.setBlurPixmap)
        # 更新背景封面和下标
        self.songInfoCardChute.currentIndexChanged[int].connect(
            self.__songInfoCardChuteCurrentChangedSlot
        )
        self.songInfoCardChute.currentIndexChanged[str].connect(self.startBlurThread)
        # 显示和隐藏播放栏
        self.songInfoCardChute.showPlayBarSignal.connect(self.showPlayBar)
        self.songInfoCardChute.hidePlayBarSignal.connect(self.hidePlayBar)
        # 将播放栏的信号连接到槽
        self.playBar.lastSongButton.clicked.connect(self.lastSongSig)
        self.playBar.nextSongButton.clicked.connect(self.nextSongSig)
        self.playBar.playButton.clicked.connect(self.switchPlayStateSig)
        self.playBar.pullUpArrowButton.clicked.connect(self.showPlaylistButtonSlot)
        self.playBar.showPlaylistButton.clicked.connect(self.showPlaylistButtonSlot)
        self.playBar.smallPlayModeButton.clicked.connect(self.showSmallestModeInterface)
        self.playBar.enterSignal.connect(self.__settleDownPlayBar)
        self.playBar.leaveSignal.connect(self.__startSongInfoCardTimer)
        # 将歌曲列表的信号连接到槽函数
        self.songListWidget.currentIndexChanged.connect(
            self.__songListWidgetCurrentChangedSlot
        )
        self.songListWidget.removeItemSignal.connect(self.__removeSongFromPlaylist)
        self.randomPlayAllButton.clicked.connect(self.randomPlayAllSignal)
        # 将最小化播放界面的信号连接到槽函数
        self.smallestModeInterface.lastSongButton.clicked.connect(self.lastSongSig)
        self.smallestModeInterface.nextSongButton.clicked.connect(self.nextSongSig)
        self.smallestModeInterface.playButton.clicked.connect(self.switchPlayStateSig)
        self.smallestModeInterface.exitSmallestModeButton.clicked.connect(
            self.__hideSmallestModeInterface
        )
        # 切换到专辑界面
        self.songInfoCardChute.switchToAlbumInterfaceSig.connect(
            self.switchToAlbumInterfaceSig
        )
        self.songListWidget.switchToAlbumInterfaceSig.connect(
            self.switchToAlbumInterfaceSig
        )

