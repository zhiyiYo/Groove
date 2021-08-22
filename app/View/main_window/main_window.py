# coding:utf-8
import json
import os
from copy import deepcopy
from random import shuffle
from time import time
from typing import Dict

from app.common.os_utils import moveToTrash
from app.components.dialog_box.create_playlist_dialog import \
    CreatePlaylistDialog
from app.components.dialog_box.message_dialog import MessageDialog
from app.components.frameless_window import FramelessWindow
from app.components.label_navigation_interface import LabelNavigationInterface
from app.components.media_player import MediaPlaylist, PlaylistType
from app.components.opacity_ani_stacked_widget import OpacityAniStackedWidget
from app.components.pop_up_ani_stacked_widget import PopUpAniStackedWidget
from app.components.state_tooltip import StateTooltip
from app.components.thumbnail_tool_bar import ThumbnailToolBar
from app.components.title_bar import TitleBar
from app.View.album_interface import AlbumInterface
from app.View.my_music_interface import MyMusicInterface
from app.View.navigation_interface import NavigationInterface
from app.View.play_bar import PlayBar
from app.View.playing_interface import PlayingInterface
from app.View.playlist_card_interface import PlaylistCardInterface
from app.View.playlist_interface import PlaylistInterface
from app.View.search_result_interface import SearchResultInterface
from app.View.setting_interface import SettingInterface
from app.View.singer_interface import SingerInterface
from app.View.smallest_play_interface import SmallestPlayInterface
from PyQt5.QtCore import QEasingCurve, QEvent, QSize, Qt, QTimer
from PyQt5.QtGui import QCloseEvent, QIcon
from PyQt5.QtMultimedia import QMediaPlayer, QMediaPlaylist
from PyQt5.QtWidgets import QAction, QApplication, QWidget
from PyQt5.QtWinExtras import QtWin
from system_hotkey import SystemHotkey


