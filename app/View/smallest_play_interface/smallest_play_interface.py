# coding:utf-8
from copy import deepcopy

from app.common.thread.blur_cover_thread import BlurCoverThread
from app.common.os_utils import getCoverPath
from app.components.buttons.circle_button import CircleButton
from app.components.frameless_window import FramelessWindow
from PyQt5.QtCore import (QAbstractAnimation, QEasingCurve, QEvent,
                          QParallelAnimationGroup, QPropertyAnimation, QRect,
                          Qt, pyqtSignal)
from PyQt5.QtGui import QFont, QFontMetrics
from PyQt5.QtWidgets import QGraphicsOpacityEffect, QLabel, QSlider, QWidget

from .buttons import PlayButton, SmallestPlayModeButton
from .title_bar import TitleBar


class SmallestPlayInterface(FramelessWindow):
    """ 最小播放模式界面 """

    CYCLE_LEFT_SHIFT = 0
    CYCLE_RIGHT_SHIFT = 1
    nextSongSig = pyqtSignal()
    lastSongSig = pyqtSignal()
    togglePlayStateSig = pyqtSignal()
    exitSmallestPlayInterfaceSig = pyqtSignal()

    def __init__(self, playlist: list = None, parent=None):
        super().__init__(parent)
        self.playlist = deepcopy(playlist) if playlist else []
        self.currentIndex = 0
        self.shiftLeftTime = 0
        self.shiftRightTime = 0
        self.songInfoCard_list = []
        self.__unCompleteShift_list = []
        self.albumCoverLabel = QLabel(self)
        self.blurCoverThread = BlurCoverThread(self)
        # 创建按钮
        self.playButton = PlayButton(
            [
                r"app\resource\images\smallest_play_interface\Pause.png",
                r"app\resource\images\smallest_play_interface\Play.png",
            ],
            self,
        )
        self.lastSongButton = SmallestPlayModeButton(
            r"app\resource\images\smallest_play_interface\Previous.png", self)
        self.nextSongButton = SmallestPlayModeButton(
            r"app\resource\images\smallest_play_interface\Next.png", self)
        self.exitSmallestModeButton = CircleButton(
            r"app\resource\images\playing_interface\最小模式播放_47_47.png", self)
        self.progressBar = QSlider(Qt.Horizontal, self)
        self.aniGroup = QParallelAnimationGroup(self)
        # 创建标题栏
        self.titleBar = TitleBar(self)
        # 创建歌曲信息卡
        self.__createSongInfoCards()
        # 初始化
        self.__initWidget()

    def __initWidget(self):
        """ 初始化界面 """
        self.resize(350, 350)
        self.setMinimumSize(206, 197)
        self.setWindowFlags(self.windowFlags() | Qt.Window)
        self.windowEffect.addShadowEffect(int(self.winId()))
        self.albumCoverLabel.setScaledContents(True)
        self.progressBar.installEventFilter(self)
        self.__setQss()
        # 信号连接到槽
        self.aniGroup.finished.connect(self.__switchSongInfoCard)
        self.lastSongButton.clicked.connect(self.lastSongSig)
        self.nextSongButton.clicked.connect(self.nextSongSig)
        self.playButton.clicked.connect(self.togglePlayStateSig)
        self.exitSmallestModeButton.clicked.connect(
            self.exitSmallestPlayInterfaceSig)
        self.blurCoverThread.blurDone.connect(self.albumCoverLabel.setPixmap)

    def __createSongInfoCards(self):
        """ 创建歌曲信息卡 """
        # 创建三个歌曲信息卡，分别为last, current, next
        self.songInfoCard_list = [SongInfoCard(
            parent=self) for i in range(3)]
        # 引用当前歌曲卡
        self.lastSongInfoCard = self.songInfoCard_list[0]  # type:SongInfoCard
        self.curSongInfoCard = self.songInfoCard_list[1]  # type:SongInfoCard
        self.nextSongInfoCard = self.songInfoCard_list[2]  # type:SongInfoCard
        # 创建动画
        self.songInfoCardAni_list = [
            QPropertyAnimation(self.songInfoCard_list[i], b"geometry") for i in range(3)
        ]
        self.lastSongInfoCardAni = self.songInfoCardAni_list[0]
        self.curSongInfoCardAni = self.songInfoCardAni_list[1]
        self.nextSongInfoCardAni = self.songInfoCardAni_list[2]
        # 将动画添加到动画组中
        for ani in self.songInfoCardAni_list:
            self.aniGroup.addAnimation(ani)
        # 初始化歌曲卡
        for i in range(3):
            self.songInfoCard_list[i].move(
                (i - 1) * self.width(), self.height() - 106)
        if self.playlist:
            self.curSongInfoCard.updateCard(self.playlist[0])
            if len(self.playlist) >= 2:
                self.nextSongInfoCard.updateCard(self.playlist[1])

    def startBlurThread(self, albumCoverPath: str):
        """ 开启磨砂线程 """
        self.blurCoverThread.setTargetCover(albumCoverPath, 40, (350, 350))
        self.blurCoverThread.start()

    def resizeEvent(self, e):
        """ 改变窗口大小时调整按钮位置和标签宽度 """
        self.resize(self.size())
        self.albumCoverLabel.resize(self.size())
        self.progressBar.resize(self.width(), 5)
        self.progressBar.move(0, self.height() - 5)
        self.titleBar.resize(self.width(), self.titleBar.height())
        self.exitSmallestModeButton.move(
            self.width() - 7 - self.exitSmallestModeButton.width(),
            self.height() - 7 - self.exitSmallestModeButton.height(),
        )
        self.playButton.move(
            int(self.width() / 2 - self.playButton.width() / 2),
            int(self.height() / 2 - self.playButton.height() / 2),
        )
        self.lastSongButton.move(self.playButton.x() - 75, self.playButton.y())
        self.nextSongButton.move(self.playButton.x() + 75, self.playButton.y())
        # 所有歌曲信息卡设置位置
        for i in range(3):
            self.songInfoCard_list[i].resize(
                self.width(), self.songInfoCard_list[i].height())
        self.curSongInfoCard.move(0, self.height() - 106)
        self.lastSongInfoCard.move(-self.width(), self.height() - 106)
        self.nextSongInfoCard.move(self.width(), self.height() - 106)
        # 高度太小时隐藏歌曲信息卡
        if self.height() <= 320:
            if self.curSongInfoCard.isVisible():
                self.curSongInfoCard.aniHide()
            self.lastSongInfoCard.hide()
            self.nextSongInfoCard.hide()
        elif self.height() > 320:
            if not self.curSongInfoCard.isVisible():
                self.curSongInfoCard.aniShow()
            else:
                self.curSongInfoCard.show()
            self.lastSongInfoCard.show()
            self.nextSongInfoCard.show()

    def __setQss(self):
        """ 设置层叠样式 """
        with open(r"app\resource\css\smallest_play_interface.qss", encoding="utf-8") as f:
            self.setStyleSheet(f.read())

    def eventFilter(self, obj, e: QEvent):
        """ 过滤事件 """
        if obj == self.progressBar:
            if e.type() in [QEvent.MouseButtonPress, QEvent.MouseButtonDblClick]:
                return True
        return super().eventFilter(obj, e)

    def __cycleLeftShift(self):
        """ 循环左移 """
        self.loopMode = self.CYCLE_LEFT_SHIFT
        self.__setAnimation(
            self.curSongInfoCardAni, self.curSongInfoCard, -self.width())
        self.__setAnimation(self.nextSongInfoCardAni, self.nextSongInfoCard, 0)
        self.aniGroup.removeAnimation(self.lastSongInfoCardAni)
        self.aniGroup.start()

    def __cycleRightShift(self):
        """ 循环右移 """
        self.loopMode = self.CYCLE_RIGHT_SHIFT
        self.__setAnimation(self.curSongInfoCardAni,
                            self.curSongInfoCard, self.width())
        self.__setAnimation(self.lastSongInfoCardAni, self.lastSongInfoCard, 0)
        self.aniGroup.removeAnimation(self.nextSongInfoCardAni)
        self.aniGroup.start()

    def __setAnimation(self, animation: QPropertyAnimation, songInfoCard, endX):
        """ 设置动画 """
        animation.setEasingCurve(QEasingCurve.OutQuart)
        animation.setTargetObject(songInfoCard)
        animation.setDuration(500)
        # 设置起始值
        animation.setStartValue(
            QRect(
                songInfoCard.x(),
                songInfoCard.y(),
                songInfoCard.width(),
                songInfoCard.height(),
            )
        )
        # 设置结束值
        animation.setEndValue(
            QRect(endX, songInfoCard.y(),
                  songInfoCard.width(), songInfoCard.height()))

    def __switchSongInfoCard(self):
        """ 交换对底层歌曲卡对象的引用 """
        # 循环左移
        if self.loopMode == self.CYCLE_LEFT_SHIFT:
            self.__resetRef(moveDirection=0)
            # 更新动画组
            self.aniGroup.addAnimation(self.lastSongInfoCardAni)
            # 移动底层对象
            self.songInfoCard_list[[2, 0, 1][self.shiftLeftTime]].move(
                self.width(), self.height() - 106
            )
            # 更新下标
            self.currentIndex += 1
            if self.currentIndex != len(self.playlist) - 1:
                # 更新歌曲信息卡
                self.updateCards()
        # 循环右移
        elif self.loopMode == self.CYCLE_RIGHT_SHIFT:
            self.__resetRef(moveDirection=1)
            # 更新动画组
            self.aniGroup.addAnimation(self.nextSongInfoCardAni)
            # 移动底层对象
            self.songInfoCard_list[[0, 2, 1][self.shiftRightTime]].move(
                -self.width(), self.height() - 106
            )
            # 更新下标
            self.currentIndex -= 1
            if self.currentIndex != 0:
                self.updateCards()
        # 完成未完成的移位动作
        if self.__unCompleteShift_list:
            index = self.__unCompleteShift_list.pop(0)
            self.__completeShift(index)

    def updateCards(self):
        """ 更新三个歌曲信息卡 """
        self.curSongInfoCard.updateCard(self.playlist[self.currentIndex])
        if self.currentIndex >= 1:
            self.lastSongInfoCard.updateCard(
                self.playlist[self.currentIndex - 1])
        if self.currentIndex <= len(self.playlist) - 2:
            self.nextSongInfoCard.updateCard(
                self.playlist[self.currentIndex + 1])

    def __resetRef(self, moveDirection=0):
        """ 设置变量对底层对象的引用，moveDirection = 0 代表左移，moveDirection = 1 代表右移 """
        # 循环左移
        if moveDirection == 0:
            self.shiftLeftTime = (self.shiftLeftTime + 1) % 3
            self.shiftRightTime = (self.shiftRightTime - 1) % 3
            if self.shiftLeftTime == 0:
                self.__resetRefIndex(0, 1, 2)
            elif self.shiftLeftTime == 1:
                self.__resetRefIndex(1, 2, 0)
            elif self.shiftLeftTime == 2:
                self.__resetRefIndex(2, 0, 1)
        # 循环右移
        elif moveDirection == 1:
            self.shiftLeftTime = (self.shiftLeftTime - 1) % 3
            self.shiftRightTime = (self.shiftRightTime + 1) % 3
            if self.shiftRightTime == 0:
                self.__resetRefIndex(0, 1, 2)
            elif self.shiftRightTime == 1:
                self.__resetRefIndex(2, 0, 1)
            elif self.shiftRightTime == 2:
                self.__resetRefIndex(1, 2, 0)

    def __resetRefIndex(self, lastIndex, curIndex, nextIndex):
        """ refsetFunc的子函数 """
        self.curSongInfoCard = self.songInfoCard_list[curIndex]
        self.lastSongInfoCard = self.songInfoCard_list[lastIndex]
        self.nextSongInfoCard = self.songInfoCard_list[nextIndex]

    def updateOneSongInfo(self, newSongInfo: dict):
        """ 更新播放列表中一首歌曲的信息 """
        for i, songInfo in enumerate(self.playlist):
            if songInfo["songPath"] == newSongInfo["songPath"]:
                self.playlist[i] = newSongInfo

    def updateMultiSongInfo(self, newSongInfo_list: list):
        """ 更新播放列表中多首歌曲的信息 """
        for newSongInfo in newSongInfo_list:
            self.updateOneSongInfo(newSongInfo)

    def setCurrentIndex(self, index):
        """ 更新当前下标并移动和更新歌曲信息卡 """
        if not self.playlist:
            return
        # 新的下标大于当前下标时，歌曲卡左移
        if self.aniGroup.state() != QAbstractAnimation.Running:
            songInfo = self.playlist[index]  # type:dict
            name = songInfo.get('coverName', '未知歌手_未知专辑')
            self.startBlurThread(getCoverPath(name, "album_big"))
            self.__completeShift(index)
        else:
            self.__unCompleteShift_list.append(index)

    def setPlaylist(self, playlist: list, isResetIndex: bool = True):
        """ 更新播放列表

        Parameters
        ----------
        playlist: list
            播放列表

        isResetIndex: bool
            是否从头播放歌曲
        """
        self.playlist = deepcopy(playlist) if playlist else []
        self.currentIndex = 0 if isResetIndex else self.currentIndex
        if playlist:
            self.curSongInfoCard.updateCard(self.playlist[0])
            self.curSongInfoCard.show()
            if len(self.playlist) > 1:
                self.nextSongInfoCard.updateCard(self.playlist[1])
        else:
            self.curSongInfoCard.hide()

    def setPlay(self, isPlay: bool):
        """ 设置播放状态 """
        self.playButton.setPlay(isPlay)

    def clearPlaylist(self):
        """ 清空播放列表 """
        self.playlist = []

    def __completeShift(self, index):
        """ 完成移位，只在调用setCurrentIndex时调用 """
        if index > self.currentIndex:
            self.currentIndex = index - 1
            self.nextSongInfoCard.updateCard(self.playlist[index])
            self.__cycleLeftShift()
        elif index < self.currentIndex:
            self.currentIndex = index + 1
            self.lastSongInfoCard.updateCard(self.playlist[index])
            self.__cycleRightShift()


