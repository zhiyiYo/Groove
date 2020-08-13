# coding:utf-8

import sys
from ctypes import POINTER, Structure, cast
from ctypes.wintypes import HWND, MSG, POINT, UINT
from enum import Enum
from random import shuffle
from shutil import rmtree
from time import time

from PyQt5.QtCore import (QAbstractAnimation, QPoint, QRect, QSize, Qt, QUrl,
                          pyqtSignal)
from PyQt5.QtGui import QCloseEvent, QFont, QIcon, QPixmap, QResizeEvent
from PyQt5.QtMultimedia import QMediaPlayer, QMediaPlaylist
from PyQt5.QtWidgets import (QAction, QApplication, QGraphicsDropShadowEffect,
                             QStackedWidget, QWidget)
from system_hotkey import SystemHotkey
from win32 import win32api, win32gui
from win32.lib import win32con

from effects import WindowEffect
from media_player import MediaPlaylist, PlaylistType
from my_music_interface import MyMusicInterface
from my_play_bar import PlayBar
from my_playing_interface import CreateSongCardsThread, PlayingInterface
from my_setting_interface import SettingInterface
from my_sub_play_window import SubPlayWindow
from my_album_interface import AlbumInterface
from my_thumbnail_tool_bar import ThumbnailToolBar
from my_title_bar import TitleBar
from navigation import NavigationBar, NavigationMenu

from .c_structures import MINMAXINFO
from .monitor_functions import isMaximized


