# coding:utf-8
import os
from copy import deepcopy
from pathlib import Path
from random import shuffle

from common import resource
from common.crawler import CrawlerBase
from common.os_utils import moveToTrash
from common.thread.get_online_song_url_thread import GetOnlineSongUrlThread
from components.dialog_box.create_playlist_dialog import CreatePlaylistDialog
from components.dialog_box.message_dialog import MessageDialog
from components.frameless_window import FramelessWindow
from components.label_navigation_interface import LabelNavigationInterface
from components.media_player import MediaPlaylist, PlaylistType
from components.system_tray_icon import SystemTrayIcon
from components.thumbnail_tool_bar import ThumbnailToolBar
from components.title_bar import TitleBar
from components.video_window import VideoWindow
from components.widgets.stacked_widget import (OpacityAniStackedWidget,
                                               PopUpAniStackedWidget)
from components.widgets.state_tooltip import StateTooltip
from PyQt5.QtCore import (QEasingCurve, QEvent, QEventLoop, QFile, Qt, QTimer,
                          QUrl)
from PyQt5.QtGui import QCloseEvent, QColor, QIcon, QPixmap
from PyQt5.QtMultimedia import QMediaContent, QMediaPlayer, QMediaPlaylist
from PyQt5.QtWidgets import (QAction, QApplication, QHBoxLayout, QLabel,
                             QWidget, qApp)
from PyQt5.QtWinExtras import QtWin
from system_hotkey import SystemHotkey
from View.album_interface import AlbumInterface
from View.my_music_interface import MyMusicInterface
from View.navigation_interface import NavigationInterface
from View.play_bar import PlayBar
from View.playing_interface import PlayingInterface
from View.playlist_card_interface import PlaylistCardInterface
from View.playlist_interface import PlaylistInterface
from View.search_result_interface import SearchResultInterface
from View.setting_interface import SettingInterface
from View.singer_interface import SingerInterface
from View.smallest_play_interface import SmallestPlayInterface