class SongInfoCard(QWidget):
    """ 歌曲信息卡 """

    def __init__(self, songInfo: dict = None, parent=None):
        super().__init__(parent)
        self.resize(320, 55)
        # 创建小部件
        self.songNameLabel = QLabel(self)
        self.singerNameLabel = QLabel(self)
        self.opacityEffect = QGraphicsOpacityEffect(self)
        self.ani = QPropertyAnimation(self.opacityEffect, b"opacity")
        # 初始化
        self.__initWidget()
        # 设置窗口信息
        self.updateCard(songInfo)

    def __initWidget(self):
        """ 初始化小部件 """
        self.setFixedHeight(55)
        self.opacityEffect.setOpacity(1)
        self.setGraphicsEffect(self.opacityEffect)
        self.setAttribute(Qt.WA_TranslucentBackground)
        self.songNameLabel.setObjectName("songNameLabel")
        self.singerNameLabel.setObjectName("singerNameLabel")

    def __setSongInfo(self, songInfo: dict):
        """ 设置标签信息 """
        if not songInfo:
            songInfo = {}
        self.songName = songInfo.get("songName", "未知歌曲")  # type:str
        self.singerName = songInfo.get("singer", "未知歌手")  # type:str
        self.songNameLabel.setText(self.songName)
        self.singerNameLabel.setText(self.singerName)

    def updateCard(self, songInfo: dict):
        """ 更新窗口 """
        self.__setSongInfo(songInfo)
        self.__adjustLabel()

    def __adjustLabel(self):
        """ 根据当前窗口的宽度设置标签文本和位置 """
        fontMetrics = QFontMetrics(QFont("Microsoft YaHei", 12, 75))
        # 字符串的最大宽度
        maxWidth = self.width() - 30
        songNameWidth, singerNameWidth = 0, 0
        # 调整歌名
        for index, char in enumerate(self.songName):
            if songNameWidth + fontMetrics.width(char) > maxWidth:
                self.songNameLabel.setText(self.songName[:index])
                break
            songNameWidth += fontMetrics.width(char)
        self.songNameLabel.setFixedWidth(songNameWidth)
        # 调整歌手名
        fontMetrics = QFontMetrics(QFont("Microsoft YaHei", 11))
        for index, char in enumerate(self.singerName):
            if singerNameWidth + fontMetrics.width(char) > maxWidth:
                self.singerNameLabel.setText(self.singerName[:index])
                break
            singerNameWidth += fontMetrics.width(char)
        self.singerNameLabel.setFixedWidth(singerNameWidth)
        # 调整标签位置
        self.songNameLabel.move(int(self.width() / 2 - songNameWidth / 2), 0)
        self.singerNameLabel.move(
            int(self.width() / 2 - singerNameWidth / 2), 30)

    def resizeEvent(self, e):
        """ 改变窗口大小时调整标签 """
        super().resizeEvent(e)
        self.__adjustLabel()

    def aniHide(self):
        """ 淡出 """
        self.ani.setStartValue(1)
        self.ani.setEndValue(0)
        self.ani.setDuration(150)
        self.ani.finished.connect(self.__hideAniSlot)
        self.ani.start()

    def aniShow(self):
        """ 淡入 """
        super().show()
        self.ani.setStartValue(0)
        self.ani.setEndValue(1)
        self.ani.setDuration(150)
        self.ani.start()

    def __hideAniSlot(self):
        """ 淡出动画完成的槽函数 """
        self.ani.disconnect()
        super().hide()