class MainWindow(QWidget):
    """ 主窗口 """
    BORDER_WIDTH = 5
    showSubPlayWindowSig = pyqtSignal()

    def __init__(self, parent=None):
        super().__init__(parent)
        # 实例化窗口特效
        self.windowEffect = WindowEffect()
        # 实例化小部件
        self.createWidgets()
        # 初始化界面
        self.__initWidget()

    def createWidgets(self):
        """ 创建小部件 """
        self.totalStackWidget = QStackedWidget(self)
        self.subMainWindow = QWidget(self)
        # 实例化播放器和播放列表
        self.player = QMediaPlayer(self)
        self.playlist = MediaPlaylist(self)
        # 实例化小部件
        self.subStackWidget = QStackedWidget(self.subMainWindow)
        self.settingInterface = SettingInterface(self.subMainWindow)
        self.navigationBar = NavigationBar(self.subMainWindow)
        # 需要先实例化导航栏，再将导航栏和导航菜单关联
        self.navigationMenu = NavigationMenu(
            self.navigationBar, self.subMainWindow)
        # 关联两个导航部件
        self.navigationBar.setBoundNavigationMenu(self.navigationMenu)
        self.currentNavigation = self.navigationBar
        # 从配置文件中的选择文件夹读取音频文件
        t3 = time()
        self.myMusicInterface = MyMusicInterface(
            self.settingInterface.config.get('selected-folders', []), self.subMainWindow)
        t4 = time()
        print('创建整个我的音乐界面所花时间：', t4 - t3)
        # 将最后一首歌作为playBar初始化时用的songInfo
        self.lastSongInfo = self.settingInterface.config.get('last-song', {})
        self.titleBar = TitleBar(self)
        self.playBar = PlayBar(self.lastSongInfo, self)
        # 实例化缩略图任务栏
        self.thumbnailToolBar = ThumbnailToolBar(self)
        self.thumbnailToolBar.setWindow(self.windowHandle())
        # 实例化左上角播放窗口
        self.subPlayWindow = SubPlayWindow(self, self.lastSongInfo)
        # 创建正在播放界面
        self.playingInterface = PlayingInterface(self.playlist.playlist, self)
        # 创建专辑界面
        self.albumInterface = AlbumInterface({}, self.subMainWindow)
        # 创建快捷键
        self.playAct = QAction(
            parent=self, shortcut=Qt.Key_Space, triggered=self.switchPlayState)
        self.showNormalAct = QAction(
            parent=self, shortcut=Qt.Key_Escape, triggered=self.exitFullScreen)
        self.addAction(self.playAct)
        self.addAction(self.showNormalAct)
        # 创建stackWidget字典
        self.stackWidget_dict = {'subStackWidget': self.subStackWidget,
                                 'myMusicInterfaceStackWidget': self.myMusicInterface.myMusicTabWidget.stackedWidget}

    def __initWidget(self):
        """ 初始化小部件 """
        self.resize(1300, 970)
        self.setMinimumWidth(1030)
        self.setWindowTitle('Groove音乐')
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.setWindowIcon(QIcon('resource\\images\\透明icon.png'))
        self.setAttribute(Qt.WA_TranslucentBackground | Qt.WA_StyledBackground)
        # 在去除任务栏的显示区域居中显示
        desktop = QApplication.desktop().availableGeometry()
        self.move(int(desktop.width() / 2 - self.width() / 2),
                  int(desktop.height() / 2 - self.height() / 2))
        # 标题栏置顶
        self.titleBar.raise_()
        # 隐藏导航菜单
        self.navigationMenu.hide()
        self.navigationBar.musicGroupButton.isSelected = True
        self.navigationMenu.musicGroupButton.isSelected = True
        # 设置窗口特效
        self.setWindowEffect()
        # todo:将窗口添加到StackWidget中
        self.subStackWidget.addWidget(self.myMusicInterface)
        self.subStackWidget.addWidget(self.settingInterface)
        self.subStackWidget.addWidget(self.albumInterface)
        self.subStackWidget.setCurrentWidget(self.myMusicInterface)
        self.totalStackWidget.addWidget(self.subMainWindow)
        self.totalStackWidget.addWidget(self.playingInterface)
        # 初始化标题栏的下标列表
        self.titleBar.stackWidgetIndex_list.append(
            ('myMusicInterfaceStackWidget', 0))
        # 设置右边子窗口的位置
        self.setWidgetGeometry()
        # 引用小部件
        self.referenceWidgets()
        # 初始化播放列表
        self.initPlaylist()
        # 设置全局热键
        self.setHotKey()
        # 设置层叠样式
        self.setObjectName('mainWindow')
        self.subMainWindow.setObjectName('subMainWindow')
        self.playingInterface.setObjectName('playingInterface')
        self.setQss()
        # 将按钮点击信号连接到槽函数
        self.connectSignalToSlot()
        # 初始化播放栏
        self.initPlayBar()
        # 创建正在播放界面的歌曲卡
        self.playingInterface.createSongCardThread.run()

    def setHotKey(self):
        """ 设置全局热键 """
        self.nextSongHotKey = SystemHotkey()
        self.lastSongHotKey = SystemHotkey()
        self.playHotKey = SystemHotkey()
        # callback会返回一个event参数，所以需要用lambda
        self.nextSongHotKey.register(
            ('f6',), callback=lambda x: self.hotKeySlot(self.playlist.next))
        self.lastSongHotKey.register(
            ('f4',), callback=lambda x: self.hotKeySlot(self.playlist.previous))
        self.playHotKey.register(
            ('f5',), callback=lambda x: self.hotKeySlot(self.switchPlayState))

    def setWindowEffect(self):
        """ 设置窗口特效 """
        self.hWnd = HWND(int(self.winId()))
        # 开启窗口动画
        self.windowEffect.setWindowAnimation(int(self.winId()))
        # 开启亚克力效果和阴影效果
        self.windowEffect.setAcrylicEffect(self.hWnd, 'F2F2F290', True)

    def setWidgetGeometry(self):
        """ 调整小部件的geometry """
        self.subMainWindow.resize(self.size())
        self.totalStackWidget.resize(self.size())
        self.titleBar.resize(self.width(), 40)
        self.navigationBar.resize(60, self.height())
        self.navigationMenu.resize(400, self.height())
        self.subStackWidget.move(self.currentNavigation.width(), 0)
        self.subStackWidget.resize(
            self.width() - self.currentNavigation.width(), self.height())
        self.myMusicInterface.resize(
            self.width() - self.currentNavigation.width(), self.height())
        if hasattr(self, 'albumInterface'):
            self.albumInterface.resize(self.myMusicInterface.size())
        if hasattr(self, 'playingInterface'):
            self.playingInterface.resize(self.size())
        if hasattr(self, 'playBar'):
            self.playBar.resize(self.width(), self.playBar.height())

    def resizeEvent(self, e: QResizeEvent):
        """ 调整尺寸时同时调整子窗口的尺寸 """
        super().resizeEvent(e)
        self.setWidgetGeometry()
        # 更新标题栏图标
        if isMaximized(int(self.winId())):
            self.titleBar.maxBt.setMaxState(True)

    def showNavigationMenu(self):
        """ 显示导航菜单和抬头 """
        self.currentNavigation = self.navigationMenu
        self.navigationBar.hide()
        self.navigationMenu.show()
        if self.titleBar.returnBt.isVisible():
            self.titleBar.title.move(self.titleBar.returnBt.width(), 0)
        else:
            self.titleBar.title.move(0, 0)
        self.titleBar.title.show()
        self.setWidgetGeometry()
        if self.sender() == self.navigationBar.searchButton:
            self.navigationMenu.searchLineEdit.setFocus()

    def showNavigationBar(self):
        """ 显示导航栏 """
        self.currentNavigation = self.navigationBar
        self.navigationMenu.hide()
        self.titleBar.title.hide()
        self.navigationBar.show()
        self.setWidgetGeometry()

    def moveEvent(self, e):
        if hasattr(self, 'playBar'):
            if not self.isMaximized():
                self.playBar.move(self.x() - 8, self.y() +
                                  self.height() - self.playBar.height())
            else:
                self.playBar.move(self.x()+1, self.y() +
                                  self.height() - self.playBar.height() + 9)

    def closeEvent(self, e: QCloseEvent):
        """ 关闭窗口前更新json文件 """
        if self.playlist.currentIndex() >= 0:
            self.settingInterface.config['last-song'] = self.playlist.playlist[
                self.playlist.currentIndex()]
        else:
            self.settingInterface.config['last-song'] = {}
        self.settingInterface.config['volume'] = self.playBar.volumeSlider.value(
        )
        self.settingInterface.config['position'] = self.playBar.progressSlider.value(
        )
        self.settingInterface.config['duration'] = self.playBar.progressSlider.maximum(
        )
        self.settingInterface.config['playBar-acrylicColor'] = self.playBar.acrylicColor
        self.settingInterface.writeConfig()
        self.playBar.close()
        self.subPlayWindow.close()
        self.playlist.save()
        e.accept()

    def nativeEvent(self, eventType, message):
        """ 处理windows消息 """
        msg = MSG.from_address(message.__int__())
        if msg.message == win32con.WM_NCHITTEST:
            xPos = win32api.LOWORD(msg.lParam) - self.frameGeometry().x()
            yPos = win32api.HIWORD(msg.lParam) - self.frameGeometry().y()
            w, h = self.width(), self.height()
            lx = xPos < self.BORDER_WIDTH
            rx = xPos + 9 > w - self.BORDER_WIDTH
            ty = yPos < self.BORDER_WIDTH
            by = yPos > h - self.BORDER_WIDTH
            if (lx and ty):
                return True, win32con.HTTOPLEFT
            elif (rx and by):
                return True, win32con.HTBOTTOMRIGHT
            elif (rx and ty):
                return True, win32con.HTTOPRIGHT
            elif (lx and by):
                return True, win32con.HTBOTTOMLEFT
            elif ty:
                return True, win32con.HTTOP
            elif by:
                return True, win32con.HTBOTTOM
            elif lx:
                return True, win32con.HTLEFT
            elif rx:
                return True, win32con.HTRIGHT
        elif msg.message == win32con.WM_NCCALCSIZE:
            if isMaximized(msg.hWnd):
                self.windowEffect.adjustMaximizedClientRect(
                    HWND(msg.hWnd), msg.lParam)
            return True, 0
        if msg.message == win32con.WM_GETMINMAXINFO:
            if isMaximized(msg.hWnd):
                window_rect = win32gui.GetWindowRect(msg.hWnd)
                if not window_rect:
                    return False, 0
                # 获取显示器句柄
                monitor = win32api.MonitorFromRect(window_rect)
                if not monitor:
                    return False, 0
                # 获取显示器信息
                monitor_info = win32api.GetMonitorInfo(monitor)
                monitor_rect = monitor_info['Monitor']
                work_area = monitor_info['Work']
                # 将lParam转换为MINMAXINFO指针
                info = cast(
                    msg.lParam, POINTER(MINMAXINFO)).contents
                # 调整位置
                info.ptMaxSize.x = work_area[2] - work_area[0]
                info.ptMaxSize.y = work_area[3] - work_area[1]
                info.ptMaxTrackSize.x = info.ptMaxSize.x
                info.ptMaxTrackSize.y = info.ptMaxSize.y
                # 修改放置点的x,y坐标
                info.ptMaxPosition.x = abs(
                    window_rect[0] - monitor_rect[0])
                info.ptMaxPosition.y = abs(
                    window_rect[1] - monitor_rect[1])
                return True, 1
        return QWidget.nativeEvent(self, eventType, message)

    def connectSignalToSlot(self):
        """ 将信号连接到槽 """
        # 爬虫完成工作时更新歌曲卡信息
        self.settingInterface.crawlComplete.connect(
            self.crawCompleteSlot)
        # todo: 标题栏返回按钮功能
        self.titleBar.returnBt.clicked.connect(
            self.returnButtonSlot)
        # todo:导航栏按钮功能
        self.navigationBar.showMenuButton.clicked.connect(
            self.showNavigationMenu)
        self.navigationBar.searchButton.clicked.connect(
            self.showNavigationMenu)
        self.navigationBar.musicGroupButton.clicked.connect(
            lambda: self.subStackWidget.setCurrentWidget(self.myMusicInterface))
        self.navigationBar.playingButton.clicked.connect(
            self.showPlayingInterface)
        self.navigationBar.settingButton.clicked.connect(
            lambda: self.subStackWidget.setCurrentWidget(self.settingInterface))
        # todo:导航菜单功能
        self.navigationMenu.showBarButton.clicked.connect(
            self.showNavigationBar)
        self.navigationMenu.musicGroupButton.clicked.connect(
            lambda: self.subStackWidget.setCurrentWidget(self.myMusicInterface))
        self.navigationMenu.playingButton.clicked.connect(
            self.showPlayingInterface)
        self.navigationMenu.settingButton.clicked.connect(
            lambda: self.subStackWidget.setCurrentWidget(self.settingInterface))
        # todo:缩略图任务栏各按钮的功能
        self.thumbnailToolBar.playButton.clicked.connect(self.switchPlayState)
        self.thumbnailToolBar.lastSongButton.clicked.connect(
            self.playlist.previous)
        self.thumbnailToolBar.nextSongButton.clicked.connect(
            self.playlist.next)
        # todo:播放栏各部件功能
        self.playBar.songInfoCard.clicked.connect(self.showPlayingInterface)
        self.playBar.randomPlayButton.clicked.connect(self.setRandomPlay)
        self.playBar.nextSongButton.clicked.connect(self.playlist.next)
        self.playBar.lastSongButton.clicked.connect(self.playlist.previous)
        self.playBar.playButton.clicked.connect(self.switchPlayState)
        self.playBar.volumeButton.muteStateChanged.connect(self.setMute)
        self.playBar.volumeSlider.valueChanged.connect(self.volumeChangedSlot)
        self.playBar.progressSlider.sliderMoved.connect(
            self.progressSliderMoveSlot)
        self.playBar.progressSlider.clicked.connect(
            self.progressSliderMoveSlot)
        self.playBar.loopModeButton.loopModeChanged.connect(
            self.switchLoopMode)
        self.playBar.moreActionsMenu.fillScreenAct.triggered.connect(
            self.setFullScreen)
        self.playBar.moreActionsMenu.showPlayListAct.triggered.connect(
            self.showPlaylist)
        self.playBar.moreActionsMenu.clearPlayListAct.triggered.connect(
            self.clearPlaylist)
        self.playBar.songInfoCard.clicked.connect(self.showPlayingInterface)
        # todo:将播放器的信号连接到槽函数
        self.player.positionChanged.connect(self.playerPositionChangeSlot)
        self.player.durationChanged.connect(self.playerDurationChangeSlot)
        # todo:将播放列表的信号连接到槽函数
        self.playlist.switchSongSignal.connect(self.updateWindow)
        self.playlist.currentIndexChanged.connect(
            self.playingInterface.setCurrentIndex)
        # todo:将正在播放界面信号连接到槽函数
        self.playingInterface.currentIndexChanged.connect(
            self.playingInterfaceCurrrentIndexChangedSlot)
        self.playingInterface.playBar.playButton.clicked.connect(
            self.switchPlayState)
        self.playingInterface.playBar.lastSongButton.clicked.connect(
            self.playlist.previous)
        self.playingInterface.playBar.nextSongButton.clicked.connect(
            self.playlist.next)
        self.playingInterface.playBar.randomPlayButton.clicked.connect(
            self.setRandomPlay)
        self.playingInterface.playBar.volumeSlider.muteStateChanged.connect(
            self.setMute)
        self.playingInterface.playBar.volumeSlider.volumeSlider.valueChanged.connect(
            self.volumeChangedSlot)
        self.playingInterface.playBar.progressSlider.sliderMoved.connect(
            self.progressSliderMoveSlot)
        self.playingInterface.playBar.progressSlider.clicked.connect(
            self.progressSliderMoveSlot)
        self.playingInterface.playBar.fillScreenButton.clicked.connect(
            self.setFullScreen)
        self.playingInterface.playBar.loopModeButton.loopModeChanged.connect(
            self.switchLoopMode)
        self.playingInterface.createSongCardThread.createDone.connect(
            lambda: self.playingInterface.setCurrentIndex(self.playlist.currentIndex()))
        self.playingInterface.removeMediaSignal.connect(
            self.playlist.removeMedia)
        self.playingInterface.randomPlayAllSignal.connect(self.disorderPlayAll)
        self.playingInterface.switchToAlbumInterfaceSig.connect(
            self.switchToAlbumInterface)
        # todo:歌曲界面歌曲卡列表视图的信号连接到槽函数
        self.songCardListWidget.playSignal.connect(
            self.songCardPlayButtonSlot)
        self.songCardListWidget.nextPlaySignal.connect(
            self.songCardNextPlaySlot)
        self.songCardListWidget.addSongToPlaylistSignal.connect(
            self.addSongToPlaylist)
        self.songCardListWidget.switchToAlbumInterfaceSig.connect(
            self.switchToAlbumInterface)
        self.songCardListWidget.editSongCardSignal.connect(
            self.editSongCardSlot)
        # todo:将专辑卡的信号连接到槽函数
        self.albumCardViewer.playSignal.connect(self.playAlbum)
        self.albumCardViewer.nextPlaySignal.connect(self.albumCardNextPlaySlot)
        self.albumCardViewer.addAlbumToPlaylistSignal.connect(
            self.addAlbumToPlaylist)
        self.albumCardViewer.switchToAlbumInterfaceSig.connect(
            self.__switchToAlbumInterface)
        # todo:将子播放窗口的信号连接槽槽函数
        self.subPlayWindow.nextSongButton.clicked.connect(self.playlist.next)
        self.subPlayWindow.lastSongButton.clicked.connect(
            self.playlist.previous)
        self.subPlayWindow.playButton.clicked.connect(self.switchPlayState)
        # todo:将无序播放所有信号连接到槽函数
        self.myMusicInterface.myMusicTabWidget.randomPlayAllSig.connect(
            self.disorderPlayAll)
        # todo:将自己的信号连接到槽函数
        self.showSubPlayWindowSig.connect(lambda: self.subPlayWindow.show())
        # todo:将专辑界面的信号连接到槽函数
        self.albumInterface.playAlbumSignal.connect(self.playAlbum)
        self.albumInterface.songCardPlaySig.connect(
            self.albumInterfaceSongCardPlaySlot)
        self.albumInterface.nextToPlaySignal.connect(self.songCardNextPlaySlot)
        self.albumInterface.addSongToPlaylistSig.connect(
            self.addSongToPlaylist)
        self.albumInterface.addAlbumToPlaylistSig.connect(
            self.addAlbumToPlaylist)
        self.albumInterface.songListWidget.editSongCardSignal.connect(
            self.editSongCardSlot)
        # todo:将主动切换界面的信号连接到槽函数
        self.navigationBar.currentIndexChanged.connect(
            self.stackWidgetIndexChangedSlot)
        self.navigationMenu.currentIndexChanged.connect(
            self.stackWidgetIndexChangedSlot)
        self.myMusicInterface.currentIndexChanged.connect(
            self.stackWidgetIndexChangedSlot)

    def referenceWidgets(self):
        """ 引用小部件 """
        self.songCardListWidget = self.myMusicInterface.myMusicTabWidget.songTab.songCardListWidget
        # self.songerCardViewer = self.myMusicInterface.myMusicTabWidget.songerTab.songerHeadPortraitViewer
        self.albumCardViewer = self.myMusicInterface.myMusicTabWidget.albumTab.albumCardViewer
        self.albumInfo_list = self.albumCardViewer.albumInfo.albumInfo_list

    def initPlaylist(self):
        """ 初始化播放列表 """
        self.player.setPlaylist(self.playlist)
        # 如果没有上一次的播放列表数据，就设置默认的播放列表
        if not self.playlist.playlist:
            songInfo_list = self.songCardListWidget.songInfo.songInfo_list.copy()
            self.playingInterface.setPlaylist(songInfo_list)
            self.playlist.setMedias(songInfo_list)
            self.playlist.playlistType = PlaylistType.SONG_CARD_PLAYLIST
        # 将当前歌曲设置为上次关闭前播放的歌曲
        if self.lastSongInfo in self.playlist.playlist:
            self.playlist.setCurrentIndex(
                self.playlist.playlist.index(self.lastSongInfo))

    def switchPlayState(self):
        """ 播放按钮按下时根据播放器的状态来决定是暂停还是播放 """
        if self.player.state() == QMediaPlayer.PlayingState:
            self.player.pause()
            self.setPlayButtonState(False)
            self.thumbnailToolBar.setButtonsEnabled(True)
        else:
            self.play()

    def setPlayButtonState(self, isPlay: bool):
        """ 设置播放按钮状态 """
        self.subPlayWindow.setPlay(isPlay)
        self.playBar.playButton.setPlay(isPlay)
        self.thumbnailToolBar.playButton.setPlay(isPlay)
        self.playingInterface.playBar.playButton.setPlay(isPlay)

    def volumeChangedSlot(self, value):
        """ 音量滑动条数值改变时更换图标并设置音量 """
        self.player.setVolume(value)
        self.playBar.volumeButton.setVolumeLevel(value)
        if self.sender() == self.playBar.volumeSlider:
            self.playingInterface.playBar.volumeSlider.setValue(value)
        elif self.sender() == self.playingInterface.playBar.volumeSlider.volumeSlider:
            self.playBar.volumeSlider.setValue(value)

    def playerPositionChangeSlot(self):
        """ 播放器的播放进度改变时更新当前播放进度标签和进度条的值 """
        self.playBar.progressSlider.setValue(self.player.position())
        self.playBar.setCurrentTime(self.player.position())
        self.playingInterface.playBar.progressSlider.setValue(
            self.player.position())
        self.playingInterface.playBar.setCurrentTime(self.player.position())

    def playerDurationChangeSlot(self):
        """ 播放器当前播放的歌曲变化时更新进度条的范围和总时长标签 """
        # 刚切换时得到的时长为0，所以需要先判断一下
        if self.player.duration() >= 1:
            self.playBar.setTotalTime(self.player.duration())
            self.playBar.progressSlider.setRange(0, self.player.duration())
            self.playingInterface.playBar.progressSlider.setRange(
                0, self.player.duration())
            self.playingInterface.playBar.setTotalTime(self.player.duration())

    def progressSliderMoveSlot(self):
        """ 手动拖动进度条时改变当前播放进度标签和播放器的值 """
        if self.sender() == self.playBar.progressSlider:
            self.player.setPosition(self.playBar.progressSlider.value())
        elif self.sender() == self.playingInterface.playBar.progressSlider:
            self.player.setPosition(
                self.playingInterface.playBar.progressSlider.value())
        self.playBar.setCurrentTime(self.player.position())
        self.playingInterface.playBar.setCurrentTime(self.player.position())

    def songCardPlayButtonSlot(self, songInfo_dict):
        """ 歌曲卡的播放按钮按下时播放这首歌 """
        self.switchCurrentSong(songInfo_dict)

    def songCardNextPlaySlot(self, songInfo_dict):
        """ 下一首播放动作触发对应的槽函数 """
        # 直接更新正在播放界面的播放列表
        newPlaylist = self.playlist.playlist[:self.playlist.currentIndex(
        ) + 1] + [songInfo_dict] + self.playlist.playlist[self.playlist.currentIndex() + 1:]
        self.playingInterface.setPlaylist(newPlaylist)
        self.playingInterface.setCurrentIndex(self.playlist.currentIndex())
        self.playlist.insertMedia(
            self.playlist.currentIndex() + 1, songInfo_dict)

    def switchCurrentSong(self, songInfo_dict: dict):
        """ 切换当前播放的歌曲 """
        newPlaylist = None
        # 如果当前播放列表模式不是歌曲界面的歌曲卡模式，就刷新播放列表
        if self.playlist.playlistType != PlaylistType.SONG_CARD_PLAYLIST:
            index = self.songCardListWidget.songInfo.songInfo_list.index(
                songInfo_dict)
            newPlaylist = self.songCardListWidget.songInfo.songInfo_list[index:] + \
                self.songCardListWidget.songInfo.songInfo_list[0:index]
            self.playingInterface.setPlaylist(newPlaylist)
        self.playlist.playThisSong(
            songInfo_dict, newPlaylist, PlaylistType.SONG_CARD_PLAYLIST)
        self.play()

    def switchLoopMode(self, loopMode):
        """ 根据随机播放按钮的状态和循环模式的状态决定播放器的播放模式 """
        # 记录按下随机播放前的循环模式
        self.playlist.prePlayMode = loopMode
        # 更新按钮样式
        if self.sender() == self.playBar.loopModeButton:
            self.playingInterface.playBar.loopModeButton.setLoopMode(loopMode)
        elif self.sender() == self.playingInterface.playBar.loopModeButton:
            self.playBar.loopModeButton.setLoopMode(loopMode)
        if not self.playlist.randPlayBtPressed:
            # 随机播放按钮没按下时，直接设置播放模式为循环模式按钮的状态
            self.playlist.setPlaybackMode(loopMode)
        else:
            # 随机播放按钮按下时，如果选了单曲循环就直接设置为单曲循环，否则设置为随机播放
            if self.playBar.loopModeButton.loopMode == QMediaPlaylist.CurrentItemInLoop:
                self.playlist.setPlaybackMode(QMediaPlaylist.CurrentItemInLoop)
            else:
                self.playlist.setPlaybackMode(QMediaPlaylist.Random)

    def setRandomPlay(self):
        """ 选择随机播放模式 """
        isRandomPlay = self.sender().isSelected
        self.playlist.setRandomPlay(isRandomPlay)
        if self.sender() == self.playBar.randomPlayButton:
            self.playingInterface.playBar.randomPlayButton.setRandomPlay(
                isRandomPlay)
        elif self.sender() == self.playingInterface.playBar.randomPlayButton:
            self.playBar.randomPlayButton.setRandomPlay(isRandomPlay)

    def updateWindow(self, songInfo):
        """ 切换歌曲时更新歌曲卡、播放栏和子播放窗口 """
        self.playBar.updateSongInfoCard(songInfo)
        self.subPlayWindow.updateWindow(songInfo)
        index = self.songCardListWidget.songInfo.songInfo_list.index(songInfo)
        self.songCardListWidget.setPlay(index)
        # 更新专辑界面的歌曲卡
        if songInfo in self.albumInterface.songListWidget.songInfo_list:
            index = self.albumInterface.songListWidget.songInfo_list.index(
                songInfo)
            self.albumInterface.songListWidget.setPlay(index)

    def hotKeySlot(self, funcObj):
        """ 热键按下时显示子播放窗口并执行对应操作 """
        funcObj()
        self.showSubPlayWindowSig.emit()

    def playAlbum(self, playlist: list):
        """ 播放专辑中的歌曲 """
        # 直接更新播放列表
        self.playingInterface.setPlaylist(playlist)
        self.playlist.playAlbum(playlist)
        self.play()

    def albumCardNextPlaySlot(self, songInfoDict_list):
        """ 下一首播放动作触发对应的槽函数 """
        newPlaylist = self.playlist.playlist[:self.playlist.currentIndex(
        ) + 1] + songInfoDict_list + self.playlist.playlist[self.playlist.currentIndex() + 1:]
        self.playingInterface.setPlaylist(newPlaylist)
        self.playingInterface.setCurrentIndex(self.playlist.currentIndex())
        self.playlist.insertMedias(
            self.playlist.currentIndex() + 1, songInfoDict_list)

    def disorderPlayAll(self):
        """ 无序播放所有 """
        self.playlist.playlistType = PlaylistType.SONG_CARD_PLAYLIST
        newPlaylist = self.songCardListWidget.songInfo.songInfo_list.copy()
        shuffle(newPlaylist)
        self.playingInterface.setPlaylist(newPlaylist)
        self.playlist.setMedias(newPlaylist)
        self.play()

    def play(self):
        """ 播放歌曲并改变按钮样式 """
        self.player.play()
        self.setPlayButtonState(True)
        # 显示被隐藏的歌曲信息卡
        if self.playlist.playlist:
            if not self.playBar.songInfoCard.isVisible() and self.playBar.isVisible():
                self.playBar.songInfoCard.show()
                self.playBar.songInfoCard.updateSongInfoCard(
                    self.playlist.playlist[0])

    def initPlayBar(self):
        """ 从配置文件中读取配置数据来初始化播放栏 """
        # 初始化音量
        volume = self.settingInterface.config.get('volume', 20)
        self.playBar.volumeSlider.setValue(volume)
        self.playingInterface.playBar.volumeSlider.setValue(volume)
        # 初始化亚克力颜色
        acrylicColor = self.settingInterface.config.get(
            'playBar-acrylicColor', '0a517aB8')
        self.playBar.setAcrylicColor(acrylicColor)

    def showPlayingInterface(self):
        """ 显示正在播放界面 """
        self.playBar.hide()
        self.titleBar.title.hide()
        self.titleBar.returnBt.show()
        self.titleBar.title.move(self.titleBar.returnBt.width(), 0)
        if not self.playingInterface.isPlaylistVisible:
            self.playingInterface.songInfoCardChute.move(0, 0)
            self.playingInterface.playBar.hide()
        self.totalStackWidget.setCurrentIndex(1)
        self.titleBar.setWhiteIcon(True)

    def hidePlayingInterface(self):
        """ 隐藏正在播放界面 """
        self.playBar.show()
        self.totalStackWidget.setCurrentIndex(0)
        # 根据当前界面设置标题栏按钮颜色
        if self.subStackWidget.currentWidget() == self.albumInterface:
            self.titleBar.returnBt.setWhiteIcon(False)
        else:
            self.titleBar.setWhiteIcon(False)
        # 隐藏返回按钮
        if len(self.titleBar.stackWidgetIndex_list) == 1 and self.subStackWidget.currentWidget() != self.albumInterface:
            self.titleBar.returnBt.hide()
        if self.navigationMenu.isVisible():
            self.titleBar.title.show()
        if not self.playingInterface.isPlaylistVisible:
            self.playingInterface.playBar.hide()
            self.playingInterface.songInfoCardChute.move(0, 0)

    def setQss(self):
        """ 设置层叠样式 """
        with open(r'resource\css\mainWindow.qss', encoding='utf-8') as f:
            self.setStyleSheet(f.read())

    def playingInterfaceCurrrentIndexChangedSlot(self, index):
        """ 正在播放界面下标变化槽函数 """
        self.playlist.setCurrentIndex(index)
        self.play()

    def setMute(self, isMute):
        """ 设置静音 """
        self.player.setMuted(isMute)
        if self.sender() == self.playBar.volumeButton:
            self.playingInterface.playBar.volumeButton.setMute(isMute)
            self.playingInterface.playBar.volumeSlider.volumeButton.setMute(
                isMute)
        elif self.sender() == self.playingInterface.playBar.volumeSlider:
            self.playBar.volumeButton.setMute(isMute)

    def setFullScreen(self):
        """ 设置全屏 """
        if not self.isFullScreen():
            # 更新标题栏
            self.playBar.hide()
            self.titleBar.title.hide()
            self.titleBar.setWhiteIcon(True)
            self.titleBar.hide()
            # 切换到正在播放界面
            self.totalStackWidget.setCurrentIndex(1)
            self.showFullScreen()
            self.playingInterface.playBar.fillScreenButton.setFillScreen(True)
            if self.playingInterface.isPlaylistVisible:
                self.playingInterface.songInfoCardChute.move(
                    0, 258 - self.height())
        else:
            self.exitFullScreen()

    def exitFullScreen(self):
        """ 退出全屏 """
        self.showNormal()
        # 更新最大化按钮图标
        self.titleBar.maxBt.setMaxState(False)
        self.titleBar.show()
        self.playingInterface.playBar.fillScreenButton.setFillScreen(False)
        if self.playingInterface.isPlaylistVisible:
            self.playingInterface.songInfoCardChute.move(
                0, 258 - self.height())

    def crawCompleteSlot(self):
        """ 爬虫完成信号槽函数 """
        self.songCardListWidget.updateSongCardInfo()
        # 爬取完成后直接删除旧的专辑封面文件夹
        # rmtree('resource\\Album_Cover')

    def showPlaylist(self):
        """ 显示正在播放界面的播放列表 """
        self.playingInterface.showPlaylist()
        # 调整歌曲列表的宽度
        self.playingInterface.songListWidget.resize(
            self.playingInterface.width()-60, self.playingInterface.height()-382)
        # 直接设置播放栏上拉箭头按钮箭头方向朝下
        self.playingInterface.playBar.pullUpArrowButton.setArrowDirection(
            'down')
        if self.playingInterface.isPlaylistVisible:
            self.showPlayingInterface()

    def clearPlaylist(self):
        """ 清空播放列表 """
        self.playlist.playlistType = PlaylistType.NO_PLAYLIST
        self.playlist.clear()
        self.playingInterface.clearPlaylist()

    def addSongToPlaylist(self, songInfo: dict):
        """ 向播放列表尾部添加一首歌 """
        self.playlist.addMedia(songInfo)
        self.playingInterface.setPlaylist(self.playlist.playlist)

    def addAlbumToPlaylist(self, songInfoDict_list: list):
        """ 向播放列表尾部添加专辑 """
        self.playlist.addMedias(songInfoDict_list)
        self.playingInterface.setPlaylist(self.playlist.playlist)

    def switchToAlbumInterface(self, album: str):
        """ 由专辑名切换到专辑界面 """
        albumInfo = self.albumCardViewer.albumInfo.getOneAlbumInfo(album)
        self.__switchToAlbumInterface(albumInfo)

    def __switchToAlbumInterface(self, albumInfo: dict):
        """ 由专辑信息切换到专辑界面 """
        # 显示返回按钮
        self.titleBar.returnBt.show()
        self.titleBar.title.move(self.titleBar.returnBt.width(), 0)
        self.albumInterface.updateWindow(albumInfo)
        self.subStackWidget.setCurrentWidget(self.albumInterface)
        self.totalStackWidget.setCurrentIndex(0)
        self.playBar.show()
        self.titleBar.setWhiteIcon(True)
        self.titleBar.returnBt.setWhiteIcon(False)
        # 根据当前播放的歌曲设置歌曲卡播放状态
        songInfo = self.playlist.playlist[self.playlist.currentIndex()]
        if songInfo in self.albumInterface.songInfo_list:
            index = self.albumInterface.songInfo_list.index(
                songInfo)
            self.albumInterface.songListWidget.setPlay(index)

    def albumInterfaceSongCardPlaySlot(self, index):
        """ 专辑界面歌曲卡播放按钮按下时 """
        albumSongList = self.albumInterface.songInfo_list
        # 播放模式不为专辑播放模式或者播放列表不同时直接刷新播放列表
        cond = self.playlist.playlistType != PlaylistType.ALBUM_CARD_PLAYLIST \
            or self.playlist.playlist != albumSongList
        if cond:
            self.playAlbum(albumSongList)
        self.playlist.setCurrentIndex(index)

    def returnButtonSlot(self):
        """ 标题栏返回按钮的槽函数 """
        if self.totalStackWidget.currentWidget() == self.playingInterface:
            self.hidePlayingInterface()
        else:
            # 当前界面不是albumInterface时弹出下标列表的最后一个下标
            if self.titleBar.stackWidgetIndex_list and self.subStackWidget.currentWidget() != self.albumInterface:
                self.titleBar.stackWidgetIndex_list.pop()
            if self.titleBar.stackWidgetIndex_list:
                stackWidgetName, index = self.titleBar.stackWidgetIndex_list[-1]
                self.stackWidget_dict[stackWidgetName].setCurrentIndex(index)
                if stackWidgetName == 'myMusicInterfaceStackWidget':
                    self.subStackWidget.setCurrentIndex(0)
                    self.navigationBar.setCurrentIndex(0)
                    self.navigationMenu.setCurrentIndex(0)
                    self.myMusicInterface.myMusicTabWidget.setSelectedButton(
                        index)
                elif stackWidgetName == 'subStackWidget':
                    self.navigationBar.setCurrentIndex(index)
                    self.navigationMenu.setCurrentIndex(index)
                if len(self.titleBar.stackWidgetIndex_list) == 1:
                    # 没有上一个下标时隐藏返回按钮
                    self.titleBar.returnBt.hide()
                    self.titleBar.title.move(0, 0)
        self.titleBar.setWhiteIcon(False)
        # 根据当前界面设置标题栏按钮颜色
        if self.subStackWidget.currentWidget() == self.albumInterface:
            self.titleBar.minBt.setWhiteIcon(True)
            self.titleBar.maxBt.setWhiteIcon(True)
            self.titleBar.closeBt.setWhiteIcon(True)

    def stackWidgetIndexChangedSlot(self, index):
        """ 堆叠窗口下标改变时的槽函数 """
        if self.sender() in [self.navigationBar, self.navigationMenu]:
            if self.subStackWidget.currentIndex() == index:
                return
            self.titleBar.stackWidgetIndex_list.append(
                ('subStackWidget', index))
        elif self.sender() == self.myMusicInterface:
            self.titleBar.stackWidgetIndex_list.append(
                ('myMusicInterfaceStackWidget', index))
        self.titleBar.returnBt.show()
        self.titleBar.title.move(self.titleBar.returnBt.width(), 0)

    def editSongCardSlot(self, oldSongInfo, newSongInfo):
        """ 编辑歌曲卡完成信号的槽函数 """
        if oldSongInfo in self.playlist.playlist:
            index = self.playlist.playlist.index(oldSongInfo)
            self.playlist.playlist[index] = newSongInfo
            self.playingInterface.updateOneSongCard(oldSongInfo, newSongInfo)
        if self.sender() == self.albumInterface.songListWidget:
            self.songCardListWidget.updateOneSongCard(oldSongInfo, newSongInfo)
        elif self.sender() == self.songCardListWidget:
            # 获取专辑信息并更新专辑界面和专辑信息
            albumInfo = self.albumCardViewer.albumInfo.updateOneAlbumSongInfo(newSongInfo)
            if albumInfo:
                self.albumInterface.updateWindow(albumInfo)
            self.albumInterface.updateOneSongCard(oldSongInfo, newSongInfo)
