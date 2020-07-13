# coding:utf-8

import sys
from ctypes.wintypes import HWND, MSG
from enum import Enum

from PyQt5.QtCore import QPoint, QRect, QSize, Qt, QUrl
from PyQt5.QtGui import QCloseEvent, QIcon, QPixmap, QResizeEvent, QFont
from PyQt5.QtMultimedia import QMediaPlayer
from PyQt5.QtWidgets import (QAction, QApplication, QGraphicsDropShadowEffect,
                             QStackedWidget, QWidget)

from effects import WindowEffect
from flags.wm_hittest import Flags
from my_music_interface import MyMusicInterface
from my_play_bar import PlayBar
from my_setting_interface import SettingInterface
from my_title_bar import TitleBar
from navigation import NavigationBar, NavigationMenu
from media_player import MediaPlaylist
from my_thumbnail_tool_bar import ThumbnailToolBar


class MainWindow(QWidget):
    """ 主窗口 """

    def __init__(self, parent=None):
        super().__init__(parent)
        # 实例化窗口特效
        self.windowEffect = WindowEffect()
        # 实例化小部件
        self.createWidgets()
        # 初始化界面
        self.initWidget()

    def createWidgets(self):
        """ 创建小部件 """
        # 实例化播放器和播放列表
        self.player = QMediaPlayer(self)
        self.playlist = MediaPlaylist(self)
        # 实例化小部件
        self.titleBar = TitleBar(self)
        self.stackedWidget = QStackedWidget(self)
        self.settingInterface = SettingInterface(self)
        self.navigationBar = NavigationBar(self)
        # 需要先实例化导航栏，再将导航栏和导航菜单关联
        self.navigationMenu = NavigationMenu(self.navigationBar, self)
        # 关联两个导航部件
        self.navigationBar.setBoundNavigationMenu(self.navigationMenu)
        self.currentNavigation = self.navigationBar
        # 从配置文件中的选择文件夹读取音频文件
        self.myMusicInterface = MyMusicInterface(
            self.settingInterface.config['selected-folders'], self)
        # 将最后一首歌作为playBar初始化时用的songInfo
        self.lastSongInfo = self.settingInterface.config.get('last-song', {})
        self.titleBar = TitleBar(self)
        self.playBar = PlayBar(self.lastSongInfo, self)
        # 实例化缩略图任务栏
        self.thumbnailToolBar = ThumbnailToolBar(self)
        self.thumbnailToolBar.setWindow(self.windowHandle())

    def initWidget(self):
        """ 初始化小部件 """
        self.resize(1300, 970)
        # 打开鼠标跟踪，用来检测鼠标是否位于边界处
        self.setObjectName('mainWindow')
        self.setWindowTitle('Groove音乐')
        self.setWindowFlags(Qt.FramelessWindowHint)
        self.setWindowIcon(QIcon('resource\\images\\透明icon.png'))
        self.setStyleSheet('QWidget#mainWindow{background:transparent}')
        self.setAttribute(Qt.WA_TranslucentBackground | Qt.WA_StyledBackground)
        # 居中显示
        desktop = QApplication.desktop()
        self.move(int(desktop.width() / 2 - self.width() / 2),
                  int((desktop.height()-120) / 2 - self.height() / 2))
        # 标题栏置顶
        self.titleBar.raise_()
        self.titleBar.closeBt.setBlackCloseIcon(0)  # 更换图标
        # 隐藏导航菜单
        self.navigationMenu.hide()
        # 设置窗口特效
        self.setWindowEffect()
        # 将窗口添加到stackedWidget中
        self.stackedWidget.addWidget(self.myMusicInterface)
        self.stackedWidget.addWidget(self.settingInterface)
        self.stackedWidget.setCurrentWidget(self.myMusicInterface)
        # 设置右边子窗口的位置
        self.setWidgetGeometry()
        # 引用小部件
        self.referenceWidgets()
        # 初始化播放列表
        self.initPlaylist()
        # 将按钮点击信号连接到槽函数
        self.connectSignalToSlot()
        # 初始化播放栏
        self.initPlayBar()

    def setWindowEffect(self):
        """ 设置窗口特效 """
        # 开启亚克力效果和阴影效果
        self.hWnd = HWND(int(self.winId()))
        self.windowEffect.setAcrylicEffect(self.hWnd, 'F2F2F250', True)

    def setWidgetGeometry(self):
        """ 调整小部件的geometry """
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
        self.settingInterface.config['last-song'] = self.playlist.currentPlaylist[
            self.playlist.currentIndex()]
        self.settingInterface.config['volume'] = self.playBar.volumeSlider.value(
        )
        self.settingInterface.config['position'] = self.playBar.progressSlider.value(
        )
        self.settingInterface.config['duration'] = self.playBar.progressSlider.maximum(
        )
        self.settingInterface.writeConfig()
        self.playBar.close()
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
        # 导航栏按钮功能
        self.navigationBar.showMenuButton.clicked.connect(
            self.showNavigationMenu)
        self.navigationBar.searchButton.clicked.connect(
            self.showNavigationMenu)
        self.navigationMenu.showBarButton.clicked.connect(
            self.showNavigationBar)
        # 播放栏各部件功能
        # self.playBar.randomPlayButton.clicked.connect(self.setRandomPlay)
        self.playBar.nextSongButton.clicked.connect(self.playlist.next)
        self.playBar.lastSongButton.clicked.connect(self.playlist.previous)
        self.playBar.playButton.clicked.connect(self.playButtonEvent)
        self.playBar.volumeButton.clicked.connect(self.volumeButtonEvent)
        self.playBar.loopModeButton.clicked.connect(
            lambda: self.playlist.setPlaybackMode(self.playBar.loopModeButton.loopMode))
        self.playBar.volumeSlider.valueChanged.connect(self.volumeChangedEvent)
        self.playBar.progressSlider.sliderMoved.connect(
            self.progressSliderMoveEvent)
        # 缩略图任务栏各按钮的功能
        self.thumbnailToolBar.playButton.clicked.connect(self.playButtonEvent)
        self.thumbnailToolBar.lastSongButton.clicked.connect(
            self.playlist.previous)
        self.thumbnailToolBar.nextSongButton.clicked.connect(
            self.playlist.next)
        # 将播放器的信号连接到槽函数
        self.player.positionChanged.connect(self.playerPositionChangeEvent)
        self.player.durationChanged.connect(self.playerDurationChangeEvent)
        # 将播放列表的信号连接到槽函数
        self.playlist.switchSongSignal.connect(
            lambda songInfo_dict: self.playBar.updateSongInfoCard(songInfo_dict))
        # 歌曲卡的信号连接到槽函数
        self.songCardListWidget.doubleClicked.connect(self.playSelectedSong)
        self.songCardListWidget.playSignal.connect(
            self.songCardPlayButtonEvent)

    def referenceWidgets(self):
        """ 引用小部件 """
        self.songCardListWidget = self.myMusicInterface.myMusicTabWidget.songTab.songCardListWidget
        self.songerCardViewer = self.myMusicInterface.myMusicTabWidget.songerTab.songerHeadPortraitViewer
        self.albumCardViewer = self.myMusicInterface.myMusicTabWidget.albumTab.albumCardViewer

    def initPlaylist(self):
        """ 初始化播放列表 """
        self.player.setPlaylist(self.playlist)
        # 添加播放列表
        songInfo_list = self.songCardListWidget.songInfo_list.copy()
        if self.lastSongInfo.keys() == songInfo_list[0].keys():
            songInfo_list = [self.lastSongInfo] + \
                self.songCardListWidget.songInfo_list
        self.playlist.addMedias(songInfo_list)

    def playButtonEvent(self):
        """ 播放栏或者缩略图任务栏的播放按钮按下时根据播放器的状态来决定是暂停还是播放 """
        if self.player.state() == QMediaPlayer.PlayingState:
            self.player.pause()
            self.playBar.playButton.setPlay(False)
            self.thumbnailToolBar.playButton.setPlay(False)
            self.thumbnailToolBar.setButtonsEnabled(True)
        else:
            self.player.play()
            self.playBar.playButton.setPlay(True)
            self.thumbnailToolBar.playButton.setPlay(True)

    def volumeButtonEvent(self):
        """ 静音按钮按下时决定是否静音 """
        if self.player.isMuted():
            self.player.setMuted(False)
        else:
            self.player.setMuted(True)

    def volumeChangedEvent(self):
        """ 音量滑动条数值改变时更换图标并设置音量 """
        self.player.setVolume(self.playBar.volumeSlider.value())
        if self.playBar.volumeSlider.value() == 0:
            self.playBar.volumeButton.setVolumeLevel(0)
        elif 0 < self.playBar.volumeSlider.value() <= 32:
            self.playBar.volumeButton.setVolumeLevel(1)
        elif 32 < self.playBar.volumeSlider.value() <= 65:
            self.playBar.volumeButton.setVolumeLevel(2)
        else:
            self.playBar.volumeButton.setVolumeLevel(3)

    def playerPositionChangeEvent(self):
        """ 播放器的播放进度改变时更新当前播放进度标签和进度条的值 """
        self.playBar.progressSlider.setValue(self.player.position())
        self.playBar.setCurrentTime(self.player.position())

    def playerDurationChangeEvent(self):
        """ 播放器当前播放的歌曲变化时更新进度条的范围和总时长标签 """
        if self.player.duration() >= 1:
            # 刚切换时得到的时长为0，所以需要先判断一下
            self.playBar.progressSlider.setRange(0, self.player.duration())
            self.playBar.setTotalTime(self.player.duration())

    def progressSliderMoveEvent(self):
        """ 手动拖动进度条时改变当前播放进度标签和播放器的值 """
        self.player.setPosition(self.playBar.progressSlider.value())
        self.playBar.setCurrentTime(self.player.position())

    def playSelectedSong(self):
        """ 播放选中的歌 """
        songInfo_dict = self.songCardListWidget.currentSongCard.songInfo_dict
        # 更新歌曲信息卡
        self.switchCurrentSong(songInfo_dict)
        self.thumbnailToolBar.setButtonsEnabled(True)

    def songCardPlayButtonEvent(self, songInfo_dict):
        """ 歌曲卡的播放按钮按下时播放这首歌 """
        self.switchCurrentSong(songInfo_dict)
        self.thumbnailToolBar.setButtonsEnabled(True)

    def switchCurrentSong(self, songInfo_dict: dict):
        """ 切换当前播放的歌曲 """
        # 更新歌曲信息卡
        self.playBar.updateSongInfoCard(songInfo_dict)
        # 播放歌曲
        self.playlist.playThisSong(songInfo_dict)
        self.playBar.playButton.setPlay(True)
        self.player.play()

    def setRandomPlay(self):
        """ 选择随机播放模式 """
        if self.playBar.randomPlayButton.isSelected:
            self.playlist.setRandomPlay(True)
        else:
            self.playlist.setRandomPlay(False)

    def initPlayBar(self):
        """ 从配置文件中读取配置数据来初始化播放栏 """
        # 初始化音量
        self.playBar.volumeSlider.setValue(
            self.settingInterface.config.get('volume', 20))

        # 根据配置文件初始化播放器
        """ if self.playlist.currentPlaylist:
            self.playlist.setCurrentIndex(0)
            self.player.pause()
            # 根据配置文件初始化进度条
            self.playBar.progressSlider.setValue(
                self.settingInterface.config.get('position', 0))
            self.playBar.progressSlider.setRange(
                0, self.settingInterface.config.get('duration', 0))
            self.player.setPosition(
                self.settingInterface.config.get('duration', 0)) """