class MainWindow(FramelessWindow):
    """ 主窗口 """

    def __init__(self, parent=None):
        super().__init__(parent)
        # 实例化小部件
        self.createWidgets()
        # 初始化标志位
        self.isInSelectionMode = False
        # 初始化导航历史
        self.navigationHistories = [("myMusicInterfaceStackWidget", 0)]
        # 初始化界面
        self.__initWidget()

    def createWidgets(self):
        """ 创建小部件 """
        # 主界面放置 totalStackWidget、playBar 和 titleBar
        # totalStackWidget用来放置 subMainWindow 和 playingInterface
        self.totalStackWidget = OpacityAniStackedWidget(self)

        # subMainWindow 用来放置堆叠窗口 subStackWidget
        self.subMainWindow = QWidget(self)
        self.titleBar = TitleBar(self)

        # 创建播放器和播放列表
        self.player = QMediaPlayer(self)
        self.mediaPlaylist = MediaPlaylist(self)

        # subStackWidget用来放置myMusicInterface、albumInterface、settingInterface、
        # playlistCardInterface等需要在导航栏右边显示的窗口
        self.subStackWidget = PopUpAniStackedWidget(self.subMainWindow)

        # 创建设置界面
        self.settingInterface = SettingInterface(self.subMainWindow)

        # 从配置文件中的选择文件夹读取音频文件
        t3 = time()
        self.myMusicInterface = MyMusicInterface(
            self.settingInterface.getConfig("selected-folders", []), self.subMainWindow)
        t4 = time()
        print("创建整个我的音乐界面耗时：".ljust(15), t4 - t3)

        # 创建定时扫描歌曲信息的定时器
        self.rescanSongInfoTimer = QTimer(self)

        # 创建缩略图任务栏
        QtWin.enableBlurBehindWindow(self)
        self.thumbnailToolBar = ThumbnailToolBar(self)
        self.thumbnailToolBar.setWindow(self.windowHandle())

        # 创建播放栏
        bgColor = self.settingInterface.getConfig(
            'playBar-background-color', [34, 92, 127])
        self.playBar = PlayBar(self.mediaPlaylist.lastSongInfo, bgColor, self)

        # 创建正在播放界面
        self.playingInterface = PlayingInterface(
            self.mediaPlaylist.playlist, self)

        # 创建专辑界面
        self.albumInterface = AlbumInterface(parent=self.subMainWindow)

        # 创建歌手界面
        self.singerInterface = SingerInterface(parent=self.subMainWindow)

        # 创建播放列表卡界面和播放列表界面
        self.playlistInterface = PlaylistInterface({}, self.subMainWindow)
        self.playlistCardInterface = PlaylistCardInterface(
            self.readCustomPlaylists(), self)

        # 创建导航界面
        self.navigationInterface = NavigationInterface(self.subMainWindow)

        # 创建标签导航界面
        self.labelNavigationInterface = LabelNavigationInterface(
            self.subMainWindow)

        # 创建最小播放界面
        self.smallestPlayInterface = SmallestPlayInterface(
            self.mediaPlaylist.playlist, parent=self)

        # 创建搜索结果界面
        pageSize = self.settingInterface.config.get(
            'online-music-page-size', 10)
        quality = self.settingInterface.config.get(
            'online-play-quality', '流畅音质')
        folder = self.settingInterface.config.get(
            'download-folder', 'app/download')
        self.searchResultInterface = SearchResultInterface(
            pageSize, quality, folder, self.subMainWindow)

        # 创建快捷键
        self.togglePlayPauseAct_1 = QAction(
            parent=self, shortcut=Qt.Key_Space, triggered=self.togglePlayState)
        self.showNormalAct = QAction(
            parent=self, shortcut=Qt.Key_Escape, triggered=self.exitFullScreen)
        self.lastSongAct = QAction(
            parent=self, shortcut=Qt.Key_MediaPrevious, triggered=self.mediaPlaylist.previous,)
        self.nextSongAct = QAction(
            parent=self, shortcut=Qt.Key_MediaNext, triggered=self.mediaPlaylist.next)
        self.togglePlayPauseAct_2 = QAction(
            parent=self, shortcut=Qt.Key_MediaPlay, triggered=self.togglePlayState)
        self.addActions(
            [
                self.togglePlayPauseAct_1,
                self.showNormalAct,
                self.nextSongAct,
                self.lastSongAct,
                self.togglePlayPauseAct_2,
            ]
        )

    def __initWidget(self):
        """ 初始化小部件 """
        self.resize(1240, 970)
        self.setMinimumSize(1030, 800)
        self.setWindowTitle("Groove 音乐")
        self.setWindowIcon(QIcon("app/resource/images/logo.png"))
        self.setAttribute(Qt.WA_TranslucentBackground | Qt.WA_StyledBackground)
        # 在去除任务栏的显示区域居中显示
        desktop = QApplication.desktop().availableGeometry()
        self.move(desktop.width()//2 - self.width()//2,
                  desktop.height()//2 - self.height()//2)
        self.smallestPlayInterface.move(desktop.width() - 390, 40)
        # 标题栏置顶
        self.titleBar.raise_()
        # 设置窗口特效
        self.setWindowEffect()
        # 将窗口添加到 StackWidget 中
        self.subStackWidget.addWidget(self.myMusicInterface, 0, 70)
        self.subStackWidget.addWidget(self.playlistCardInterface, 0, 120)
        self.subStackWidget.addWidget(self.settingInterface, 0, 120)
        self.subStackWidget.addWidget(self.albumInterface, 0, 70)
        self.subStackWidget.addWidget(self.singerInterface, 0, 70)
        self.subStackWidget.addWidget(self.playlistInterface, 0, 70)
        self.subStackWidget.addWidget(self.labelNavigationInterface, 0, 100)
        self.subStackWidget.addWidget(self.searchResultInterface, 0, 120)
        self.totalStackWidget.addWidget(self.subMainWindow)
        self.totalStackWidget.addWidget(self.playingInterface)
        # 设置右边子窗口的位置
        self.adjustWidgetGeometry()
        # 引用小部件
        self.referenceWidgets()
        # 设置层叠样式
        self.setObjectName("mainWindow")
        self.subMainWindow.setObjectName("subMainWindow")
        self.subStackWidget.setObjectName("subStackWidget")
        self.playingInterface.setObjectName("playingInterface")
        self.setQss()
        # 设置定时器溢出时间
        self.rescanSongInfoTimer.setInterval(180000)
        # 初始化播放列表
        self.initPlaylist()
        # todo:设置全局热键
        # self.setHotKey()
        # 将信号连接到槽函数
        self.connectSignalToSlot()
        # 初始化播放栏
        self.initPlayBar()
        # 安装事件过滤器
        self.navigationInterface.navigationMenu.installEventFilter(self)
        self.rescanSongInfoTimer.start()

    def setHotKey(self):
        """ 设置全局热键 """
        self.nextSongHotKey = SystemHotkey()
        self.lastSongHotKey = SystemHotkey()
        self.playHotKey = SystemHotkey()
        # callback会返回一个event参数，所以需要用lambda
        self.nextSongHotKey.register(
            ("f6",), callback=lambda x: self.mediaPlaylist.next)
        self.lastSongHotKey.register(
            ("f4",), callback=lambda x: self.hotKeySlot(self.mediaPlaylist.previous))
        self.playHotKey.register(
            ("f5",), callback=lambda x: self.togglePlayState)

    def setWindowEffect(self):
        """ 设置窗口特效 """
        # 开启窗口动画
        self.windowEffect.addWindowAnimation(self.winId())
        # 开启亚克力效果和阴影效果
        self.windowEffect.setAcrylicEffect(self.winId(), "FFFFFFCC", True)

    def adjustWidgetGeometry(self):
        """ 调整小部件的geometry """
        self.subMainWindow.resize(self.size())
        self.totalStackWidget.resize(self.size())
        self.titleBar.resize(self.width(), 40)
        self.playBar.resize(self.width(), self.playBar.height())
        self.playBar.move(0, self.height()-self.playBar.height())

        if hasattr(self, "navigationInterface"):
            self.navigationInterface.setOverlay(self.width() < 1280)
            self.subStackWidget.move(self.navigationInterface.width(), 0)
            self.subStackWidget.resize(
                self.width() - self.navigationInterface.width(), self.height())
            self.navigationInterface.resize(
                self.navigationInterface.width(), self.height())

    def eventFilter(self, obj, e: QEvent):
        """ 过滤事件 """
        if obj == self.navigationInterface.navigationMenu:
            # 显示导航菜单是更改标题栏返回按钮和标题的父级为导航菜单
            isVisible = self.titleBar.returnBt.isVisible()
            if e.type() == QEvent.Show:
                self.titleBar.returnBt.setParent(obj)
                # 显示标题
                self.titleBar.title.setParent(obj)
                self.titleBar.title.move(15, 10)
                self.titleBar.title.show()
                # 如果播放栏可见就缩短导航菜单
                isScaled = self.playBar.isVisible()
                height = self.height() - isScaled * self.playBar.height()
                self.navigationInterface.navigationMenu.setBottomSpacingVisible(
                    not isScaled)
                self.navigationInterface.navigationMenu.resize(
                    self.navigationInterface.navigationMenu.width(), height)
            elif e.type() == QEvent.Hide:
                # 隐藏标题
                self.titleBar.title.setParent(self.titleBar)
                self.titleBar.returnBt.setParent(self.titleBar)
                self.titleBar.title.hide()
            # 根据情况显示/隐藏返回按钮和标题
            self.titleBar.returnBt.setVisible(isVisible)
        return super().eventFilter(obj, e)

    def resizeEvent(self, e):
        """ 调整尺寸时同时调整子窗口的尺寸 """
        super().resizeEvent(e)
        self.adjustWidgetGeometry()
        self.titleBar.maxBt.setMaxState(
            self._isWindowMaximized(int(self.winId())))

    def closeEvent(self, e: QCloseEvent):
        """ 关闭窗口前更新json文件 """
        config = {}
        config["volume"] = self.playBar.volumeSlider.value()
        config["playBar-background-color"] = self.playBar.backgroundColor
        self.settingInterface.updateConfig(config)
        self.mediaPlaylist.save()
        e.accept()

    def referenceWidgets(self):
        """ 引用小部件 """
        self.songTabSongListWidget = self.myMusicInterface.songListWidget
        self.albumCardInterface = self.myMusicInterface.albumCardInterface

    def onNavigationDisplayModeChanged(self, disPlayMode: int):
        """ 导航界面显示模式改变对应的槽函数 """
        self.titleBar.title.setVisible(self.navigationInterface.isExpanded)
        self.adjustWidgetGeometry()
        self.navigationInterface.navigationMenu.stackUnder(self.playBar)
        # 如果现在显示的是字母导航界面就将其隐藏
        if self.subStackWidget.currentWidget() is self.labelNavigationInterface:
            self.subStackWidget.setCurrentIndex(0)

    def initPlaylist(self):
        """ 初始化播放列表 """
        self.player.setPlaylist(self.mediaPlaylist)

        # 如果没有上一次的播放列表数据，就设置默认的播放列表
        if not self.mediaPlaylist.playlist:
            songInfo_list = self.songTabSongListWidget.songInfo_list
            self.playingInterface.setPlaylist(songInfo_list)
            self.smallestPlayInterface.setPlaylist(songInfo_list)
            self.mediaPlaylist.setPlaylist(songInfo_list)
            self.mediaPlaylist.playlistType = PlaylistType.ALL_SONG_PLAYLIST

        # 将当前歌曲设置为上次关闭前播放的歌曲
        if self.mediaPlaylist.lastSongInfo in self.mediaPlaylist.playlist:
            index = self.mediaPlaylist.playlist.index(
                self.mediaPlaylist.lastSongInfo)
            self.mediaPlaylist.setCurrentIndex(index)
            self.playingInterface.setCurrentIndex(index)
            self.smallestPlayInterface.setCurrentIndex(index)
            index = self.songTabSongListWidget.index(
                self.mediaPlaylist.lastSongInfo)
            if index is not None:
                self.songTabSongListWidget.setPlay(index)

    def togglePlayState(self):
        """ 播放按钮按下时根据播放器的状态来决定是暂停还是播放 """
        if self.player.state() == QMediaPlayer.PlayingState:
            self.player.pause()
            self.setPlayButtonState(False)
            self.thumbnailToolBar.setButtonsEnabled(True)
        else:
            self.play()

    def setPlayButtonState(self, isPlay: bool):
        """ 设置播放按钮状态 """
        self.playBar.setPlay(isPlay)
        self.playingInterface.setPlay(isPlay)
        self.thumbnailToolBar.setPlay(isPlay)
        self.smallestPlayInterface.setPlay(isPlay)

    def onVolumeChanged(self, volume: int):
        """ 音量滑动条数值改变时更换图标并设置音量 """
        self.player.setVolume(volume)
        if self.sender() is self.playBar:
            self.playingInterface.setVolume(volume)
        elif self.sender() is self.playingInterface:
            self.playBar.setVolume(volume)

    def onPlayerPositionChanged(self, position):
        """ 播放器的播放进度改变时更新当前播放进度标签和进度条的值 """
        self.playBar.setCurrentTime(position)
        self.playBar.progressSlider.setValue(position)
        self.playingInterface.playBar.setCurrentTime(position)
        self.playingInterface.playBar.progressSlider.setValue(position)
        self.smallestPlayInterface.progressBar.setValue(position)

    def onPlayerDurationChanged(self):
        """ 播放器当前播放的歌曲变化时更新进度条的范围和总时长标签 """
        # 刚切换时得到的时长为0，所以需要先判断一下
        duration = self.player.duration()
        if duration < 1:
            return
        self.playBar.setTotalTime(duration)
        self.playBar.progressSlider.setRange(0, duration)
        self.playingInterface.playBar.setTotalTime(duration)
        self.playingInterface.playBar.progressSlider.setRange(0, duration)
        self.smallestPlayInterface.progressBar.setRange(0, duration)

    def onprogressSliderMoved(self, position):
        """ 手动拖动进度条时改变当前播放进度标签和播放器的值 """
        self.player.setPosition(position)
        self.playBar.setCurrentTime(position)
        self.playingInterface.setCurrentTime(position)
        self.smallestPlayInterface.progressBar.setValue(position)

    def onSongCardNextPlay(self, songInfo: dict):
        """ 下一首播放动作触发对应的槽函数 """
        # 直接更新正在播放界面的播放列表
        index = self.mediaPlaylist.currentIndex()
        newPlaylist = (
            self.mediaPlaylist.playlist[: index + 1]
            + [songInfo]
            + self.mediaPlaylist.playlist[index + 1:]
        )
        self.playingInterface.setPlaylist(newPlaylist, False)
        self.smallestPlayInterface.setPlaylist(newPlaylist, False)
        self.playingInterface.setCurrentIndex(
            self.mediaPlaylist.currentIndex())
        self.mediaPlaylist.insertMedia(
            self.mediaPlaylist.currentIndex() + 1, songInfo)

    def onSongTabSongCardPlay(self, songInfo: dict):
        """ 歌曲界面歌曲卡的播放按钮按下或者双击歌曲卡时播放这首歌 """
        songInfo_list = self.songTabSongListWidget.songInfo_list

        # 如果当前播放列表模式不是歌曲文件夹的所有歌曲或者指定的歌曲不在播放列表中就刷新播放列表
        if self.mediaPlaylist.playlistType != PlaylistType.ALL_SONG_PLAYLIST \
                or songInfo_list != self.mediaPlaylist.playlist:
            self.mediaPlaylist.playlistType = PlaylistType.ALL_SONG_PLAYLIST
            songInfo_list = self.songTabSongListWidget.songInfo_list
            index = songInfo_list.index(songInfo)
            playlist = songInfo_list[index:] + songInfo_list[:index]
            self.setPlaylist(playlist)

        # 将播放列表的当前歌曲设置为指定的歌曲
        self.mediaPlaylist.setCurrentSong(songInfo)

    def playOneSongCard(self, songInfo: dict):
        """ 将播放列表重置为一首歌 """
        self.mediaPlaylist.playlistType = PlaylistType.SONG_CARD_PLAYLIST
        self.setPlaylist([songInfo])

    def switchLoopMode(self, loopMode):
        """ 根据随机播放按钮的状态和循环模式的状态决定播放器的播放模式 """
        # 记录按下随机播放前的循环模式
        self.mediaPlaylist.prePlayMode = loopMode

        # 更新按钮样式
        if self.sender() == self.playBar:
            self.playingInterface.setLoopMode(loopMode)
        elif self.sender() == self.playingInterface:
            self.playBar.loopModeButton.setLoopMode(loopMode)
        if not self.mediaPlaylist.randPlayBtPressed:
            # 随机播放按钮没按下时，直接设置播放模式为循环模式按钮的状态
            self.mediaPlaylist.setPlaybackMode(loopMode)
        else:
            # 随机播放按钮按下时，如果选了单曲循环就直接设置为单曲循环，否则设置为随机播放
            if self.playBar.loopModeButton.loopMode == QMediaPlaylist.CurrentItemInLoop:
                self.mediaPlaylist.setPlaybackMode(
                    QMediaPlaylist.CurrentItemInLoop)
            else:
                self.mediaPlaylist.setPlaybackMode(QMediaPlaylist.Random)

    def setRandomPlay(self, isRandomPlay: bool):
        """ 选择随机播放模式 """
        self.mediaPlaylist.setRandomPlay(isRandomPlay)
        self.playingInterface.setRandomPlay(isRandomPlay)
        self.playBar.randomPlayButton.setRandomPlay(isRandomPlay)

    def updateWindow(self, index: int):
        """ 切换歌曲时更新歌曲卡、播放栏和最小化播放窗口 """
        songInfo = self.mediaPlaylist.playlist[index]

        # 更新正在播放界面、播放栏、专辑界面、播放列表界面、搜索界面和最小播放界面
        self.playBar.updateSongInfoCard(songInfo)
        self.playingInterface.setCurrentIndex(index)

        if self.smallestPlayInterface.isVisible():
            self.smallestPlayInterface.setCurrentIndex(index)

        if songInfo in self.albumInterface.songInfo_list:
            i = self.albumInterface.songListWidget.index(songInfo)
            self.albumInterface.songListWidget.setPlay(i)
        elif self.albumInterface.songListWidget.playingIndex is not None:
            self.albumInterface.songListWidget.cancelPlayState()

        if songInfo in self.playlistInterface.songInfo_list:
            i = self.playlistInterface.songListWidget.index(songInfo)
            self.playlistInterface.songListWidget.setPlay(i)
        elif self.playlistInterface.songListWidget.playingIndex is not None:
            self.playlistInterface.songListWidget.cancelPlayState()

        if songInfo in self.searchResultInterface.localSongListWidget.songInfo_list:
            i = self.searchResultInterface.localSongListWidget.index(songInfo)
            self.searchResultInterface.localSongListWidget.setPlay(i)
        elif self.searchResultInterface.localSongListWidget.playingIndex is not None:
            self.searchResultInterface.localSongListWidget.cancelPlayState()

        if songInfo in self.searchResultInterface.onlineSongListWidget.songInfo_list:
            i = self.searchResultInterface.onlineSongListWidget.index(songInfo)
            self.searchResultInterface.onlineSongListWidget.setPlay(i)
        elif self.searchResultInterface.onlineSongListWidget.playingIndex is not None:
            self.searchResultInterface.onlineSongListWidget.cancelPlayState()

        index = self.songTabSongListWidget.index(songInfo)
        if index is not None:
            self.songTabSongListWidget.setPlay(index)
        else:
            self.songTabSongListWidget.cancelPlayState()

    def playAlbum(self, playlist: list, index=0):
        """ 播放专辑中的歌曲 """
        self.playingInterface.setPlaylist(playlist, index=index)
        self.smallestPlayInterface.setPlaylist(playlist)
        self.mediaPlaylist.playAlbum(playlist, index)
        self.play()

    def onMultiSongsNextPlay(self, songInfo_list: list):
        """ 多首歌下一首播放动作触发对应的槽函数 """
        index = self.mediaPlaylist.currentIndex()
        newPlaylist = (
            self.mediaPlaylist.playlist[: index + 1]
            + songInfo_list
            + self.mediaPlaylist.playlist[index + 1:]
        )
        self.playingInterface.setPlaylist(newPlaylist, False)
        self.smallestPlayInterface.setPlaylist(newPlaylist, False)
        self.playingInterface.setCurrentIndex(
            self.mediaPlaylist.currentIndex())
        # insertMedia的时候自动更新playlist列表，所以不必手动更新列表
        self.mediaPlaylist.insertMedias(
            self.mediaPlaylist.currentIndex() + 1, songInfo_list)

    def disorderPlayAll(self):
        """ 无序播放所有 """
        self.mediaPlaylist.playlistType = PlaylistType.ALL_SONG_PLAYLIST
        newPlaylist = deepcopy(self.songTabSongListWidget.songInfo_list)
        shuffle(newPlaylist)
        self.setPlaylist(newPlaylist)

    def play(self):
        """ 播放歌曲并改变按钮样式 """
        self.player.play()
        self.setPlayButtonState(True)
        # 显示被隐藏的歌曲信息卡
        if self.mediaPlaylist.playlist and self.playBar.songInfoCard.isHidden() and self.playBar.isVisible():
            self.playBar.songInfoCard.show()
            self.playBar.songInfoCard.updateSongInfoCard(
                self.mediaPlaylist.playlist[0])

    def initPlayBar(self):
        """ 从配置文件中读取配置数据来初始化播放栏 """
        # 初始化音量
        volume = self.settingInterface.getConfig("volume", 20)
        self.playingInterface.setVolume(volume)

        # 初始化歌曲卡信息
        if self.mediaPlaylist.playlist:
            self.playBar.updateSongInfoCard(
                self.mediaPlaylist.getCurrentSong())

    def showPlayingInterface(self):
        """ 显示正在播放界面 """
        if self.playingInterface.isVisible():
            return

        # 先退出选择模式
        self.exitSelectionMode()
        self.playBar.hide()
        self.titleBar.title.hide()
        self.titleBar.returnBt.show()
        if not self.playingInterface.isPlaylistVisible:
            self.playingInterface.songInfoCardChute.move(
                0, -self.playingInterface.playBar.height() + 68)
            self.playingInterface.playBar.show()
        self.totalStackWidget.setCurrentIndex(1)
        self.titleBar.setWhiteIcon(True)

        # 增加导航历史
        self.navigationHistories.append(("totalStackWidget", 1))

    def hidePlayingInterface(self):
        """ 隐藏正在播放界面 """
        if not self.playingInterface.isVisible():
            return

        self.playBar.show()
        self.totalStackWidget.setCurrentIndex(0)

        # 根据当前界面设置标题栏按钮颜色
        whiteInterface = [self.albumInterface,
                          self.playlistInterface, self.singerInterface]
        if self.subStackWidget.currentWidget() in whiteInterface:
            self.titleBar.returnBt.setWhiteIcon(False)
        else:
            self.titleBar.setWhiteIcon(False)

        # 隐藏返回按钮
        cond = self.subStackWidget.currentWidget() not in [
            self.albumInterface, self.labelNavigationInterface]
        if len(self.navigationHistories) == 1 and cond:
            self.titleBar.returnBt.hide()

        self.titleBar.title.setVisible(self.navigationInterface.isExpanded)

    def setQss(self):
        """ 设置层叠样式 """
        with open(r"app\resource\css\main_window.qss", encoding="utf-8") as f:
            self.setStyleSheet(f.read())

    def onPlayingInterfaceCurrentIndexChanged(self, index):
        """ 正在播放界面下标变化槽函数 """
        self.mediaPlaylist.setCurrentIndex(index)
        self.play()

    def setMute(self, isMute: bool):
        """ 设置静音 """
        self.player.setMuted(isMute)
        self.playingInterface.setMute(isMute)
        self.playBar.setMute(isMute)

    def setFullScreen(self, isFullScreen: bool):
        """ 设置全屏 """
        if isFullScreen == self.isFullScreen():
            return
        if not isFullScreen:
            self.exitFullScreen()
        else:
            # 更新标题栏
            self.playBar.hide()
            self.titleBar.title.hide()
            self.titleBar.setWhiteIcon(True)
            self.titleBar.hide()
            # 切换到正在播放界面
            self.totalStackWidget.setCurrentIndex(1)
            self.showFullScreen()
            self.playingInterface.setFullScreen(True)
            if self.playingInterface.isPlaylistVisible:
                self.playingInterface.songInfoCardChute.move(
                    0, 258 - self.height())

    def exitFullScreen(self):
        """ 退出全屏 """
        if not self.isFullScreen():
            return
        self.showNormal()
        # 更新最大化按钮图标
        self.titleBar.maxBt.setMaxState(False)
        self.titleBar.returnBt.show()
        self.titleBar.show()
        self.playingInterface.playBar.FullScreenButton.setFullScreen(False)
        if self.playingInterface.isPlaylistVisible:
            self.playingInterface.songInfoCardChute.move(
                0, 258 - self.height())

    def showPlaylist(self):
        """ 显示正在播放界面的播放列表 """
        self.playingInterface.showPlaylist()
        # 直接设置播放栏上拉箭头按钮箭头方向朝下
        self.playingInterface.playBar.pullUpArrowButton.setArrowDirection(
            "down")
        if self.playingInterface.isPlaylistVisible:
            self.showPlayingInterface()

    def clearPlaylist(self):
        """ 清空播放列表 """
        self.mediaPlaylist.playlistType = PlaylistType.NO_PLAYLIST
        self.mediaPlaylist.clear()
        self.playingInterface.clearPlaylist()
        self.smallestPlayInterface.clearPlaylist()

    def addOneSongToPlayingPlaylist(self, songInfo: dict):
        """ 向正在播放列表尾部添加一首歌 """
        self.mediaPlaylist.addMedia(songInfo)
        self.playingInterface.setPlaylist(self.mediaPlaylist.playlist, False)
        self.smallestPlayInterface.setPlaylist(
            self.mediaPlaylist.playlist, False)

    def addSongsToPlayingPlaylist(self, songInfo_list: list):
        """ 向正在播放列表尾部添加多首歌 """
        self.mediaPlaylist.addMedias(songInfo_list)
        self.playingInterface.setPlaylist(self.mediaPlaylist.playlist, False)
        self.smallestPlayInterface.setPlaylist(
            self.mediaPlaylist.playlist, False)

    def switchToPlaylistInterface(self, playlistName: str):
        """ 切换到播放列表界面 """
        if self.isInSelectionMode:
            return

        playlist = self.playlistCardInterface.playlists[playlistName]

        # 显示返回按钮
        self.titleBar.returnBt.show()
        QApplication.processEvents()
        self.playlistInterface.updateWindow(playlist)
        self.subStackWidget.setCurrentWidget(
            self.playlistInterface, duration=300)
        self.totalStackWidget.setCurrentIndex(0)
        self.titleBar.setWhiteIcon(True)
        self.titleBar.returnBt.setWhiteIcon(False)
        self.playBar.show()

        # 增加导航历史
        index = self.subStackWidget.indexOf(self.playlistInterface)
        if self.navigationHistories[-1] != ("subStackWidget", index):
            self.navigationHistories.append(("subStackWidget", index))

        # 根据当前播放的歌曲设置歌曲卡播放状态
        songInfo = self.mediaPlaylist.getCurrentSong()
        if songInfo in self.playlistInterface.songInfo_list:
            index = self.playlistInterface.songInfo_list.index(songInfo)
            self.playlistInterface.songListWidget.setPlay(index)

    def switchToSingerInterface(self, singerName: str):
        """ 切换到专辑界面 """
        if self.isInSelectionMode:
            return
        if self.isFullScreen():
            self.exitFullScreen()

        singerInfo = self.myMusicInterface.findSingerInfo(singerName)
        if not singerInfo:
            return

        # 显示返回按钮
        self.titleBar.returnBt.show()
        QApplication.processEvents()
        self.singerInterface.updateWindow(singerInfo)
        self.subStackWidget.setCurrentWidget(
            self.singerInterface, duration=300)
        self.totalStackWidget.setCurrentIndex(0)
        self.singerInterface.albumBlurBackground.hide()
        self.titleBar.setWhiteIcon(True)
        self.titleBar.returnBt.setWhiteIcon(False)
        self.playBar.show()

        # 增加导航历史
        index = self.subStackWidget.indexOf(self.singerInterface)
        self.navigationHistories.append(("subStackWidget", index))

    def switchToAlbumInterface(self, albumName: str, singerName: str):
        """ 切换到专辑界面 """
        if self.isInSelectionMode:
            return
        if self.isFullScreen():
            self.exitFullScreen()

        albumInfo = self.albumCardInterface.findAlbumInfoByName(
            albumName, singerName)
        if not albumInfo:
            return

        # 显示返回按钮
        self.titleBar.returnBt.show()
        QApplication.processEvents()
        self.albumInterface.updateWindow(albumInfo)
        self.subStackWidget.setCurrentWidget(self.albumInterface, duration=300)
        self.totalStackWidget.setCurrentIndex(0)
        self.titleBar.setWhiteIcon(True)
        self.titleBar.returnBt.setWhiteIcon(False)
        self.playBar.show()

        # 增加导航历史
        index = self.subStackWidget.indexOf(self.albumInterface)
        self.navigationHistories.append(("subStackWidget", index))

        # 根据当前播放的歌曲设置歌曲卡播放状态
        songInfo = self.mediaPlaylist.getCurrentSong()
        if songInfo in self.albumInterface.songInfo_list:
            index = self.albumInterface.songInfo_list.index(songInfo)
            self.albumInterface.songListWidget.setPlay(index)

    def onAlbumInterfaceSongCardPlay(self, index):
        """ 专辑界面歌曲卡播放按钮按下时 """
        albumSongList = self.albumInterface.songInfo_list

        # 播放模式不为专辑播放模式或者播放列表不同时直接刷新播放列表
        if self.mediaPlaylist.playlistType != PlaylistType.ALBUM_CARD_PLAYLIST or \
                self.mediaPlaylist.playlist != albumSongList:
            self.playAlbum(albumSongList, index)

        self.mediaPlaylist.setCurrentIndex(index)

    def onPlaylistInterfaceSongCardPlay(self, index):
        """ 专辑界面歌曲卡播放按钮按下时 """
        playlistSongList = self.playlistInterface.songInfo_list

        # 播放模式不为自定义播放列表模式或者播放列表不同时直接刷新播放列表
        if self.mediaPlaylist.playlistType != PlaylistType.CUSTOM_PLAYLIST or \
                self.mediaPlaylist.playlist != playlistSongList:

            self.playCustomPlaylist(playlistSongList, index)

        self.mediaPlaylist.setCurrentIndex(index)

    def onReturnButtonClicked(self):
        """ 标题栏返回按钮的槽函数 """
        if self.isInSelectionMode:
            return

        # 隐藏音量条
        self.playingInterface.playBar.volumeSliderWidget.hide()
        self.navigationHistories.pop()

        # 如果上一个界面还是正在播放界面就直接将其弹出，因为不应该回退到正在播放界面
        if self.navigationHistories[-1] == ("totalStackWidget", 1):
            self.navigationHistories.pop()

        stackWidgetName, index = self.navigationHistories[-1]
        if stackWidgetName == "myMusicInterfaceStackWidget":
            self.myMusicInterface.stackedWidget.setCurrentIndex(index)
            self.subStackWidget.setCurrentIndex(
                0, True, False, 200, QEasingCurve.InCubic)
            self.navigationInterface.setCurrentIndex(0)
            self.myMusicInterface.setSelectedButton(index)
            self.titleBar.setWhiteIcon(False)
        elif stackWidgetName == "subStackWidget":
            isShowNextWidgetDirectly = self.subStackWidget.currentWidget() is not self.settingInterface
            self.subStackWidget.setCurrentIndex(
                index, True, isShowNextWidgetDirectly, 200, QEasingCurve.InCubic)
            self.navigationInterface.setCurrentIndex(index)

            # 更新标题栏图标颜色
            whiteIndexes = [self.subStackWidget.indexOf(
                i) for i in [self.playlistInterface, self.albumInterface, self.singerInterface]]
            self.titleBar.setWhiteIcon(index in whiteIndexes)
            self.titleBar.returnBt.setWhiteIcon(False)

        self.hidePlayingInterface()

        if len(self.navigationHistories) == 1:
            self.titleBar.returnBt.hide()

    def onMyMucicInterfaceStackWidgetIndexChanged(self, index):
        """ 堆叠窗口下标改变时的槽函数 """
        self.navigationHistories.append(("myMusicInterfaceStackWidget", index))
        self.titleBar.returnBt.show()

    def onEditSongInfo(self, oldSongInfo: dict, newSongInfo: dict):
        """ 编辑歌曲卡完成信号的槽函数 """
        self.mediaPlaylist.updateOneSongInfo(newSongInfo)
        self.playingInterface.updateOneSongCard(newSongInfo)
        self.playlistCardInterface.updateOneSongInfo(newSongInfo)
        self.smallestPlayInterface.updateOneSongInfo(newSongInfo)
        self.myMusicInterface.updateOneSongInfo(oldSongInfo, newSongInfo)
        self.albumCardInterface.updateOneSongInfo(oldSongInfo, newSongInfo)
        self.playlistInterface.updateOneSongCard(oldSongInfo, newSongInfo)

    def onEditAlbumInfo(self, oldAlbumInfo: dict, newAlbumInfo: dict, coverPath: str):
        """ 更新专辑卡及其对应的歌曲卡信息 """
        newSongInfo_list = newAlbumInfo["songInfo_list"]
        self.mediaPlaylist.updateMultiSongInfo(newSongInfo_list)
        self.playingInterface.updateMultiSongCards(newSongInfo_list)
        self.playlistInterface.updateMultiSongCards(newSongInfo_list)
        self.smallestPlayInterface.updateMultiSongInfo(newSongInfo_list)
        self.playlistCardInterface.updateMultiSongInfo(newSongInfo_list)
        self.songTabSongListWidget.updateMultiSongCards(newSongInfo_list)

        if self.sender() is self.albumInterface:
            self.albumCardInterface.updateOneAlbumInfo(
                oldAlbumInfo, newAlbumInfo, coverPath)
            self.myMusicInterface.singerInfoGetter.updateSingerInfos(
                self.albumCardInterface.albumInfo_list)
            if not self.albumInterface.songInfo_list:
                self.titleBar.returnBt.click()

        elif self.sender() is self.albumCardInterface:
            self.myMusicInterface.singerInfoGetter.updateSingerInfos(
                self.albumCardInterface.albumInfo_list)
            if oldAlbumInfo == self.albumInterface.albumInfo:
                self.albumInterface.albumInfoBar.updateWindow(newAlbumInfo)

        elif self.sender() is self.singerInterface:
            self.albumCardInterface.updateOneAlbumInfo(
                oldAlbumInfo, newAlbumInfo, coverPath)
            self.myMusicInterface.singerInfoGetter.updateSingerInfos(
                self.albumCardInterface.albumInfo_list)
            self.singerInterface.updateWindow(
                self.myMusicInterface.findSingerInfo(newAlbumInfo['singer']))

    def showSmallestPlayInterface(self):
        """ 切换到最小化播放模式 """
        self.smallestPlayInterface.setCurrentIndex(
            self.mediaPlaylist.currentIndex())
        self.hide()
        self.smallestPlayInterface.show()

    def exitSmallestPlayInterface(self):
        """ 退出最小播放模式 """
        self.smallestPlayInterface.hide()
        self.show()

    def onSelectionModeStateChanged(self, isOpenSelectionMode: bool):
        """ 进入/退出选择模式信号的槽函数 """
        self.isInSelectionMode = isOpenSelectionMode
        if self.sender() != self.playingInterface:
            self.playBar.setHidden(isOpenSelectionMode)

    def playCheckedCards(self, songInfo_list: list, index=0):
        """ 重置播放列表为所有选中的歌曲卡中的歌曲 """
        self.mediaPlaylist.playlistType = PlaylistType.CUSTOM_PLAYLIST
        self.setPlaylist(songInfo_list, index)

    def setPlaylist(self, playlist: list, index=0):
        """ 设置播放列表 """
        self.playingInterface.setPlaylist(playlist, index=index)
        self.mediaPlaylist.setPlaylist(playlist, index)
        self.smallestPlayInterface.setPlaylist(playlist)
        self.play()

    def switchToSettingInterface(self):
        """ 切换到设置界面 """
        # 先退出选择模式再切换界面
        self.exitSelectionMode()
        self.subStackWidget.setCurrentWidget(
            self.settingInterface, duration=300)

        # 更新标题栏
        self.titleBar.setWhiteIcon(False)
        self.titleBar.returnBt.show()

        # 增加导航历史
        index = self.subStackWidget.indexOf(self.settingInterface)
        self.navigationHistories.append(('subStackWidget', index))

    def switchToMyMusicInterface(self):
        """ 切换到我的音乐界面 """
        self.exitSelectionMode()
        self.subStackWidget.setCurrentWidget(self.myMusicInterface)

        # 更新标题栏
        self.titleBar.setWhiteIcon(False)
        self.titleBar.returnBt.show()

        # 增加导航历史
        index = self.subStackWidget.indexOf(self.myMusicInterface)
        self.navigationHistories.append(('subStackWidget', index))

    def switchToPlaylistCardInterface(self):
        """ 切换到播放列表卡界面 """
        self.exitSelectionMode()
        self.subStackWidget.setCurrentWidget(
            self.playlistCardInterface, duration=300)

        # 更新标题栏
        self.titleBar.setWhiteIcon(False)
        self.titleBar.returnBt.show()

        # 增加导航历史
        index = self.subStackWidget.indexOf(self.playlistCardInterface)
        self.navigationHistories.append(('subStackWidget', index))

    def exitSelectionMode(self):
        """ 退出选择模式 """
        if not self.isInSelectionMode:
            return
        self.myMusicInterface.exitSelectionMode()
        self.albumInterface.exitSelectionMode()
        self.playlistCardInterface.exitSelectionMode()
        self.playlistInterface.exitSelectionMode()
        self.playingInterface.exitSelectionMode()
        self.singerInterface.exitSelectionMode()

    @staticmethod
    def readCustomPlaylists():
        """ 读取自定义播放列表 """
        path = "app/Playlists"
        os.makedirs(path, exist_ok=True)

        customPlaylists = {}  # type:Dict[str, dict]
        playlistFiles = os.listdir(path)
        for playlistFile in playlistFiles:
            with open(os.path.join(path, playlistFile), encoding="utf-8") as f:
                playlist = json.load(f)  # type:dict
                name = playlist.get("playlistName", playlistFile[:-5])
                playlist["playlistName"] = name
                customPlaylists[name] = playlist
        return customPlaylists

    def showCreatePlaylistDialog(self, songInfo_list: list = None):
        """ 显示创建播放列表面板 """
        w = CreatePlaylistDialog(songInfo_list, self)
        w.createPlaylistSig.connect(self.onCreatePlaylist)
        w.exec_()

    def onCreatePlaylist(self, playlistName: str, playlist: dict):
        """ 创建播放列表 """
        self.playlistCardInterface.addOnePlaylistCard(playlistName, playlist)
        self.navigationInterface.updateWindow()

    def onRenamePlaylist(self, oldPlaylist: dict, newPlaylist: dict):
        """ 重命名播放列表槽函数 """
        self.playlistCardInterface.renamePlaylist(oldPlaylist, newPlaylist)
        self.navigationInterface.updateWindow()

    def onDeleteCustomPlaylist(self, playlistName: str):
        """ 删除自定义播放列表槽函数 """
        self.navigationInterface.updateWindow()
        if self.sender() is self.playlistInterface:
            self.playlistCardInterface.deleteOnePlaylistCard(playlistName)
            self.titleBar.returnBt.click()
        elif self.sender() is self.searchResultInterface:
            self.playlistCardInterface.deleteOnePlaylistCard(playlistName)

    def playCustomPlaylist(self, songInfo_list: list, index=0):
        """ 播放自定义播放列表中的所有歌曲 """
        self.playCheckedCards(songInfo_list, index)

    def addSongsToCustomPlaylist(self, playlistName: str, songInfo_list: list):
        """ 将歌曲添加到自定义播放列表中 """

        def resetSongInfo(songInfo_list: list, differentSongInfo_list):
            songInfo_list.clear()
            songInfo_list.extend(differentSongInfo_list)

        songInfo_list = deepcopy(songInfo_list)

        # 找出新的歌曲
        oldPlaylist = self.playlistCardInterface.playlists[playlistName]
        oldSongInfo_list = oldPlaylist.get("songInfo_list", [])
        differentSongInfo_list = [
            i for i in songInfo_list if i not in oldSongInfo_list]

        planToAddNum = len(songInfo_list)
        repeatNum = planToAddNum-len(differentSongInfo_list)

        # 如果有重复的歌曲就显示对话框
        if repeatNum > 0:
            if planToAddNum == 1:
                content = "此歌已在你的播放列表中。是否要添加？"
            elif repeatNum < planToAddNum:
                content = "部分歌曲已在你的播放列表中。是否要添加？"
            else:
                content = "所有这些歌曲都已在你的播放列表中。是否要添加？"
            w = MessageDialog("歌曲重复", content, self.window())
            w.cancelSignal.connect(lambda: resetSongInfo(
                songInfo_list, differentSongInfo_list))
            w.exec_()

        self.playlistCardInterface.addSongsToPlaylist(
            playlistName, songInfo_list)

    def switchToAlbumCardInterface(self):
        """ 切换到专辑卡界面 """
        self.subStackWidget.setCurrentWidget(self.myMusicInterface)
        self.titleBar.setWhiteIcon(False)
        self.titleBar.returnBt.show()
        self.myMusicInterface.setCurrentTab(1)
        self.navigationInterface.setCurrentIndex(0)

        # 增加导航历史
        index = self.myMusicInterface.stackedWidget.indexOf(
            self.albumCardInterface)
        self.navigationHistories.append(('myMusicInterfaceStackWidget', index))

    def switchToSearchResultInterface(self, keyWord: str):
        """ 切换到搜索结果界面 """
        # 更新搜索结果界面
        self.searchResultInterface.search(
            keyWord,
            self.songTabSongListWidget.songInfo_list,
            self.albumCardInterface.albumInfo_list,
            self.playlistCardInterface.playlists
        )

        # 切换界面
        self.titleBar.returnBt.show()
        QApplication.processEvents()
        self.subStackWidget.setCurrentWidget(
            self.searchResultInterface, duration=300)
        self.titleBar.setWhiteIcon(False)

        # 增加导航历史
        index = self.subStackWidget.indexOf(self.searchResultInterface)
        if self.navigationHistories[-1] != ("subStackWidget", index):
            self.navigationHistories.append(('subStackWidget', index))

    def showLabelNavigationInterface(self, label_list: list, layout: str):
        """ 显示标签导航界面 """
        self.labelNavigationInterface.setLabels(label_list, layout)
        self.subStackWidget.setCurrentWidget(
            self.labelNavigationInterface, duration=300)
        index = self.subStackWidget.indexOf(self.labelNavigationInterface)
        self.navigationHistories.append(('subStackWidget', index))

    def onNavigationLabelClicked(self, label: str):
        """ 导航标签点击槽函数 """
        self.myMusicInterface.scrollToLabel(label)
        self.subStackWidget.setCurrentWidget(
            self.subStackWidget.previousWidget)
        # 弹出导航历史
        self.navigationHistories.pop()

    def rescanSongInfoTimerSlot(self):
        """ 重新扫描歌曲信息 """
        if self.isInSelectionMode or not self.myMusicInterface.hasSongModified():
            return
        w = StateTooltip("正在更新歌曲列表", "要耐心等待哦 ٩(๑>◡<๑)۶ ", self)
        w.move(self.width()-w.width()-30, 63)
        w.show()
        self.myMusicInterface.rescanSongInfo()
        w.setState(True)

    def deleteSongs(self, songPaths: list):
        """ 删除歌曲 """
        self.playlistCardInterface.deleteSongs(songPaths)
        if self.sender() in [self.searchResultInterface, self.singerInterface]:
            self.myMusicInterface.deleteSongs(songPaths)
            if self.sender() is self.singerInterface and not self.singerInterface.albumInfo_list:
                self.titleBar.returnBt.click()

        # 歌曲移动到回收站
        for songPath in songPaths:
            moveToTrash(songPath)

    def playLocalSearchedSongs(self, index: int):
        """ 播放选中的本地搜索结果中的歌曲卡 """
        songInfo_list = self.searchResultInterface.localSongListWidget.songInfo_list

        if self.mediaPlaylist.playlistType != PlaylistType.CUSTOM_PLAYLIST or \
                self.mediaPlaylist.playlist != songInfo_list:
            self.playCheckedCards(songInfo_list, index)

        self.mediaPlaylist.setCurrentIndex(index)

    def playOnlineSearchedSongs(self, index: int):
        """ 播放选中的在线搜索结果中的歌曲卡 """
        songInfo_list = self.searchResultInterface.onlineSongListWidget.songInfo_list

        if self.mediaPlaylist.playlistType != PlaylistType.CUSTOM_PLAYLIST or \
                self.mediaPlaylist.playlist != songInfo_list:
            self.playCheckedCards(songInfo_list, index)

        self.mediaPlaylist.setCurrentIndex(index)

    def connectSignalToSlot(self):
        """ 将信号连接到槽 """

        # 将播放器的信号连接到槽函数
        self.player.positionChanged.connect(self.onPlayerPositionChanged)
        self.player.durationChanged.connect(self.onPlayerDurationChanged)

        # 将播放列表的信号连接到槽函数
        self.mediaPlaylist.currentIndexChanged.connect(self.updateWindow)

        # 将设置界面信号连接到槽函数
        self.settingInterface.crawlComplete.connect(
            self.myMusicInterface.rescanSongInfo)
        self.settingInterface.selectedMusicFoldersChanged.connect(
            self.myMusicInterface.scanTargetPathSongInfo)
        self.settingInterface.downloadFolderChanged.connect(
            self.searchResultInterface.setDownloadFolder)
        self.settingInterface.onlinePlayQualityChanged.connect(
            self.searchResultInterface.setOnlinePlayQuality)
        self.settingInterface.pageSizeChanged.connect(
            self.searchResultInterface.setOnlineMusicPageSize)

        # 将标题栏返回按钮点击信号连接到槽函数
        self.titleBar.returnBt.clicked.connect(self.onReturnButtonClicked)

        # 将导航界面信号连接到槽函数
        self.navigationInterface.displayModeChanged.connect(
            self.onNavigationDisplayModeChanged)
        self.navigationInterface.showPlayingInterfaceSig.connect(
            self.showPlayingInterface)
        self.navigationInterface.showCreatePlaylistDialogSig.connect(
            self.showCreatePlaylistDialog)
        self.navigationInterface.switchToSettingInterfaceSig.connect(
            self.switchToSettingInterface)
        self.navigationInterface.switchToMyMusicInterfaceSig.connect(
            self.switchToMyMusicInterface)
        self.navigationInterface.switchToPlaylistCardInterfaceSig.connect(
            self.switchToPlaylistCardInterface)
        self.navigationInterface.switchToPlaylistInterfaceSig.connect(
            self.switchToPlaylistInterface)
        self.navigationInterface.searchSig.connect(
            self.switchToSearchResultInterface)

        # 缩略图任务栏信号连接到槽函数
        self.thumbnailToolBar.togglePlayStateSig.connect(self.togglePlayState)
        self.thumbnailToolBar.lastSongSig.connect(self.mediaPlaylist.previous)
        self.thumbnailToolBar.nextSongSig.connect(self.mediaPlaylist.next)

        # 将播放栏信号连接到槽函数
        self.playBar.muteStateChanged.connect(self.setMute)
        self.playBar.nextSongSig.connect(self.mediaPlaylist.next)
        self.playBar.lastSongSig.connect(self.mediaPlaylist.previous)
        self.playBar.togglePlayStateSig.connect(self.togglePlayState)
        self.playBar.randomPlayChanged.connect(self.setRandomPlay)
        self.playBar.showPlayingInterfaceSig.connect(self.showPlayingInterface)
        self.playBar.volumeChanged.connect(self.onVolumeChanged)
        self.playBar.progressSliderMoved.connect(self.onprogressSliderMoved)
        self.playBar.loopModeChanged.connect(self.switchLoopMode)
        self.playBar.fullScreenSig.connect(lambda: self.setFullScreen(True))
        self.playBar.showPlaylistSig.connect(self.showPlaylist)
        self.playBar.clearPlaylistSig.connect(self.clearPlaylist)
        self.playBar.showSmallestPlayInterfaceSig.connect(
            self.showSmallestPlayInterface)
        self.playBar.savePlaylistSig.connect(
            lambda: self.showCreatePlaylistDialog(self.mediaPlaylist.playlist))

        # 将正在播放界面信号连接到槽函数
        self.playingInterface.currentIndexChanged.connect(
            self.onPlayingInterfaceCurrentIndexChanged)
        self.playingInterface.muteStateChanged.connect(self.setMute)
        self.playingInterface.nextSongSig.connect(self.mediaPlaylist.next)
        self.playingInterface.lastSongSig.connect(self.mediaPlaylist.previous)
        self.playingInterface.togglePlayStateSig.connect(self.togglePlayState)
        self.playingInterface.randomPlayChanged.connect(self.setRandomPlay)
        self.playingInterface.volumeChanged.connect(self.onVolumeChanged)
        self.playingInterface.fullScreenChanged.connect(self.setFullScreen)
        self.playingInterface.loopModeChanged.connect(self.switchLoopMode)
        self.playingInterface.removeMediaSignal.connect(
            self.mediaPlaylist.removeMedia)
        self.playingInterface.randomPlayAllSig.connect(self.disorderPlayAll)
        self.playingInterface.progressSliderMoved.connect(
            self.onprogressSliderMoved)
        self.playingInterface.switchToSingerInterfaceSig.connect(
            self.switchToSingerInterface)
        self.playingInterface.switchToAlbumInterfaceSig.connect(
            self.switchToAlbumInterface)
        self.playingInterface.savePlaylistSig.connect(
            lambda: self.showCreatePlaylistDialog(self.mediaPlaylist.playlist))
        self.playingInterface.showSmallestPlayInterfaceSig.connect(
            self.showSmallestPlayInterface)
        self.playingInterface.addSongsToNewCustomPlaylistSig.connect(
            self.showCreatePlaylistDialog)
        self.playingInterface.addSongsToCustomPlaylistSig.connect(
            self.addSongsToCustomPlaylist)
        self.playingInterface.selectionModeStateChanged.connect(
            self.onSelectionModeStateChanged)
        self.playingInterface.clearPlaylistSig.connect(self.clearPlaylist)

        # 将歌曲界面歌曲卡列表视图的信号连接到槽函数
        self.songTabSongListWidget.playSignal.connect(
            self.onSongTabSongCardPlay)
        self.songTabSongListWidget.playOneSongSig.connect(self.playOneSongCard)
        self.songTabSongListWidget.nextToPlayOneSongSig.connect(
            self.onSongCardNextPlay)
        self.songTabSongListWidget.addSongToPlayingSignal.connect(
            self.addOneSongToPlayingPlaylist)
        self.songTabSongListWidget.switchToSingerInterfaceSig.connect(
            self.switchToSingerInterface)
        self.songTabSongListWidget.switchToAlbumInterfaceSig.connect(
            self.switchToAlbumInterface)
        self.songTabSongListWidget.editSongInfoSignal.connect(
            self.onEditSongInfo)

        # 将专辑卡的信号连接到槽函数
        self.albumCardInterface.playSignal.connect(self.playAlbum)
        self.albumCardInterface.editAlbumInfoSignal.connect(
            self.onEditAlbumInfo)
        self.albumCardInterface.nextPlaySignal.connect(
            self.onMultiSongsNextPlay)
        self.albumCardInterface.switchToAlbumInterfaceSig.connect(
            self.switchToAlbumInterface)
        self.albumCardInterface.switchToSingerInterfaceSig.connect(
            self.switchToSingerInterface)

        # 将我的音乐界面连接到槽函数
        self.myMusicInterface.removeSongSig.connect(self.deleteSongs)
        self.myMusicInterface.randomPlayAllSig.connect(self.disorderPlayAll)
        self.myMusicInterface.playCheckedCardsSig.connect(
            self.playCheckedCards)
        self.myMusicInterface.currentIndexChanged.connect(
            self.onMyMucicInterfaceStackWidgetIndexChanged)
        self.myMusicInterface.nextToPlayCheckedCardsSig.connect(
            self.onMultiSongsNextPlay)
        self.myMusicInterface.selectionModeStateChanged.connect(
            self.onSelectionModeStateChanged)
        self.myMusicInterface.addSongsToCustomPlaylistSig.connect(
            self.addSongsToCustomPlaylist)
        self.myMusicInterface.addSongsToNewCustomPlaylistSig.connect(
            self.showCreatePlaylistDialog)
        self.myMusicInterface.addSongsToPlayingPlaylistSig.connect(
            self.addSongsToPlayingPlaylist)
        self.myMusicInterface.showLabelNavigationInterfaceSig.connect(
            self.showLabelNavigationInterface)

        # 将定时器信号连接到槽函数
        self.rescanSongInfoTimer.timeout.connect(self.rescanSongInfoTimerSlot)

        # 将专辑界面的信号连接到槽函数
        self.albumInterface.playAlbumSignal.connect(self.playAlbum)
        self.albumInterface.playOneSongCardSig.connect(self.playOneSongCard)
        self.albumInterface.editSongInfoSignal.connect(self.onEditSongInfo)
        self.albumInterface.editAlbumInfoSignal.connect(self.onEditAlbumInfo)
        self.albumInterface.songCardPlaySig.connect(
            self.onAlbumInterfaceSongCardPlay)
        self.albumInterface.nextToPlayOneSongSig.connect(
            self.onSongCardNextPlay)
        self.albumInterface.addOneSongToPlayingSig.connect(
            self.addOneSongToPlayingPlaylist)
        self.albumInterface.addSongsToPlayingPlaylistSig.connect(
            self.addSongsToPlayingPlaylist)
        self.albumInterface.selectionModeStateChanged.connect(
            self.onSelectionModeStateChanged)
        self.albumInterface.playCheckedCardsSig.connect(self.playCheckedCards)
        self.albumInterface.nextToPlayCheckedCardsSig.connect(
            self.onMultiSongsNextPlay)
        self.albumInterface.addSongsToCustomPlaylistSig.connect(
            self.addSongsToCustomPlaylist)
        self.albumInterface.addSongsToNewCustomPlaylistSig.connect(
            self.showCreatePlaylistDialog)
        self.albumInterface.switchToSingerInterfaceSig.connect(
            self.switchToSingerInterface)

        # 将播放界面信号连接到槽函数
        self.playlistInterface.playAllSig.connect(self.playCustomPlaylist)
        self.playlistInterface.editSongInfoSignal.connect(self.onEditSongInfo)
        self.playlistInterface.playOneSongCardSig.connect(self.playOneSongCard)
        self.playlistInterface.deletePlaylistSig.connect(
            self.onDeleteCustomPlaylist)
        self.playlistInterface.playCheckedCardsSig.connect(
            self.playCustomPlaylist)
        self.playlistInterface.songCardPlaySig.connect(
            self.onPlaylistInterfaceSongCardPlay)
        self.playlistInterface.addSongsToPlayingPlaylistSig.connect(
            self.addSongsToPlayingPlaylist)
        self.playlistInterface.addSongsToNewCustomPlaylistSig.connect(
            self.showCreatePlaylistDialog)
        self.playlistInterface.addSongsToCustomPlaylistSig.connect(
            self.addSongsToCustomPlaylist)
        self.playlistInterface.nextToPlayOneSongSig.connect(
            self.onSongCardNextPlay)
        self.playlistInterface.nextToPlayCheckedCardsSig.connect(
            self.onMultiSongsNextPlay)
        self.playlistInterface.addOneSongToPlayingSig.connect(
            self.addOneSongToPlayingPlaylist)
        self.playlistInterface.selectionModeStateChanged.connect(
            self.onSelectionModeStateChanged)
        self.playlistInterface.switchToAlbumInterfaceSig.connect(
            self.switchToAlbumInterface)
        self.playlistInterface.renamePlaylistSig.connect(
            self.onRenamePlaylist)
        self.playlistInterface.removeSongSig.connect(
            self.playlistCardInterface.updateOnePlaylist)
        self.playlistInterface.switchToAlbumCardInterfaceSig.connect(
            self.switchToAlbumCardInterface)
        self.playlistInterface.switchToSingerInterfaceSig.connect(
            self.switchToSingerInterface)

        # 将播放列表卡界面信号连接到槽函数
        self.playlistCardInterface.selectionModeStateChanged.connect(
            self.onSelectionModeStateChanged)
        self.playlistCardInterface.createPlaylistSig.connect(
            self.showCreatePlaylistDialog)
        self.playlistCardInterface.renamePlaylistSig.connect(
            self.onRenamePlaylist)
        self.playlistCardInterface.deletePlaylistSig.connect(
            self.onDeleteCustomPlaylist)
        self.playlistCardInterface.playSig.connect(self.playCustomPlaylist)
        self.playlistCardInterface.nextToPlaySig.connect(
            self.onMultiSongsNextPlay)
        self.playlistCardInterface.switchToPlaylistInterfaceSig.connect(
            self.switchToPlaylistInterface)
        self.playlistCardInterface.addSongsToCustomPlaylistSig.connect(
            self.addSongsToCustomPlaylist)
        self.playlistCardInterface.addSongsToNewCustomPlaylistSig.connect(
            self.showCreatePlaylistDialog)
        self.playlistCardInterface.addSongsToPlayingPlaylistSig.connect(
            self.addSongsToPlayingPlaylist)

        # 将最小播放界面连接到槽函数
        self.smallestPlayInterface.nextSongSig.connect(self.mediaPlaylist.next)
        self.smallestPlayInterface.lastSongSig.connect(
            self.mediaPlaylist.previous)
        self.smallestPlayInterface.togglePlayStateSig.connect(
            self.togglePlayState)
        self.smallestPlayInterface.exitSmallestPlayInterfaceSig.connect(
            self.exitSmallestPlayInterface)

        # 将标签导航界面的信号连接到槽函数
        self.labelNavigationInterface.labelClicked.connect(
            self.onNavigationLabelClicked)

        # 将搜索结果界面信号连接到槽函数
        self.searchResultInterface.playAlbumSig.connect(self.playAlbum)
        self.searchResultInterface.deleteAlbumSig.connect(self.deleteSongs)
        self.searchResultInterface.playLocalSongSig.connect(
            self.playLocalSearchedSongs)
        self.searchResultInterface.playOnlineSongSig.connect(
            self.playOnlineSearchedSongs)
        self.searchResultInterface.deletePlaylistSig.connect(
            self.onDeleteCustomPlaylist)
        self.searchResultInterface.playPlaylistSig.connect(
            self.playCustomPlaylist)
        self.searchResultInterface.nextToPlaySig.connect(
            self.onMultiSongsNextPlay)
        self.searchResultInterface.playOneSongCardSig.connect(
            self.playOneSongCard)
        self.searchResultInterface.renamePlaylistSig.connect(
            self.onRenamePlaylist)
        self.searchResultInterface.switchToSingerInterfaceSig.connect(
            self.switchToSingerInterface)
        self.searchResultInterface.switchToAlbumInterfaceSig.connect(
            self.switchToAlbumInterface)
        self.searchResultInterface.switchToPlaylistInterfaceSig.connect(
            self.switchToPlaylistInterface)
        self.searchResultInterface.addSongsToPlayingPlaylistSig.connect(
            self.addSongsToPlayingPlaylist)
        self.searchResultInterface.addSongsToNewCustomPlaylistSig.connect(
            self.showCreatePlaylistDialog)
        self.searchResultInterface.addSongsToCustomPlaylistSig.connect(
            self.addSongsToCustomPlaylist)
        self.searchResultInterface.deleteSongSig.connect(
            lambda songPath: self.deleteSongs([songPath]))

        # 将歌手界面信号连接到槽函数
        self.singerInterface.playSig.connect(self.playCustomPlaylist)
        self.singerInterface.deleteAlbumSig.connect(self.deleteSongs)
        self.singerInterface.nextToPlaySig.connect(self.onMultiSongsNextPlay)
        self.singerInterface.editAlbumInfoSignal.connect(self.onEditAlbumInfo)
        self.singerInterface.switchToAlbumInterfaceSig.connect(
            self.switchToAlbumInterface)
        self.singerInterface.addSongsToPlayingPlaylistSig.connect(
            self.addSongsToPlayingPlaylist)
        self.singerInterface.addSongsToNewCustomPlaylistSig.connect(
            self.showCreatePlaylistDialog)
        self.singerInterface.addSongsToCustomPlaylistSig.connect(
            self.addSongsToCustomPlaylist)
        self.singerInterface.selectionModeStateChanged.connect(
            self.onSelectionModeStateChanged)
