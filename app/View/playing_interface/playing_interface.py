# coding:utf-8
from copy import deepcopy

from common.thread.blur_cover_thread import BlurCoverThread
from components.buttons.three_state_button import ThreeStatePushButton
from components.widgets.menu import AddToMenu
from PyQt5.QtCore import (QAbstractAnimation, QEasingCurve, QFile,
                          QParallelAnimationGroup, QPoint, QPropertyAnimation,
                          QRect, QSize, Qt, QTimer, pyqtSignal)
from PyQt5.QtMultimedia import QMediaPlaylist
from PyQt5.QtWidgets import QLabel, QWidget

from .play_bar import PlayBar
from .selection_mode_bar import SelectionModeBar
from .song_info_card_chute import SongInfoCardChute
from .song_list_widget import SongListWidget


def handleSelectionMode(func):
    """ 处理选择模式装饰器 """

    def wrapper(playingInterface, *args, **kwargs):
        if playingInterface.isInSelectionMode:
            playingInterface.exitSelectionMode()
        return func(playingInterface, *args, **kwargs)

    return wrapper


class PlayingInterface(QWidget):
    """ 正在播放界面 """

    lastSongSig = pyqtSignal()                           # 上一首
    nextSongSig = pyqtSignal()                           # 下一首
    togglePlayStateSig = pyqtSignal()                    # 播放/暂停
    volumeChanged = pyqtSignal(int)                      # 改变音量
    randomPlayAllSig = pyqtSignal()                      # 创建新的无序播放列表
    randomPlayChanged = pyqtSignal(bool)                 # 随机播放当前播放列表
    removeMediaSignal = pyqtSignal(int)                  # 从播放列表移除歌曲
    muteStateChanged = pyqtSignal(bool)                  # 静音/取消静音
    progressSliderMoved = pyqtSignal(int)                # 歌曲进度条滑动
    fullScreenChanged = pyqtSignal(bool)                 # 进入/退出全屏
    clearPlaylistSig = pyqtSignal()                      # 清空播放列表
    savePlaylistSig = pyqtSignal()                       # 保存播放列表
    currentIndexChanged = pyqtSignal(int)                # 当前歌曲改变
    selectionModeStateChanged = pyqtSignal(bool)         # 进入/退出选择模式
    switchToSingerInterfaceSig = pyqtSignal(str)         # 切换到歌手界面
    switchToAlbumInterfaceSig = pyqtSignal(str, str)     # 切换到专辑界面
    showSmallestPlayInterfaceSig = pyqtSignal()          # 进入最小播放模式
    addSongsToNewCustomPlaylistSig = pyqtSignal(list)    # 将歌曲添加到新的自定义播放列表
    addSongsToCustomPlaylistSig = pyqtSignal(str, list)  # 将歌曲添加到已存在的自定义播放列表
    loopModeChanged = pyqtSignal(QMediaPlaylist.PlaybackMode)

    def __init__(self, playlist: list = None, parent=None):
        super().__init__(parent)
        self.playlist = deepcopy(playlist) if playlist else []
        self.currentIndex = 0
        self.isPlaylistVisible = False
        self.isInSelectionMode = True
        # 创建小部件
        self.blurPixmap = None
        self.blurBackgroundPic = QLabel(self)
        self.blurCoverThread = BlurCoverThread(self)
        self.songInfoCardChute = SongInfoCardChute(self.playlist, self)
        self.parallelAniGroup = QParallelAnimationGroup(self)
        self.songInfoCardChuteAni = QPropertyAnimation(
            self.songInfoCardChute, b"geometry")
        self.playBar = PlayBar(self)
        self.songListWidget = SongListWidget(self.playlist, self)
        self.playBarAni = QPropertyAnimation(self.playBar, b"geometry")
        self.songListWidgetAni = QPropertyAnimation(
            self.songListWidget, b"geometry")
        self.selectionModeBar = SelectionModeBar(self)
        self.guideLabel = QLabel(self.tr(
            "Here, you will see the song being played and the songs to be played."), self)
        self.randomPlayAllButton = ThreeStatePushButton(
            {
                "normal": ":/images/playing_interface/Shuffle_normal.png",
                "hover": ":/images/playing_interface/Shuffle_hover.png",
                "pressed": ":/images/playing_interface/Shuffle_pressed.png",
            },
            self.tr(" Shuffle all songs in your collection"),
            (30, 22),
            self
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
        self.randomPlayAllButton.hide()
        self.selectionModeBar.hide()
        self.guideLabel.hide()
        self.playBar.hide()
        # 设置层叠样式
        self.__setQss()
        # 开启磨砂线程
        if self.playlist:
            self.startBlurThread(
                self.songInfoCardChute.cards[1].albumCoverPath)
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
        self.hidePlaylistTimer.timeout.connect(self.hidePlaylistTimerSlot)

    def __setQss(self):
        """ 设置层叠样式 """
        self.setObjectName("playingInterface")
        self.guideLabel.setObjectName("guideLabel")
        self.randomPlayAllButton.setObjectName("randomPlayAllButton")
        f = QFile(":/qss/playing_interface.qss")
        f.open(QFile.ReadOnly)
        self.setStyleSheet(str(f.readAll(), encoding='utf-8'))
        f.close()

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

    def startBlurThread(self, albumCoverPath: str):
        """ 开启磨砂线程 """
        self.blurCoverThread.setTargetCover(albumCoverPath, 15)
        self.blurCoverThread.start()

    def resizeEvent(self, e):
        """ 改变尺寸时也改变小部件的大小 """
        super().resizeEvent(e)
        self.__resizeBlurPixmap()
        self.songInfoCardChute.resize(self.size())
        self.blurBackgroundPic.setFixedSize(self.size())
        self.playBar.resize(self.width(), self.playBar.height())
        self.songListWidget.resize(self.width(), self.height() - 382)
        self.selectionModeBar.resize(
            self.width(), self.selectionModeBar.height())
        self.selectionModeBar.move(
            0, self.height()-self.selectionModeBar.height())
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
        if self.playBar.isVisible():
            return
        self.playBar.show()
        self.songInfoCardChuteAni.setDuration(450)
        self.songInfoCardChuteAni.setEasingCurve(QEasingCurve.OutCubic)
        self.songInfoCardChuteAni.setStartValue(
            self.songInfoCardChute.rect())
        self.songInfoCardChuteAni.setEndValue(
            QRect(0, -self.playBar.height() + 68, self.width(), self.height()))
        self.songInfoCardChuteAni.start()

    def hidePlayBar(self):
        """ 隐藏播放栏 """
        if not self.playBar.isVisible() or self.isPlaylistVisible:
            return
        self.playBar.hide()
        self.songInfoCardChuteAni.setEasingCurve(QEasingCurve.OutCirc)
        self.songInfoCardChuteAni.setStartValue(
            QRect(0, -self.playBar.height() + 68, self.width(), self.height()))
        self.songInfoCardChuteAni.setEndValue(
            QRect(0, 0, self.width(), self.height()))
        self.songInfoCardChuteAni.start()

    def showPlaylist(self):
        """ 显示播放列表 """
        if self.songListWidgetAni.state() == QAbstractAnimation.Running:
            return
        self.songInfoCardChuteAni.setDuration(350)
        self.songInfoCardChuteAni.setEasingCurve(QEasingCurve.InOutQuad)
        self.songInfoCardChuteAni.setStartValue(
            QRect(0, self.songInfoCardChute.y(), self.width(), self.height()))
        self.songInfoCardChuteAni.setEndValue(
            QRect(0, 258 - self.height(), self.width(), self.height()))
        self.playBarAni.setStartValue(
            QRect(0, self.playBar.y(), self.width(), self.playBar.height()))
        self.playBarAni.setEndValue(
            QRect(0, 190, self.width(), self.playBar.height()))
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

    def hidePlaylistTimerSlot(self):
        """ 显示播放列表定时器溢出槽函数 """
        self.hidePlaylistTimer.stop()
        self.parallelAniGroup.start()

    @handleSelectionMode
    def hidePlaylist(self):
        """ 隐藏播放列表 """
        if self.parallelAniGroup.state() == QAbstractAnimation.Running:
            return
        self.songInfoCardChuteAni.setDuration(350)
        self.songInfoCardChuteAni.setEasingCurve(QEasingCurve.InOutQuad)
        self.songInfoCardChuteAni.setStartValue(
            QRect(0, self.songInfoCardChute.y(), self.width(), self.height()))
        self.songInfoCardChuteAni.setEndValue(
            QRect(0, -self.playBar.height() + 68, self.width(), self.height()))
        self.playBarAni.setStartValue(
            QRect(0, 190, self.width(), self.playBar.height()))
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
        if self.sender() is self.playBar.showPlaylistButton:
            self.playBar.pullUpArrowButton.timer.start()
        # self.parallelAniGroup.start()
        self.songListWidgetAni.start()
        self.hidePlaylistTimer.start()
        self.blurBackgroundPic.show()
        self.isPlaylistVisible = False

    def __onShowPlaylistButtonClicked(self):
        """ 显示或隐藏播放列表 """
        if not self.isPlaylistVisible:
            self.showPlaylist()
        else:
            self.hidePlaylist()

    def setCurrentIndex(self, index):
        """ 更新播放列表下标 """
        # 下标大于等于0时才更新
        if self.currentIndex == index or index <= -1:
            return
        # 在播放列表的最后一首歌被移除时不更新样式
        if index >= len(self.playlist):
            return
        self.currentIndex = index
        self.songListWidget.setCurrentIndex(index)
        self.songInfoCardChute.setCurrentIndex(index)

    def setPlaylist(self, playlist: list, isResetIndex: bool = True, index=0):
        """ 更新播放列表

        Parameters
        ----------
        playlist: list
            播放列表，每一个元素都是songInfo字典

        isResetIndex: bool
            是否重置当前歌曲索引

        index: int
            重置后的当前歌曲索引
        """
        self.playlist = deepcopy(playlist) if playlist else []
        self.currentIndex = index if isResetIndex else self.currentIndex
        self.songInfoCardChute.setPlaylist(self.playlist, isResetIndex, index)
        self.songListWidget.updateSongCards(self.playlist, isResetIndex, index)
        self.startBlurThread(self.songInfoCardChute.cards[1].albumCoverPath)

        # 如果小部件不可见就显示
        if playlist and not self.songListWidget.isVisible():
            self.__setGuideLabelHidden(True)
        else:
            self.__setGuideLabelHidden(False)

    def setPlay(self, isPlay: bool):
        """ 设置播放状态 """
        self.playBar.playButton.setPlay(isPlay)

    def __settleDownPlayBar(self):
        """ 定住播放栏 """
        self.songInfoCardChute.stopSongInfoCardTimer()

    def __startSongInfoCardTimer(self):
        """ 重新打开歌曲信息卡的定时器 """
        if not self.playBar.volumeSliderWidget.isVisible():
            # 只有音量滑动条不可见才打开计时器
            self.songInfoCardChute.startSongInfoCardTimer()

    def __removeSongFromPlaylist(self, index):
        """ 从播放列表中移除选中的歌曲 """

        if self.currentIndex > index:
            self.currentIndex -= 1
            self.songInfoCardChute.currentIndex -= 1

        elif self.currentIndex == index:
            self.currentIndex -= 1
            self.songInfoCardChute.currentIndex -= 1

        # 强制更新当前歌曲的信息
        n = len(self.playlist)
        if n > 0:
            self.songInfoCardChute.cards[1].updateCard(
                self.playlist[self.currentIndex])

            if self.currentIndex == n-1:
                self.songInfoCardChute.cards[-1].hide()
            else:
                self.songInfoCardChute.cards[-1].updateCard(
                    self.playlist[self.currentIndex+1])

            if self.currentIndex == 0:
                self.songInfoCardChute.cards[0].hide()
            else:
                self.songInfoCardChute.cards[0].updateCard(
                    self.playlist[self.currentIndex-1])

        self.removeMediaSignal.emit(index)

        # 如果播放列表为空，隐藏小部件
        if len(self.playlist) == 0:
            self.__setGuideLabelHidden(False)

    @handleSelectionMode
    def clearPlaylist(self):
        """ 清空歌曲卡 """
        self.playlist.clear()
        self.songListWidget.clearSongCards()
        # 显示随机播放所有按钮
        self.__setGuideLabelHidden(False)
        self.playBar.hide()

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

    def updateOneSongCard(self, newSongInfo: dict):
        """ 更新一个歌曲卡 """
        self.songListWidget.updateOneSongCard(newSongInfo)
        self.playlist = self.songListWidget.songInfo_list
        self.songInfoCardChute.playlist = self.playlist

    def updateMultiSongCards(self, newSongInfo_list: list):
        """ 更新多个歌曲卡 """
        self.songListWidget.updateMultiSongCards(newSongInfo_list)
        self.playlist = self.songListWidget.songInfo_list
        self.songInfoCardChute.playlist = self.playlist

    @handleSelectionMode
    def __onShowSmallestPlayInterfaceButtonClicked(self):
        """ 显示最小播放模式界面 """
        self.fullScreenChanged.emit(False)
        self.showSmallestPlayInterfaceSig.emit()

    def setRandomPlay(self, isRandomPlay: bool):
        """ 设置随机播放 """
        self.playBar.randomPlayButton.setRandomPlay(isRandomPlay)

    def setMute(self, isMute: bool):
        """ 设置静音 """
        self.playBar.volumeButton.setMute(isMute)
        self.playBar.volumeSliderWidget.volumeButton.setMute(isMute)

    def setVolume(self, volume: int):
        """ 设置音量 """
        self.playBar.volumeSliderWidget.setVolume(volume)

    def setCurrentTime(self, currentTime: int):
        """ 设置当前进度条时间 """
        self.playBar.setCurrentTime(currentTime)

    def setFullScreen(self, isFullScreen: int):
        """ 更新全屏按钮图标 """
        self.playBar.FullScreenButton.setFullScreen(isFullScreen)

    def setLoopMode(self, loopMode: QMediaPlaylist.PlaybackMode):
        """ 设置循环模式 """
        self.playBar.loopModeButton.setLoopMode(loopMode)

    def __onSelectionModeChanged(self, isOpenSelectionMode: bool):
        """ 选择模式状态变化槽函数 """
        self.isInSelectionMode = isOpenSelectionMode
        self.selectionModeBar.setVisible(isOpenSelectionMode)
        self.selectionModeStateChanged.emit(isOpenSelectionMode)

    def __onCancelButtonClicked(self):
        """ 选择栏取消按钮点击槽函数 """
        self.selectionModeBar.checkAllButton.setCheckedState(
            not self.songListWidget.isAllSongCardsChecked)
        self.songListWidget.unCheckAllSongCards()
        self.selectionModeBar.checkAllButton.setCheckedState(True)

    def __onCheckAllButtonClicked(self):
        """ 全选/取消全选按钮点击槽函数 """
        isChecked = not self.songListWidget.isAllSongCardsChecked
        self.songListWidget.setAllSongCardCheckedState(isChecked)
        self.selectionModeBar.checkAllButton.setCheckedState(isChecked)

    def __onSelectionModeBarAlbumButtonClicked(self):
        """ 选择栏显示专辑按钮点击槽函数 """
        songCard = self.songListWidget.checkedSongCard_list[0]
        songCard.setChecked(False)
        self.switchToAlbumInterfaceSig.emit(songCard.album, songCard.singer)

    def __onSelectionModeBarDeleteButtonClicked(self):
        """ 选择栏播放按钮点击槽函数 """
        for songCard in self.songListWidget.checkedSongCard_list.copy():
            songCard.setChecked(False)
            self.songListWidget.removeSongCard(songCard.itemIndex)

    def __onSelectionModeBarPlayButtonClicked(self):
        """ 选择栏播放按钮点击槽函数 """
        songCard = self.songListWidget.checkedSongCard_list[0]
        songCard.setChecked(False)
        self.currentIndexChanged.emit(songCard.itemIndex)

    def __onSelectionModeBarPropertyButtonClicked(self):
        """ 选择栏播放按钮点击槽函数 """
        songCard = self.songListWidget.checkedSongCard_list[0]
        songCard.setChecked(False)
        self.songListWidget.showSongPropertyDialog(songCard)

    def __onSelectionModeBarAddToButtonClicked(self):
        """ 选择栏添加到按钮点击槽函数 """
        menu = AddToMenu(parent=self)
        btn = self.selectionModeBar.addToButton
        pos = self.selectionModeBar.mapToGlobal(btn.pos())
        x = pos.x()+btn.width()+5
        y = pos.y()+btn.height()//2-(13+38*menu.actionCount())//2
        songInfo_list = [
            i.songInfo for i in self.songListWidget.checkedSongCard_list]
        # 菜单信号连接到槽
        for act in menu.action_list:
            act.triggered.connect(self.exitSelectionMode)
        menu.newPlaylistAct.triggered.connect(
            lambda: self.addSongsToNewCustomPlaylistSig.emit(songInfo_list))
        menu.addSongsToPlaylistSig.connect(
            lambda name: self.addSongsToCustomPlaylistSig.emit(name, songInfo_list))
        menu.exec(QPoint(x, y))

    def exitSelectionMode(self):
        """ 退出选择模式 """
        self.__onCancelButtonClicked()

    def __connectSignalToSlot(self):
        """ 将信号连接到槽 """
        self.blurCoverThread.blurDone.connect(self.setBlurPixmap)
        self.randomPlayAllButton.clicked.connect(self.randomPlayAllSig)

        # 歌曲信息卡滑动槽信号连接到槽
        self.songInfoCardChute.currentIndexChanged[int].connect(
            self.currentIndexChanged)
        self.songInfoCardChute.currentIndexChanged[str].connect(
            self.startBlurThread)
        self.songInfoCardChute.switchToAlbumInterfaceSig.connect(
            self.switchToAlbumInterfaceSig)
        self.songInfoCardChute.showPlayBarSignal.connect(self.showPlayBar)
        self.songInfoCardChute.hidePlayBarSignal.connect(self.hidePlayBar)

        # 将播放栏的信号连接到槽
        self.playBar.randomPlayButton.randomPlayChanged.connect(
            self.randomPlayChanged)
        self.playBar.volumeSliderWidget.muteStateChanged.connect(
            self.muteStateChanged)
        self.playBar.volumeSliderWidget.volumeSlider.valueChanged.connect(
            self.volumeChanged)
        self.playBar.FullScreenButton.fullScreenChanged.connect(
            self.fullScreenChanged)
        self.playBar.progressSlider.sliderMoved.connect(
            self.progressSliderMoved)
        self.playBar.progressSlider.clicked.connect(self.progressSliderMoved)
        self.playBar.lastSongButton.clicked.connect(self.lastSongSig)
        self.playBar.nextSongButton.clicked.connect(self.nextSongSig)
        self.playBar.playButton.clicked.connect(self.togglePlayStateSig)
        self.playBar.loopModeButton.loopModeChanged.connect(
            self.loopModeChanged)
        self.playBar.pullUpArrowButton.clicked.connect(
            self.__onShowPlaylistButtonClicked)
        self.playBar.showPlaylistButton.clicked.connect(
            self.__onShowPlaylistButtonClicked)
        self.playBar.smallPlayModeButton.clicked.connect(
            lambda i: self.__onShowSmallestPlayInterfaceButtonClicked())
        self.playBar.enterSignal.connect(self.__settleDownPlayBar)
        self.playBar.leaveSignal.connect(self.__startSongInfoCardTimer)
        self.playBar.moreActionsMenu.clearPlayListAct.triggered.connect(
            self.clearPlaylistSig)
        self.playBar.moreActionsMenu.savePlayListAct.triggered.connect(
            self.savePlaylistSig)

        # 将歌曲列表的信号连接到槽函数
        self.songListWidget.currentIndexChanged.connect(
            self.currentIndexChanged)
        self.songListWidget.removeSongSig.connect(
            self.__removeSongFromPlaylist)
        self.songListWidget.addSongsToCustomPlaylistSig.connect(
            self.addSongsToCustomPlaylistSig)
        self.songListWidget.addSongsToNewCustomPlaylistSig.connect(
            self.addSongsToNewCustomPlaylistSig)
        self.songListWidget.selectionModeStateChanged.connect(
            self.__onSelectionModeChanged)
        self.songListWidget.checkedSongCardNumChanged.connect(
            lambda n: self.selectionModeBar.setPartButtonHidden(n > 1))
        self.songListWidget.isAllCheckedChanged.connect(
            lambda x: self.selectionModeBar.checkAllButton.setCheckedState(not x))
        self.songListWidget.switchToAlbumInterfaceSig.connect(
            self.switchToAlbumInterfaceSig)
        self.songListWidget.switchToSingerInterfaceSig.connect(
            self.switchToSingerInterfaceSig)

        # 选择栏信号连接到槽函数
        self.selectionModeBar.cancelButton.clicked.connect(
            self.__onCancelButtonClicked)
        self.selectionModeBar.checkAllButton.clicked.connect(
            self.__onCheckAllButtonClicked)
        self.selectionModeBar.playButton.clicked.connect(
            self.__onSelectionModeBarPlayButtonClicked)
        self.selectionModeBar.deleteButton.clicked.connect(
            self.__onSelectionModeBarDeleteButtonClicked)
        self.selectionModeBar.propertyButton.clicked.connect(
            self.__onSelectionModeBarPropertyButtonClicked)
        self.selectionModeBar.showAlbumButton.clicked.connect(
            self.__onSelectionModeBarAlbumButtonClicked)
        self.selectionModeBar.addToButton.clicked.connect(
            self.__onSelectionModeBarAddToButtonClicked)
