# coding:utf-8

import sys
from ctypes.wintypes import HWND, MSG
from enum import Enum
from random import shuffle

from PyQt5.QtCore import QPoint, QRect, QSize, Qt, QUrl, pyqtSignal
from PyQt5.QtGui import QCloseEvent, QFont, QIcon, QPixmap, QResizeEvent
from PyQt5.QtMultimedia import QMediaPlayer, QMediaPlaylist
from PyQt5.QtWidgets import (QAction, QApplication, QGraphicsDropShadowEffect,
                             QStackedWidget, QWidget)
from system_hotkey import SystemHotkey

from effects import WindowEffect
from flags.wm_hittest import Flags
from media_player import MediaPlaylist, PlaylistType
from my_music_interface import MyMusicInterface
from my_play_bar import PlayBar
from my_setting_interface import SettingInterface
from my_sub_play_window import SubPlayWindow
from my_thumbnail_tool_bar import ThumbnailToolBar
from my_title_bar import TitleBar
from navigation import NavigationBar, NavigationMenu
from my_playing_interface import PlayingInterface, CreateSongCardsThread


class MainWindow(QWidget):
    """ 主窗口 """
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
        self.stackedWidget = QStackedWidget(self.subMainWindow)
        self.settingInterface = SettingInterface(self.subMainWindow)
        self.navigationBar = NavigationBar(self.subMainWindow)
        # 需要先实例化导航栏，再将导航栏和导航菜单关联
        self.navigationMenu = NavigationMenu(
            self.navigationBar, self.subMainWindow)
        # 关联两个导航部件
        self.navigationBar.setBoundNavigationMenu(self.navigationMenu)
        self.currentNavigation = self.navigationBar
        # 从配置文件中的选择文件夹读取音频文件
        self.myMusicInterface = MyMusicInterface(
            self.settingInterface.config['selected-folders'], self.subMainWindow)
        # 将最后一首歌作为playBar初始化时用的songInfo
        self.lastSongInfo = self.settingInterface.config.get('last-song', {})
        self.titleBar = TitleBar(self)
        self.playBar = PlayBar(self.lastSongInfo, self)
        # 实例化缩略图任务栏
        self.thumbnailToolBar = ThumbnailToolBar(self)
        self.thumbnailToolBar.setWindow(self.windowHandle())
        # 实例化左上角播放窗口
        self.subPlayWindow = SubPlayWindow(self, self.lastSongInfo)
        # 创建正在播放界面和创建歌曲卡线程
        self.playingInterface = PlayingInterface(self.playlist.playlist, self)
        #self.createSongCardThread = CreateSongCardsThread(self.playingInterface.songListWidget, self)
        # 创建快捷键
        self.playAct = QAction(
            parent=self, shortcut=Qt.Key_Space, triggered=self.switchPlayState)
        self.showNormalAct = QAction(
            parent=self, shortcut=Qt.Key_Escape, triggered=self.setFullScreen)
        self.addAction(self.playAct)
        self.addAction(self.showNormalAct)

    def __initWidget(self):
        """ 初始化小部件 """
        self.resize(1300, 970)
        self.setWindowTitle('Groove音乐')
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.setWindowIcon(QIcon('resource\\images\\透明icon.png'))
        self.setAttribute(Qt.WA_TranslucentBackground | Qt.WA_StyledBackground)
        # self.subMainWindow.setAttribute(Qt.WA_TranslucentBackground)
        # 居中显示
        desktop = QApplication.desktop()
        self.move(int(desktop.width() / 2 - self.width() / 2),
                  int((desktop.height()-120) / 2 - self.height() / 2))
        # 标题栏置顶
        self.titleBar.raise_()
        # self.titleBar.closeBt.setBlackCloseIcon(0)  # 更换图标
        # 隐藏导航菜单
        self.navigationMenu.hide()
        self.navigationBar.musicGroupButton.isSelected = True
        self.navigationMenu.musicGroupButton.isSelected = True
        # 设置窗口特效
        self.setWindowEffect()
        # 将窗口添加到stackedWidget中
        self.stackedWidget.addWidget(self.myMusicInterface)
        self.stackedWidget.addWidget(self.settingInterface)
        self.stackedWidget.setCurrentWidget(self.myMusicInterface)
        self.totalStackWidget.addWidget(self.subMainWindow)
        # 设置右边子窗口的位置
        self.setWidgetGeometry()
        # 引用小部件
        self.referenceWidgets()
        # 初始化播放列表
        self.initPlaylist()
        # 设置全局热键
        self.setHotKey()
        self.totalStackWidget.addWidget(self.playingInterface)
        # 设置层叠样式
        self.setObjectName('mainWindow')
        self.subMainWindow.setObjectName('subMainWindow')
        self.playingInterface.setObjectName('playingInterface')
        self.setQss()
        # 将按钮点击信号连接到槽函数
        self.connectSignalToSlot()
        # 初始化播放栏
        self.initPlayBar()
        # 显示主界面
        self.show()
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
        # 开启亚克力效果和阴影效果
        self.hWnd = HWND(int(self.winId()))
        self.windowEffect.setAcrylicEffect(self.hWnd, 'F2F2F250', True)

    def setWidgetGeometry(self):
        """ 调整小部件的geometry """
        self.subMainWindow.resize(self.size())
        self.totalStackWidget.resize(self.size())
        self.playingInterface.resize(self.size())
        self.titleBar.resize(self.width(), 40)
        self.navigationBar.resize(60, self.height())
        self.navigationMenu.resize(400, self.height())
        self.stackedWidget.move(self.currentNavigation.width(), 0)
        self.stackedWidget.resize(
            self.width() - self.currentNavigation.width(), self.height())
        self.playBar.resize(self.width(), self.playBar.height())

    def resizeEvent(self, e: QResizeEvent):
        """ 调整尺寸时同时调整子窗口的尺寸 """
        self.setWidgetGeometry()

    def showNavigationMenu(self):
        """ 显示导航菜单和抬头 """
        self.currentNavigation = self.navigationMenu
        self.navigationBar.hide()
        self.navigationMenu.show()
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
            if self.playBar.moveTime > 0:
                self.playBar.move(self.x() - 8, self.y() +
                                  self.height() - self.playBar.height())
            else:
                self.playBar.move(self.x() + 1, self.y() +
                                  self.height() - self.playBar.height() + 38)
            self.playBar.moveTime += 1

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
        self.settingInterface.writeConfig()
        self.playBar.close()
        self.subPlayWindow.close()
        self.playlist.save()
        e.accept()

    def GET_X_LPARAM(self, param):
        return param & 0xffff

    def GET_Y_LPARAM(self, param):
        return param >> 16

    def nativeEvent(self, eventType, message):
        result = 0
        msg = MSG.from_address(message.__int__())
        minV, maxV = 0, 4
        if msg.message == 0x0084:
            xPos = self.GET_X_LPARAM(msg.lParam) - self.frameGeometry().x()
            yPos = self.GET_Y_LPARAM(msg.lParam) - self.frameGeometry().y()
            if(xPos > minV and xPos < maxV):
                result = Flags.HTLEFT.value
            elif(xPos > (self.width() - maxV) and xPos < (self.width() - minV)):
                result = Flags.HTRIGHT.value
            elif (yPos > minV and yPos < maxV):
                result = Flags.HTTOP.value
            elif(yPos > (self.height() - maxV) and yPos < (self.height() - minV)):
                result = Flags.HTBOTTOM.value
            elif(xPos > minV and xPos < maxV and yPos > minV and yPos < maxV):
                result = Flags.HTTOPLEFT.value
            elif(xPos > (self.width() - maxV) and xPos < (self.width() - minV) and yPos > minV and yPos < maxV):
                result = Flags.HTTOPRIGHT.value
            elif(xPos > minV and xPos < maxV and yPos > (self.height() - maxV) and yPos < (self.height() - minV)):
                result = Flags.HTBOTTOMLEFT.value
            elif(xPos > (self.width() - maxV) and xPos < (self.width() - minV) and yPos > (self.height() - maxV) and yPos < (self.height() - minV)):
                result = Flags.HTBOTTOMRIGHT.value
            if result != 0:
                return (True, result)
        return QWidget.nativeEvent(self, eventType, message)

    def connectSignalToSlot(self):
        """ 将信号连接到槽 """
        # 爬虫完成工作时更新歌曲卡信息
        self.settingInterface.crawlComplete.connect(
            self.songCardListWidget.updateSongCardInfo)
        # todo: 标题栏返回按钮功能
        self.titleBar.returnBt.clicked.connect(
            self.hidePlayingInterface)
        # todo:导航栏按钮功能
        self.navigationBar.showMenuButton.clicked.connect(
            self.showNavigationMenu)
        self.navigationBar.searchButton.clicked.connect(
            self.showNavigationMenu)
        self.navigationBar.playingButton.clicked.connect(
            self.showPlayingInterface)
        self.navigationMenu.showBarButton.clicked.connect(
            self.showNavigationBar)
        self.navigationMenu.playingButton.clicked.connect(
            self.showPlayingInterface)
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
        self.playBar.songInfoCard.clicked.connect(self.showPlayingInterface)
        # todo:将播放器的信号连接到槽函数
        self.player.positionChanged.connect(self.playerPositionChangeSlot)
        self.player.durationChanged.connect(self.playerDurationChangeSlot)
        # todo:将播放列表的信号连接到槽函数
        self.playlist.switchSongSignal.connect(self.updateWindow)
        self.playlist.currentIndexChanged.connect(
            self.playingInterface.setCurrentIndex)
        self.playlist.currentIndexChanged.connect(
            self.songCardListWidget.setPlay)
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
        # todo:歌曲卡的信号连接到槽函数
        self.songCardListWidget.doubleClicked.connect(
            self.songCardDoubleClickedSlot)
        self.songCardListWidget.playSignal.connect(
            self.songCardPlayButtonSlot)
        self.songCardListWidget.nextPlaySignal.connect(
            self.songCardNextPlaySlot)
        # todo:将专辑卡的信号连接到槽函数
        self.albumCardViewer.playSignal.connect(self.playAlbum)
        self.albumCardViewer.nextPlaySignal.connect(self.albumCardNextPlaySlot)
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

    def referenceWidgets(self):
        """ 引用小部件 """
        self.songCardListWidget = self.myMusicInterface.myMusicTabWidget.songTab.songCardListWidget
        # self.songerCardViewer = self.myMusicInterface.myMusicTabWidget.songerTab.songerHeadPortraitViewer
        self.albumCardViewer = self.myMusicInterface.myMusicTabWidget.albumTab.albumCardViewer

    def initPlaylist(self):
        """ 初始化播放列表 """
        self.player.setPlaylist(self.playlist)
        # 如果没有上一次的播放列表数据，就设置默认的播放列表
        if not self.playlist.playlist:
            songInfo_list = self.songCardListWidget.songInfo_list.copy()
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

    def songCardDoubleClickedSlot(self):
        """ 播放选中的歌曲卡 """
        songInfo_dict = self.songCardListWidget.songCard_list[self.songCardListWidget.currentRow(
        )].songInfo
        # 更新歌曲信息卡
        self.switchCurrentSong(songInfo_dict)

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
        # 如果当前播放列表模式不是歌曲界面的歌曲卡模式，就刷新播放列表
        newPlaylist = None
        if self.playlist.playlistType != PlaylistType.SONG_CARD_PLAYLIST:
            index = self.songCardListWidget.songInfo_list.index(songInfo_dict)
            newPlaylist = self.songCardListWidget.songInfo_list[index:] + \
                self.songCardListWidget.songInfo_list[0:index]
            self.playingInterface.setPlaylist(newPlaylist)
        self.playlist.playThisSong(
            songInfo_dict, newPlaylist, PlaylistType.SONG_CARD_PLAYLIST.value)
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
        """ 切换歌曲时更新播放栏和子播放窗口 """
        self.playBar.updateSongInfoCard(songInfo)
        self.subPlayWindow.updateWindow(songInfo)

    def hotKeySlot(self, funcObj):
        """ 热键按下时显示子播放窗口并执行对应操作 """
        funcObj()
        self.showSubPlayWindowSig.emit()

    def playAlbum(self, playlist):
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
        newPlaylist = self.songCardListWidget.songInfo_list.copy()
        shuffle(newPlaylist)
        self.playingInterface.setPlaylist(newPlaylist)
        self.playlist.setMedias(newPlaylist)
        self.play()

    def play(self):
        """ 播放歌曲并改变按钮样式 """
        self.player.play()
        self.setPlayButtonState(True)
        if self.playlist.playlist:
            if not self.playBar.songInfoCard.isVisible():
                self.playBar.songInfoCard.show()
                self.playBar.songInfoCard.updateSongInfoCard(
                    self.playlist.playlist[0])

    def initPlayBar(self):
        """ 从配置文件中读取配置数据来初始化播放栏 """
        # 初始化音量
        volume = self.settingInterface.config.get('volume', 20)
        self.playBar.volumeSlider.setValue(volume)
        self.playingInterface.playBar.volumeSlider.setValue(volume)

    def showPlayingInterface(self):
        """ 显示正在播放界面 """
        self.playBar.hide()
        self.totalStackWidget.setCurrentIndex(1)
        self.titleBar.setWhiteIcon(True)

    def hidePlayingInterface(self):
        """ 隐藏正在播放界面 """
        self.playBar.show()
        self.totalStackWidget.setCurrentIndex(0)
        self.titleBar.setWhiteIcon(False)
        self.playingInterface.playBar.hide()

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
            self.showFullScreen()
            self.titleBar.hide()
            self.playingInterface.playBar.fillScreenButton.setFillScreen(True)
            if self.playingInterface.isPlaylistVisible:
                self.playingInterface.songInfoCardChute.move(
                    0, 258 - self.height())
        else:
            self.showNormal()
            self.titleBar.show()
            self.playingInterface.playBar.fillScreenButton.setFillScreen(False)
            if self.playingInterface.isPlaylistVisible:
                self.playingInterface.songInfoCardChute.move(
                    0, 258 - self.height())