class MainWindow(FramelessWindow):
    """ 主窗口 """

    def __init__(self, parent=None):
        super().__init__(parent)
        self.setObjectName("mainWindow")
        self.createWidgets()
        self.isInSelectionMode = False
        self.navigationHistories = [("myMusicInterfaceStackWidget", 0)]
        self.initWidget()

    def createWidgets(self):
        """ 创建小部件 """
        # 主界面放置 totalStackWidget、playBar 和 titleBar
        # totalStackWidget用来放置 subMainWindow、 playingInterface 和 videoWindow
        self.totalStackWidget = OpacityAniStackedWidget(self)

        # subMainWindow 用来放置导航界面和 subStackWidget
        self.subMainWindow = QWidget(self)

        # 启动界面
        self.splashScreen = SplashScreen(self)

        # 标题栏
        self.titleBar = TitleBar(self)

        self.resize(1240, 970)
        self.setWindowTitle(self.tr("Groove Music"))
        self.setWindowIcon(QIcon(":/images/logo/logo_small.png"))

        # 在去除任务栏的显示区域居中显示
        QtWin.enableBlurBehindWindow(self)
        self.setWindowFlags(Qt.FramelessWindowHint |
                            Qt.WindowMinMaxButtonsHint)
        self.windowEffect.addWindowAnimation(self.winId())
        desktop = QApplication.desktop().availableGeometry()
        self.move(desktop.width()//2 - self.width()//2,
                  desktop.height()//2 - self.height()//2)
        self.show()
        QApplication.processEvents()

        # 创建播放器和播放列表
        self.player = QMediaPlayer(self)
        self.mediaPlaylist = MediaPlaylist(self)

        # subStackWidget用来放置 myMusicInterface、albumInterface等需要在导航栏右边显示的窗口
        self.subStackWidget = PopUpAniStackedWidget(self.subMainWindow)

        # 创建设置界面
        self.settingInterface = SettingInterface(self.subMainWindow)

        # 从配置文件中的选择文件夹读取音频文件
        self.myMusicInterface = MyMusicInterface(
            self.settingInterface.config["selected-folders"], self.subMainWindow)

        # 创建定时扫描歌曲信息的定时器
        self.rescanSongInfoTimer = QTimer(self)

        # 创建更新歌词位置的定时器
        self.updateLyricPosTimer = QTimer(self)

        # 创建缩略图任务栏
        self.thumbnailToolBar = ThumbnailToolBar(self)
        self.thumbnailToolBar.setWindow(self.windowHandle())

        # 创建播放栏
        color = self.settingInterface.config['playBar-color']
        self.playBar = PlayBar(
            self.mediaPlaylist.lastSongInfo, QColor(*color), self)

        # 创建正在播放界面
        self.playingInterface = PlayingInterface(
            self.mediaPlaylist.playlist, self)

        # 创建视频界面
        self.videoWindow = VideoWindow(self)

        # 创建专辑界面
        self.albumInterface = AlbumInterface(parent=self.subMainWindow)

        # 创建歌手界面
        self.singerInterface = SingerInterface(parent=self.subMainWindow)

        # 创建播放列表卡界面和播放列表界面
        self.playlistInterface = PlaylistInterface({}, self.subMainWindow)
        self.playlistCardInterface = PlaylistCardInterface(self.subMainWindow)

        # 创建导航界面
        self.navigationInterface = NavigationInterface(self.subMainWindow)

        # 创建标签导航界面
        self.labelNavigationInterface = LabelNavigationInterface(
            self.subMainWindow)

        # 创建最小播放界面
        self.smallestPlayInterface = SmallestPlayInterface(
            self.mediaPlaylist.playlist, parent=self)

        # 创建系统托盘图标
        self.systemTrayIcon = SystemTrayIcon(self)

        # 创建搜索结果界面
        pageSize = self.settingInterface.config['online-music-page-size']
        quality = self.settingInterface.config['online-play-quality']
        folder = self.settingInterface.config['download-folder']
        self.searchResultInterface = SearchResultInterface(
            pageSize, quality, folder, self.subMainWindow)

        # 创建线程
        self.getOnlineSongUrlThread = GetOnlineSongUrlThread(self)

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
        self.addActions([
            self.togglePlayPauseAct_1,
            self.showNormalAct,
            self.nextSongAct,
            self.lastSongAct,
            self.togglePlayPauseAct_2,
        ])

        self.songTabSongListWidget = self.myMusicInterface.songListWidget
        self.albumCardInterface = self.myMusicInterface.albumCardInterface

    def initWidget(self):
        """ 初始化小部件 """
        self.resize(1240, 970)
        self.setMinimumSize(1030, 800)
        self.videoWindow.hide()

        # 关闭最后一个窗口后不退出
        QApplication.setQuitOnLastWindowClosed(
            not self.settingInterface.config['minimize-to-tray'])

        # 在去除任务栏的显示区域居中显示
        desktop = QApplication.desktop().availableGeometry()
        self.smallestPlayInterface.move(desktop.width() - 390, 40)

        # 标题栏置顶
        self.titleBar.raise_()

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
        self.totalStackWidget.addWidget(self.videoWindow)
        self.subMainWindow.setGraphicsEffect(None)

        # 设置右边子窗口的位置
        self.adjustWidgetGeometry()

        # 设置层叠样式
        self.setQss()

        # 设置定时器溢出时间
        self.rescanSongInfoTimer.setInterval(180000)
        self.updateLyricPosTimer.setInterval(100)

        # 设置播放器发送播放位置改变的信号的间隔
        self.player.setNotifyInterval(1000)

        # 设置 MV 画质
        self.playingInterface.getMvUrlThread.setVideoQuality(
            self.settingInterface.config['mv-quality'])

        # 初始化播放列表
        self.initPlaylist()

        # TODO:设置全局热键
        # self.setHotKey()

        # 将信号连接到槽函数
        self.connectSignalToSlot()

        # 初始化播放栏
        self.initPlayBar()

        # 设置播放按钮可用性
        self.setPlayButtonEnabled(
            len(self.songTabSongListWidget.songInfo_list) > 0)

        # 安装事件过滤器
        self.navigationInterface.navigationMenu.installEventFilter(self)
        self.rescanSongInfoTimer.start()
        self.updateLyricPosTimer.start()
        self.onInitFinished()

    def onInitFinished(self):
        """ 初始化完成 """
        self.splashScreen.hide()
        self.subStackWidget.show()
        self.navigationInterface.show()
        self.playBar.show()
        self.systemTrayIcon.show()
        self.setWindowEffect(
            self.settingInterface.config["enable-acrylic-background"])

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

    def setWindowEffect(self, isEnableAcrylic: bool):
        """ 设置窗口特效 """
        if isEnableAcrylic:
            self.windowEffect.setAcrylicEffect(self.winId(), "F2F2F299", True)
            self.setStyleSheet("#mainWindow{background:transparent}")
        else:
            self.setStyleSheet("#mainWindow{background:#F2F2F2}")
            self.windowEffect.addShadowEffect(self.winId())
            self.windowEffect.removeBackgroundEffect(self.winId())

    def adjustWidgetGeometry(self):
        """ 调整小部件的geometry """
        self.titleBar.resize(self.width(), 40)
        self.splashScreen.resize(self.size())

        if not hasattr(self, 'playBar'):
            return

        self.subMainWindow.resize(self.size())
        self.totalStackWidget.resize(self.size())
        self.playBar.resize(self.width(), self.playBar.height())
        self.playBar.move(0, self.height()-self.playBar.height())

        if not hasattr(self, "navigationInterface"):
            return

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
            isVisible = self.titleBar.returnButton.isVisible()

            if e.type() == QEvent.Show:
                self.titleBar.returnButton.setParent(obj)
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
                self.titleBar.returnButton.setParent(self.titleBar)
                self.titleBar.title.hide()

            self.titleBar.returnButton.setVisible(isVisible)

        return super().eventFilter(obj, e)

    def resizeEvent(self, e):
        """ 调整尺寸时同时调整子窗口的尺寸 """
        super().resizeEvent(e)
        self.adjustWidgetGeometry()
        self.titleBar.maxButton.setMaxState(
            self._isWindowMaximized(int(self.winId())))

    def closeEvent(self, e: QCloseEvent):
        """ 关闭窗口前更新json文件 """
        config = {}
        config["volume"] = self.playBar.volumeSlider.value()
        config["playBar-color"] = list(
            self.playBar.getColor().getRgb()[:3])
        self.settingInterface.updateConfig(config)
        self.mediaPlaylist.save()

        # 显示通知
        if self.settingInterface.config['minimize-to-tray']:
            title = self.tr('Minimize to system tray')
            content = self.tr(
                'Groove Music will continue to run in the background.')
            self.systemTrayIcon.showMessage(
                title, content, SystemTrayIcon.Information)

        e.accept()

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
            self.songTabSongListWidget.setPlay(0)
            if songInfo_list:
                self.systemTrayIcon.updateWindow(songInfo_list[0])

        # 将当前歌曲设置为上次关闭前播放的歌曲
        if self.mediaPlaylist.lastSongInfo in self.mediaPlaylist.playlist:
            index = self.mediaPlaylist.playlist.index(
                self.mediaPlaylist.lastSongInfo)
            self.mediaPlaylist.setCurrentIndex(index)
            self.playingInterface.setCurrentIndex(index)
            self.smallestPlayInterface.setCurrentIndex(index)
            self.systemTrayIcon.updateWindow(self.mediaPlaylist.lastSongInfo)

            index = self.songTabSongListWidget.index(
                self.mediaPlaylist.lastSongInfo)
            if index is not None:
                self.songTabSongListWidget.setPlay(index)

    def togglePlayState(self):
        """ 播放按钮按下时根据播放器的状态来决定是暂停还是播放 """
        if self.totalStackWidget.currentWidget() is self.videoWindow:
            self.videoWindow.togglePlayState()
            return

        if self.player.state() == QMediaPlayer.PlayingState:
            self.player.pause()
            self.setPlayButtonState(False)
            self.thumbnailToolBar.setButtonsEnabled(True)
        else:
            self.play()

    def checkMediaAvailable(self):
        """ 当前播放的音频切换槽函数 """
        if not self.mediaPlaylist.playlist:
            return

        # 判断媒体是否可用
        songPath = self.mediaPlaylist.getCurrentSong().get("songPath", '')
        if songPath.startswith('http') or os.path.exists(songPath):
            return

        # 媒体不可用时暂停播放器
        self.player.pause()
        self.setPlayButtonState(False)

        # 弹出提示框
        w = MessageDialog(self.tr("Can't play this song"), self.tr(
            "It's not on this device or somewhere we can stream from."), self)
        w.cancelButton.setText(self.tr('Close'))
        w.yesButton.hide()
        w.exec()

    def setPlayButtonState(self, isPlay: bool):
        """ 设置播放按钮状态 """
        self.playBar.setPlay(isPlay)
        self.systemTrayIcon.setPlay(isPlay)
        self.playingInterface.setPlay(isPlay)
        self.thumbnailToolBar.setPlay(isPlay)
        self.smallestPlayInterface.setPlay(isPlay)

    def setPlayButtonEnabled(self, isEnabled: bool):
        """ 设置播放按钮是否启用 """
        self.playBar.playButton.setEnabled(isEnabled)
        self.playBar.nextSongButton.setEnabled(isEnabled)
        self.playBar.lastSongButton.setEnabled(isEnabled)
        self.playingInterface.playBar.playButton.setEnabled(isEnabled)
        self.playingInterface.playBar.nextSongButton.setEnabled(isEnabled)
        self.playingInterface.playBar.lastSongButton.setEnabled(isEnabled)
        self.thumbnailToolBar.playButton.setEnabled(isEnabled)
        self.thumbnailToolBar.nextSongButton.setEnabled(isEnabled)
        self.thumbnailToolBar.lastSongButton.setEnabled(isEnabled)
        self.smallestPlayInterface.playButton.setEnabled(isEnabled)
        self.smallestPlayInterface.lastSongButton.setEnabled(isEnabled)
        self.smallestPlayInterface.nextSongButton.setEnabled(isEnabled)
        self.systemTrayIcon.menu.songAct.setEnabled(isEnabled)
        self.systemTrayIcon.menu.playAct.setEnabled(isEnabled)
        self.systemTrayIcon.menu.lastSongAct.setEnabled(isEnabled)
        self.systemTrayIcon.menu.nextSongAct.setEnabled(isEnabled)

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
        self.playingInterface.setCurrentTime(position)
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
        self.mediaPlaylist.insertSong(
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
        if not self.mediaPlaylist.playlist:
            self.playBar.songInfoCard.hide()
            self.setPlayButtonState(False)
            self.setPlayButtonEnabled(False)
            return

        self.setPlayButtonEnabled(True)

        # 处理歌曲不存在的情况
        if index < 0:
            return

        songInfo = self.mediaPlaylist.playlist[index]

        # 更新正在播放界面、播放栏、专辑界面、播放列表界面、搜索界面和最小播放界面
        self.playBar.updateSongInfoCard(songInfo)
        self.playingInterface.setCurrentIndex(index)
        self.systemTrayIcon.updateWindow(songInfo)

        if self.smallestPlayInterface.isVisible():
            self.smallestPlayInterface.setCurrentIndex(index)

        self.songTabSongListWidget.setPlayBySongInfo(songInfo)
        self.albumInterface.songListWidget.setPlayBySongInfo(songInfo)
        self.playlistInterface.songListWidget.setPlayBySongInfo(songInfo)
        self.searchResultInterface.localSongListWidget.setPlayBySongInfo(
            songInfo)
        self.searchResultInterface.onlineSongListWidget.setPlayBySongInfo(
            songInfo)

        # 在更新完界面之后，检查媒体是否可用（需要显示警告图标）
        self.checkMediaAvailable()

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
        self.mediaPlaylist.insertSongs(
            self.mediaPlaylist.currentIndex() + 1, songInfo_list)

    def disorderPlayAll(self):
        """ 无序播放所有 """
        self.mediaPlaylist.playlistType = PlaylistType.ALL_SONG_PLAYLIST
        newPlaylist = deepcopy(self.songTabSongListWidget.songInfo_list)
        shuffle(newPlaylist)
        self.setPlaylist(newPlaylist)

    def play(self):
        """ 播放歌曲并改变按钮样式 """
        if not self.mediaPlaylist.playlist:
            self.playBar.songInfoCard.hide()
            self.setPlayButtonState(False)
            self.setPlayButtonEnabled(False)
            self.playBar.setTotalTime(0)
            self.playBar.progressSlider.setRange(0, 0)
        else:
            self.player.play()
            self.setPlayButtonState(True)
            self.playBar.songInfoCard.show()

    def initPlayBar(self):
        """ 从配置文件中读取配置数据来初始化播放栏 """
        # 初始化音量
        volume = self.settingInterface.config["volume"]
        self.playingInterface.setVolume(volume)

        # 初始化歌曲卡信息
        if self.mediaPlaylist.playlist:
            self.playBar.updateSongInfoCard(
                self.mediaPlaylist.getCurrentSong())
            self.playBar.songInfoCard.albumCoverLabel.setOpacity(1)

    def setQss(self):
        """ 设置层叠样式 """
        self.setObjectName("mainWindow")
        self.subMainWindow.setObjectName("subMainWindow")
        self.subStackWidget.setObjectName("subStackWidget")
        self.playingInterface.setObjectName("playingInterface")

        f = QFile(":/qss/main_window.qss")
        f.open(QFile.ReadOnly)
        self.setStyleSheet(str(f.readAll(), encoding='utf-8'))
        f.close()

    def onPlayingInterfaceCurrentIndexChanged(self, index):
        """ 正在播放界面下标变化槽函数 """
        self.mediaPlaylist.setCurrentIndex(index)
        self.play()

    def setMute(self, isMute: bool):
        """ 设置静音 """
        self.player.setMuted(isMute)
        self.playingInterface.setMute(isMute)
        self.playBar.setMute(isMute)

    def setVideoFullScreen(self, isFullScreen: bool):
        """ 设置视频界面全屏 """
        self.titleBar.setVisible(not isFullScreen)
        self.titleBar.maxButton.setMaxState(isFullScreen)
        self.titleBar.returnButton.show()
        if isFullScreen:
            self.showFullScreen()
        else:
            self.showNormal()

    def setFullScreen(self, isFullScreen: bool):
        """ 设置全屏 """
        if isFullScreen == self.isFullScreen():
            return

        if not isFullScreen:
            self.exitFullScreen()
            return

        # 更新标题栏
        self.playBar.hide()
        self.titleBar.title.hide()
        self.titleBar.setWhiteIcon(True)
        self.titleBar.hide()

        # 切换到正在播放界面
        self.totalStackWidget.setCurrentIndex(1)

        # 增加导航历史
        self.navigationHistories.append(("totalStackWidget", 1))

        self.showFullScreen()
        self.videoWindow.playBar.fullScreenButton.setFullScreen(True)
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
        self.titleBar.maxButton.setMaxState(False)
        self.titleBar.returnButton.show()
        self.titleBar.show()

        self.videoWindow.playBar.fullScreenButton.setFullScreen(False)
        self.playingInterface.setFullScreen(False)
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
        self.playBar.songInfoCard.hide()
        self.setPlayButtonState(False)
        self.setPlayButtonEnabled(False)

        self.songTabSongListWidget.cancelPlayState()
        self.albumInterface.songListWidget.cancelPlayState()
        self.playlistInterface.songListWidget.cancelPlayState()
        self.searchResultInterface.localSongListWidget.cancelPlayState()
        self.searchResultInterface.onlineSongListWidget.cancelPlayState()

        self.playBar.setTotalTime(0)
        self.playBar.progressSlider.setRange(0, 0)

    def addOneSongToPlayingPlaylist(self, songInfo: dict):
        """ 向正在播放列表尾部添加一首歌 """
        self.mediaPlaylist.addSong(songInfo)
        self.playingInterface.setPlaylist(self.mediaPlaylist.playlist, False)
        self.smallestPlayInterface.setPlaylist(
            self.mediaPlaylist.playlist, False)

    def addSongsToPlayingPlaylist(self, songInfo_list: list):
        """ 向正在播放列表尾部添加多首歌 """
        self.mediaPlaylist.addSongs(songInfo_list)
        self.playingInterface.setPlaylist(self.mediaPlaylist.playlist, False)
        self.smallestPlayInterface.setPlaylist(
            self.mediaPlaylist.playlist, False)

    def switchToSubInterface(self, widget: QWidget, whiteIcon=False, whiteReturn=False):
        """ 切换到 `subStackWidget` 的一个子界面

        Parameters
        ----------
        widget: QWidget
            将要切换到的界面

        whiteIcon: bool
            是否将最小化按钮、最大化按钮和关闭按钮设置为白色按钮

        whiteReturn: bool
            是否将返回按钮设置为白色按钮
        """
        # 更新标题栏图标颜色
        self.titleBar.returnButton.show()
        self.titleBar.setWhiteIcon(whiteIcon)
        self.titleBar.returnButton.setWhiteIcon(whiteReturn)

        # 切换界面
        self.exitSelectionMode()
        self.playBar.show()
        self.totalStackWidget.setCurrentIndex(0)
        self.subStackWidget.setCurrentWidget(widget)
        self.appendSubStackWidgetHistory(widget)

    def switchToPlaylistInterface(self, playlistName: str):
        """ 切换到播放列表界面 """
        if self.isInSelectionMode:
            return

        # 切换界面
        playlist = self.playlistCardInterface.playlists[playlistName]
        self.playlistInterface.updateWindow(playlist)
        self.switchToSubInterface(self.playlistInterface, True)

        # 根据当前播放的歌曲设置歌曲卡播放状态
        songInfo = self.mediaPlaylist.getCurrentSong()
        if songInfo in self.playlistInterface.songInfo_list:
            index = self.playlistInterface.songInfo_list.index(songInfo)
            self.playlistInterface.songListWidget.setPlay(index)

    def switchToSingerInterface(self, singerName: str):
        """ 切换到专辑界面 """
        if self.isInSelectionMode:
            return

        singerInfo = self.myMusicInterface.findSingerInfo(singerName)
        if not singerInfo:
            return

        # 切换界面
        self.exitFullScreen()
        self.singerInterface.updateWindow(singerInfo)
        self.switchToSubInterface(self.singerInterface, True)
        self.singerInterface.albumBlurBackground.hide()

    def switchToAlbumInterface(self, albumName: str, singerName: str):
        """ 切换到专辑界面 """
        if self.isInSelectionMode:
            return

        albumInfo = self.albumCardInterface.findAlbumInfoByName(
            albumName, singerName)
        if not albumInfo:
            return

        # 切换界面
        self.exitFullScreen()
        self.albumInterface.updateWindow(albumInfo)
        self.switchToSubInterface(self.albumInterface, True)

        # 根据当前播放的歌曲设置歌曲卡播放状态
        songInfo = self.mediaPlaylist.getCurrentSong()
        self.albumInterface.songListWidget.setPlayBySongInfo(songInfo)

    def switchToSettingInterface(self):
        """ 切换到设置界面 """
        self.show()

        if self.videoWindow.isVisible():
            # TODO: 从视频界面直接切换回设置界面
            return

        if self.playingInterface.isVisible():
            self.titleBar.returnButton.click()

        self.switchToSubInterface(self.settingInterface)

    def switchToMyMusicInterface(self):
        """ 切换到我的音乐界面 """
        self.exitSelectionMode()
        self.subStackWidget.setCurrentWidget(self.myMusicInterface)
        self.appendSubStackWidgetHistory(self.myMusicInterface)

    def switchToPlaylistCardInterface(self):
        """ 切换到播放列表卡界面 """
        self.switchToSubInterface(self.playlistCardInterface)

    def switchToAlbumCardInterface(self):
        """ 切换到专辑卡界面 """
        self.subStackWidget.setCurrentWidget(self.myMusicInterface)
        self.titleBar.setWhiteIcon(False)
        self.titleBar.returnButton.show()
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

        # 增加导航历史
        self.switchToSubInterface(self.searchResultInterface)

        # 设置当前播放歌曲
        self.searchResultInterface.localSongListWidget.setPlayBySongInfo(
            self.mediaPlaylist.getCurrentSong())

    def showLabelNavigationInterface(self, label_list: list, layout: str):
        """ 显示标签导航界面 """
        self.labelNavigationInterface.setLabels(label_list, layout)
        self.switchToSubInterface(self.labelNavigationInterface)

    def appendSubStackWidgetHistory(self, widget: QWidget):
        """ 压入子堆栈界面的切换历史 """
        index = self.subStackWidget.indexOf(widget)
        if self.navigationHistories[-1] == ("subStackWidget", index):
            return

        self.navigationHistories.append(('subStackWidget', index))

    def showPlayingInterface(self):
        """ 显示正在播放界面 """
        self.show()

        if self.playingInterface.isVisible():
            return

        # 先退出选择模式
        self.exitSelectionMode()
        self.playBar.hide()
        self.titleBar.title.hide()
        self.titleBar.returnButton.show()

        if not self.playingInterface.isPlaylistVisible and len(self.playingInterface.playlist) > 0:
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
            self.titleBar.returnButton.setWhiteIcon(False)
        else:
            self.titleBar.setWhiteIcon(False)

        # 隐藏返回按钮
        cond = self.subStackWidget.currentWidget() not in [
            self.albumInterface, self.labelNavigationInterface]
        if len(self.navigationHistories) == 1 and cond:
            self.titleBar.returnButton.hide()

        self.titleBar.title.setVisible(self.navigationInterface.isExpanded)

    def showVideoWindow(self, url: str):
        """ 显示视频界面 """
        self.player.pause()
        self.setPlayButtonState(False)

        songInfo = self.mediaPlaylist.getCurrentSong()
        self.videoWindow.setVideo(
            url, songInfo['singer']+' - '+songInfo['songName'])
        self.totalStackWidget.setCurrentIndex(2)

        self.navigationHistories.append(("totalStackWidget", 2))
        self.titleBar.returnButton.show()

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

        history = self.navigationHistories.pop()
        if history == ("totalStackWidget", 2):
            self.videoWindow.pause()
            self.totalStackWidget.setCurrentIndex(1)
            return

        # 如果上一个界面还是正在播放界面就直接将其弹出，因为不应该回退到正在播放界面
        if self.navigationHistories[-1] == ("totalStackWidget", 1):
            self.navigationHistories.pop()

        stackWidget, index = self.navigationHistories[-1]
        if stackWidget == "myMusicInterfaceStackWidget":
            self.myMusicInterface.stackedWidget.setCurrentIndex(index)
            self.subStackWidget.setCurrentIndex(
                0, True, False, 200, QEasingCurve.InCubic)
            self.navigationInterface.setCurrentIndex(0)
            self.myMusicInterface.setSelectedButton(index)
            self.titleBar.setWhiteIcon(False)
        elif stackWidget == "subStackWidget":
            isShowNextWidgetDirectly = self.subStackWidget.currentWidget() is not self.settingInterface
            self.subStackWidget.setCurrentIndex(
                index, True, isShowNextWidgetDirectly, 200, QEasingCurve.InCubic)
            self.navigationInterface.setCurrentIndex(index)
            # 更新标题栏图标颜色
            whiteIndexes = [self.subStackWidget.indexOf(
                i) for i in [self.playlistInterface, self.albumInterface, self.singerInterface]]
            self.titleBar.setWhiteIcon(index in whiteIndexes)
            self.titleBar.returnButton.setWhiteIcon(False)

        self.hidePlayingInterface()

        if len(self.navigationHistories) == 1:
            self.titleBar.returnButton.hide()

    def onMyMusicInterfaceStackWidgetIndexChanged(self, index):
        """ 堆叠窗口下标改变时的槽函数 """
        self.navigationHistories.append(("myMusicInterfaceStackWidget", index))
        self.titleBar.returnButton.show()

    def onEditSongInfo(self, oldSongInfo: dict, newSongInfo: dict):
        """ 编辑歌曲卡完成信号的槽函数 """
        self.mediaPlaylist.updateOneSongInfo(newSongInfo)
        self.playingInterface.updateOneSongCard(newSongInfo)
        self.playlistCardInterface.updateOneSongInfo(newSongInfo)
        self.smallestPlayInterface.updateOneSongInfo(newSongInfo)
        self.myMusicInterface.updateOneSongInfo(oldSongInfo, newSongInfo)
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
            self.myMusicInterface.singerInfoReader.updateSingerInfos(
                self.albumCardInterface.albumInfo_list)
            if not self.albumInterface.songInfo_list:
                self.titleBar.returnButton.click()

        elif self.sender() is self.albumCardInterface:
            self.myMusicInterface.singerInfoReader.updateSingerInfos(
                self.albumCardInterface.albumInfo_list)
            if oldAlbumInfo == self.albumInterface.albumInfo:
                self.albumInterface.albumInfoBar.updateWindow(newAlbumInfo)

        elif self.sender() is self.singerInterface:
            self.albumCardInterface.updateOneAlbumInfo(
                oldAlbumInfo, newAlbumInfo, coverPath)
            self.myMusicInterface.singerInfoReader.updateSingerInfos(
                self.albumCardInterface.albumInfo_list)
            self.singerInterface.updateWindow(
                self.myMusicInterface.findSingerInfo(newAlbumInfo['singer']))

        self.myMusicInterface.songInfoReader.songInfo_list = deepcopy(
            self.songTabSongListWidget.songInfo_list)
        self.myMusicInterface.albumInfoReader.albumInfo_list = deepcopy(
            self.albumCardInterface.albumInfo_list)

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
        self.smallestPlayInterface.setPlaylist(playlist)
        self.mediaPlaylist.setPlaylist(playlist, index)
        self.play()

    def showEvent(self, e):
        if hasattr(self, 'smallestPlayInterface'):
            self.smallestPlayInterface.hide()
        super().showEvent(e)

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
            self.titleBar.returnButton.click()
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
                content = self.tr(
                    "This song is already in your playlist. Do you want to add?")
            elif repeatNum < planToAddNum:
                content = self.tr(
                    "Some songs are already in your playlist. Do you want to add?")
            else:
                content = self.tr(
                    "All these songs are already in your playlist. Do you want to add?")

            w = MessageDialog(self.tr("Song duplication"), content, self)
            w.cancelSignal.connect(lambda: resetSongInfo(
                songInfo_list, differentSongInfo_list))
            w.exec_()

        self.playlistCardInterface.addSongsToPlaylist(
            playlistName, songInfo_list)

    def onNavigationLabelClicked(self, label: str):
        """ 导航标签点击槽函数 """
        self.myMusicInterface.scrollToLabel(label)
        self.subStackWidget.setCurrentWidget(
            self.subStackWidget.previousWidget)
        # 弹出导航历史
        self.navigationHistories.pop()

    def onRescanSongInfoTimeOut(self):
        """ 重新扫描歌曲信息 """
        if self.isInSelectionMode or not self.myMusicInterface.hasSongModified():
            return

        w = StateTooltip(self.tr("Updating song list"),
                         self.tr("Please wait patiently"), self)
        w.move(w.getSuitablePos())
        w.show()
        self.myMusicInterface.rescanSongInfo()
        self.songTabSongListWidget.setPlayBySongInfo(
            self.mediaPlaylist.getCurrentSong())
        w.setState(True)

    def deleteSongs(self, songPaths: list):
        """ 删除歌曲 """
        self.playlistCardInterface.deleteSongs(songPaths)
        if self.sender() in [self.searchResultInterface, self.singerInterface]:
            self.myMusicInterface.deleteSongs(songPaths)
            if self.sender() is self.singerInterface and not self.singerInterface.albumInfo_list:
                self.titleBar.returnButton.click()

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

    def onDownloadFinished(self, downloadFolder):
        """ 下载完成槽函数 """
        downloadFolder = Path(downloadFolder).absolute()
        musicFolders = [Path(i).absolute()
                        for i in self.settingInterface.config['selected-folders']]
        needUpdate = any([downloadFolder == i for i in musicFolders])
        if needUpdate:
            self.myMusicInterface.rescanSongInfo()
            self.songTabSongListWidget.setPlayBySongInfo(
                self.mediaPlaylist.getCurrentSong())

    def onMediaStatusChanged(self, status: QMediaPlayer.MediaStatus):
        """ 媒体状态改变槽函数 """
        if status != QMediaPlayer.NoMedia:
            return
        self.setPlayButtonState(False)

    def onExit(self):
        """ 退出界面前保存信息 """
        config = {}
        config["volume"] = self.playBar.volumeSlider.value()
        config["playBar-color"] = list(
            self.playBar.getColor().getRgb()[:3])

        self.settingInterface.updateConfig(config)
        self.mediaPlaylist.save()
        qApp.exit()

    def getOnlineSongUrl(self, index: int):
        """ 获取在线音乐播放地址 """
        if index < 0 or not self.mediaPlaylist.playlist:
            return

        songInfo = self.mediaPlaylist.playlist[index]
        if songInfo['songPath'] != CrawlerBase.song_url_mark:
            return

        i = self.searchResultInterface.onlineSongInfo_list.index(songInfo)
        songCard = self.searchResultInterface.onlineSongListWidget.songCard_list[i]

        # 获取封面和播放地址
        eventLoop = QEventLoop(self)
        self.getOnlineSongUrlThread.finished.connect(eventLoop.quit)
        self.getOnlineSongUrlThread.setSongInfo(
            songInfo, self.searchResultInterface.onlinePlayQuality)
        self.getOnlineSongUrlThread.start()
        eventLoop.exec()

        # TODO：更优雅地更新在线媒体
        songInfo['songPath'] = self.getOnlineSongUrlThread.playUrl
        songInfo['coverPath'] = self.getOnlineSongUrlThread.coverPath
        songCard.setSongInfo(songInfo)
        self.mediaPlaylist.insertSong(index, songInfo)
        self.playingInterface.playlist[index] = songInfo
        self.smallestPlayInterface.playlist[index] = songInfo
        self.searchResultInterface.onlineSongInfo_list[i] = songInfo
        self.mediaPlaylist.removeOnlineSong(index+1)
        self.mediaPlaylist.setCurrentIndex(index)

    def onMinimizeToTrayChanged(self, isMinimize: bool):
        """ 最小化到托盘改变槽函数 """
        QApplication.setQuitOnLastWindowClosed(not isMinimize)

    def onUpdateLyricPosTimeOut(self):
        """ 更新歌词位置 """
        if self.player.state() != QMediaPlayer.PlayingState:
            return

        t = self.player.position()
        self.playingInterface.lyricWidget.setCurrentTime(t)

    def connectSignalToSlot(self):
        """ 将信号连接到槽 """

        # 将播放器的信号连接到槽函数
        self.player.positionChanged.connect(self.onPlayerPositionChanged)
        self.player.durationChanged.connect(self.onPlayerDurationChanged)
        self.player.mediaStatusChanged.connect(self.onMediaStatusChanged)

        # 将播放列表的信号连接到槽函数
        self.mediaPlaylist.currentIndexChanged.connect(self.getOnlineSongUrl)
        self.mediaPlaylist.currentIndexChanged.connect(self.updateWindow)

        # 将设置界面信号连接到槽函数
        self.settingInterface.crawlComplete.connect(
            self.myMusicInterface.rescanSongInfo)
        self.settingInterface.acrylicEnableChanged.connect(
            self.setWindowEffect)
        self.settingInterface.selectedMusicFoldersChanged.connect(
            self.myMusicInterface.scanTargetPathSongInfo)
        self.settingInterface.downloadFolderChanged.connect(
            self.searchResultInterface.setDownloadFolder)
        self.settingInterface.onlinePlayQualityChanged.connect(
            self.searchResultInterface.setOnlinePlayQuality)
        self.settingInterface.pageSizeChanged.connect(
            self.searchResultInterface.setOnlineMusicPageSize)
        self.settingInterface.mvQualityChanged.connect(
            self.playingInterface.getMvUrlThread.setVideoQuality)
        self.settingInterface.minimizeToTrayChanged.connect(
            self.onMinimizeToTrayChanged)

        # 将标题栏返回按钮点击信号连接到槽函数
        self.titleBar.returnButton.clicked.connect(self.onReturnButtonClicked)

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
        self.playingInterface.clearPlaylistSig.connect(self.clearPlaylist)
        self.playingInterface.removeSongSignal.connect(
            self.mediaPlaylist.removeSong)
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
        self.playingInterface.switchToVideoInterfaceSig.connect(
            self.showVideoWindow)

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
            self.onMyMusicInterfaceStackWidgetIndexChanged)
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
        self.rescanSongInfoTimer.timeout.connect(self.onRescanSongInfoTimeOut)
        self.updateLyricPosTimer.timeout.connect(self.onUpdateLyricPosTimeOut)

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
        self.searchResultInterface.downloadFinished.connect(
            self.onDownloadFinished)

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

        # 将系统托盘图标信号连接到槽函数
        qApp.aboutToQuit.connect(self.systemTrayIcon.hide)
        self.systemTrayIcon.exitSignal.connect(self.onExit)
        self.systemTrayIcon.showMainWindowSig.connect(self.show)
        self.systemTrayIcon.togglePlayStateSig.connect(self.togglePlayState)
        self.systemTrayIcon.lastSongSig.connect(self.mediaPlaylist.previous)
        self.systemTrayIcon.nextSongSig.connect(self.mediaPlaylist.next)
        self.systemTrayIcon.switchToSettingInterfaceSig.connect(
            self.switchToSettingInterface)
        self.systemTrayIcon.showPlayingInterfaceSig.connect(
            self.showPlayingInterface)

        # 将视频界面信号连接到槽函数
        self.videoWindow.fullScreenChanged.connect(self.setVideoFullScreen)


class SplashScreen(QWidget):
    """ 启动界面 """

    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.hBoxLayout = QHBoxLayout(self)
        self.logo = QLabel(self)
        self.logo.setPixmap(QPixmap(":/images/logo/splash_screen_logo.png"))
        self.hBoxLayout.addWidget(self.logo, 0, Qt.AlignCenter)
        self.setAttribute(Qt.WA_StyledBackground)
        self.setStyleSheet('background:white')
