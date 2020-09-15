# coding:utf-8
from time import time

from PyQt5.QtCore import QPoint, QSize, Qt, pyqtSignal
from PyQt5.QtGui import (QColor, QContextMenuEvent, QFont, QIcon, QPainter,
                         QPen, QResizeEvent)
from PyQt5.QtWidgets import QAction, QLabel, QStackedWidget, QWidget

from get_info.get_song_info import GetSongInfo
from get_info.get_album_cover import GetAlbumCover
from get_info.get_album_info import GetAlbumInfo
from my_album_tab_interface import AlbumTabInterface
from my_album_tab_interface.album_blur_background import AlbumBlurBackground
from my_album_tab_interface.selection_mode_bar import \
    SelectionModeBar as AlbumTabSelectionBar
from my_song_tab_interface import SongTabInterface
from my_song_tab_interface.selection_mode_bar import \
    SelectionModeBar as SongTabSelectionModeBar

from .scroll_bar import ScrollBar
from .tab_button import TabButton


class MyMusicInterface(QWidget):
    """ 创建一个本地音乐分组界面 """
    randomPlayAllSig = pyqtSignal()
    currentIndexChanged = pyqtSignal(int)
    playCheckedCardsSig = pyqtSignal(list)
    selectionModeStateChanged = pyqtSignal(bool)
    nextToPlayCheckedCardsSig = pyqtSignal(list)

    def __init__(self, targetFolderPath_list: list, parent=None):
        super().__init__(parent)
        self.__targetFolderPath_list = targetFolderPath_list
        # 初始化标志位
        self.isInSelectionMode = False
        # 创建小部件
        self.__createWidgets()
        # 初始化
        self.__initWidget()

    def __createWidgets(self):
        """ 创建小部件 """
        # 实例化标签界面
        self.stackedWidget = QStackedWidget(self)
        # 扫描文件夹列表下的音频文件信息
        self.__songInfoGetter = GetSongInfo(self.__targetFolderPath_list)
        self.__albumCoverGetter = GetAlbumCover(self.__targetFolderPath_list)
        self.__albumInfoGetter = GetAlbumInfo(
            self.__songInfoGetter.songInfo_list)
        t1 = time()
        self.songTab = SongTabInterface(
            self.__songInfoGetter.songInfo_list, self)
        t2 = time()
        self.albumTab = AlbumTabInterface(
            self.__albumInfoGetter.albumInfo_list, self)
        t3 = time()
        print('创建歌曲标签界面耗时：'.ljust(17), t2 - t1)
        print('创建专辑标签界面耗时：'.ljust(17), t3 - t2)
        # 引用小部件
        self.__referenceWidgets()
        # 实例化标签页按钮
        self.songTabButton = TabButton('歌曲', self, 0)
        self.songerTabButton = TabButton('歌手', self, 1)
        self.albumTabButton = TabButton('专辑', self, 1)
        self.button_list = [self.songTabButton,
                            self.songerTabButton, self.albumTabButton]
        # 实例化一个标签和三个竖直滚动条
        self.myMusicLabel = QLabel(self)
        self.song_scrollBar = ScrollBar(self.songCardList_vScrollBar, self)
        self.album_scrollBar = ScrollBar(self.albumViewer_vScrollBar, self)
        self.scrollBar_list = [self.song_scrollBar, self.album_scrollBar]
        # 实例化底部选择栏
        self.songTabSelectionModeBar = SongTabSelectionModeBar(self)
        self.albumTabSelectionModeBar = AlbumTabSelectionBar(self)

    def __initLayout(self):
        """ 初始化布局 """
        self.myMusicLabel.move(30, 54)
        self.stackedWidget.move(0, 181)
        self.songTabButton.move(33, 136)
        self.albumTabButton.move(239, 136)
        self.songerTabButton.move(136, 136)
        for scrollBar in self.scrollBar_list:
            scrollBar.move(self.width() - scrollBar.width(), 40)

    def __initWidget(self):
        """ 初始化小部件的属性 """
        self.__initLayout()
        self.resize(1300, 970)
        self.setAttribute(Qt.WA_StyledBackground)
        # 将标签页面添加到stackedWidget中
        self.stackedWidget.addWidget(self.songTab)
        self.stackedWidget.addWidget(self.albumTab)
        self.songTabButton.setSelected(True)
        # 设置标签上
        self.myMusicLabel.setText('我的音乐')
        # 隐藏列表视图的滚动条
        self.songCardListWidget.setVerticalScrollBarPolicy(
            Qt.ScrollBarAlwaysOff)
        # 设置滚动条高度
        self.adjustScrollBarHeight()
        # 隐藏底部选择栏和磨砂背景
        self.songTabSelectionModeBar.hide()
        self.albumTabSelectionModeBar.hide()
        self.album_scrollBar.hide()
        # 分配ID并设置层叠样式
        self.setObjectName('musicGroupInterface')
        self.myMusicLabel.setObjectName('myMusicLabel')
        self.song_scrollBar.setObjectName('songScrollBar')
        self.album_scrollBar.setObjectName('albumScrollBar')
        self.__setQss()
        # 信号连接到槽
        self.__connectSignalToSlot()

    def adjustScrollBarHeight(self):
        """ 调整滚动条高度 """
        self.song_scrollBar.adjustSrollBarHeight()
        self.album_scrollBar.adjustSrollBarHeight()

    def __setQss(self):
        """ 设置层叠样式表 """
        with open('resource\\css\\myMusicInterface.qss', 'r',
                  encoding='utf-8') as f:
            self.setStyleSheet(f.read())

    def __changeTabSlot(self, index):
        """ 当前标签窗口改变时更改滚动条的绑定对象 """
        self.song_scrollBar.setVisible(index == 0)
        self.album_scrollBar.setVisible(index == 1)

    def __checkedCardNumChangedSlot(self, num):
        """ 选中的卡数量发生改变时刷新选择栏 """
        if self.sender() == self.songCardListWidget:
            self.songTabSelectionModeBar.setPartButtonHidden(num > 1)
        elif self.sender() == self.albumCardViewer:
            self.albumTabSelectionModeBar.setPartButtonHidden(num > 1)
            # 隐藏部分按钮时会发生高度的改变，需要调整位置
            self.albumTabSelectionModeBar.move(
                0, self.height() - self.albumTabSelectionModeBar.height())

    def __selectionModeStateChangedSlot(self, isOpenSelectionMode: bool):
        """ 选择模式状态变化槽函数 """
        self.isInSelectionMode = isOpenSelectionMode
        if self.sender() == self.songCardListWidget:
            self.songTabSelectionModeBar.setHidden(not isOpenSelectionMode)
        elif self.sender() == self.albumCardViewer:
            self.albumTabSelectionModeBar.setHidden(not isOpenSelectionMode)
        self.selectionModeStateChanged.emit(isOpenSelectionMode)

    def __referenceWidgets(self):
        """ 引用小部件 """
        # 引用视图
        self.songCardListWidget = self.songTab.songCardListWidget
        self.albumCardViewer = self.albumTab.albumCardViewer
        # 引用三个视图的滚动条
        self.songCardList_vScrollBar = self.songCardListWidget.verticalScrollBar(
        )
        self.albumViewer_vScrollBar = self.albumCardViewer.scrollArea.verticalScrollBar(
        )

    def __songTabSelectAllButtonSlot(self):
        """ 歌曲卡全选/取消全选 """
        isChecked = not self.songCardListWidget.isAllSongCardsChecked
        self.songCardListWidget.setAllSongCardCheckedState(isChecked)
        self.songTabSelectionModeBar.checkAllButton.setCheckedState(isChecked)

    def __albumTabSelectAllButtonSlot(self):
        """ 专辑卡全选/取消全选 """
        isChecked = not self.albumCardViewer.isAllAlbumCardsChecked
        self.albumCardViewer.setAllAlbumCardCheckedState(isChecked)
        self.albumTabSelectionModeBar.checkAllButton.setCheckedState(isChecked)

    def __unCheckSongCards(self):
        """ 取消已选中歌曲卡的选中状态并更新按钮图标 """
        self.songCardListWidget.unCheckSongCards()
        # 更新按钮的图标为全选
        self.songTabSelectionModeBar.checkAllButton.setCheckedState(True)

    def __unCheckAlbumCards(self):
        """ 取消已选中的专辑卡的选中状态并更新按钮图标 """
        self.albumCardViewer.unCheckAlbumCards()
        self.albumTabSelectionModeBar.checkAllButton.setChecked(True)

    def __emitSongTabPlaylist(self):
        """ 发送歌曲界面选中的播放列表 """
        playlist = [
            songCard.songInfo for songCard in self.songCardListWidget.checkedSongCard_list]
        self.__unCheckSongCards()
        if self.sender() == self.songTabSelectionModeBar.playButton:
            self.playCheckedCardsSig.emit(playlist)
        elif self.sender() == self.songTabSelectionModeBar.nextToPlayButton:
            self.nextToPlayCheckedCardsSig.emit(playlist)

    def __emitAlbumTabPlaylist(self):
        """ 发送专辑界面选中的播放列表 """
        # 将选中的所有专辑中的歌曲合成为一个列表
        playlist = []
        for albumCard in self.albumCardViewer.checkedAlbumCard_list:
            playlist.extend(albumCard.albumInfo['songInfo_list'])
        self.__unCheckAlbumCards()
        if self.sender() == self.albumTabSelectionModeBar.playButton:
            self.playCheckedCardsSig.emit(playlist)
        elif self.sender() == self.albumTabSelectionModeBar.nextToPlayButton:
            self.nextToPlayCheckedCardsSig.emit(playlist)

    def __switchToAlbumInterface(self):
        """ 切换到专辑界面 """
        if self.sender() == self.songTabSelectionModeBar.showAlbumButton:
            songCard = self.songCardListWidget.checkedSongCard_list[0]
            # 取消选中的歌曲卡的选中状态，隐藏选择栏并显示播放栏
            self.__unCheckSongCards()
            self.songCardListWidget.switchToAlbumInterfaceSig.emit(
                songCard.album, songCard.songer)

    def __editCardInfo(self):
        """ 编辑卡片信息 """
        if self.sender() == self.songTabSelectionModeBar.editInfoButton:
            songCard = self.songCardListWidget.checkedSongCard_list[0]
            self.__unCheckSongCards()
            self.songCardListWidget.showSongInfoEditPanel(songCard)
        elif self.sender() == self.albumTabSelectionModeBar.editInfoButton:
            albumCard = self.albumCardViewer.checkedAlbumCard_list[0]
            self.__unCheckAlbumCards()
            albumCard.showAlbumInfoEditPanel()

    def __showCheckedSongCardProperty(self):
        """ 显示选中的歌曲卡的属性 """
        songInfo = self.songCardListWidget.checkedSongCard_list[0].songInfo
        self.__unCheckSongCards()
        self.songCardListWidget.showPropertyPanel(songInfo)

    def exitSelectionMode(self):
        """ 退出选择模式 """
        self.__unCheckSongCards()
        self.__unCheckAlbumCards()

    def setSelectedButton(self, index):
        """ 设置选中的按钮 """
        for button in [self.songTabButton, self.albumTabButton]:
            button.setSelected(button.tabIndex == index)

    def __buttonSelectedSlot(self, tabIndex: int):
        """ 按钮点击时切换界面 """
        # 如果此时处于选择状态则不切换界面
        if self.isInSelectionMode:
            return
        self.setSelectedButton(tabIndex)
        self.stackedWidget.setCurrentIndex(tabIndex)
        self.currentIndexChanged.emit(tabIndex)

    def paintEvent(self, QPaintEvent):
        """ 绘制背景 """
        super().paintEvent(QPaintEvent)
        painter = QPainter(self)
        pen = QPen(QColor(229, 229, 229))
        painter.setPen(pen)
        painter.drawLine(30, 176, self.width() - 30, 176)

    def resizeEvent(self, e):
        """ 当窗口大小发生改变时隐藏小部件 """
        self.adjustScrollBarHeight()
        # 调整标签页面尺寸
        self.stackedWidget.resize(self.width(),self.height()-181)
        for scrollBar in self.scrollBar_list:
            scrollBar.move(self.width() - scrollBar.width(), 40)
        # 调整选中模式栏的位置和宽度
        self.songTabSelectionModeBar.resize(
            self.width(), self.songTabSelectionModeBar.height())
        self.songTabSelectionModeBar.move(
            0, self.height() - self.songTabSelectionModeBar.height())
        self.albumTabSelectionModeBar.resize(
            self.width(), self.albumTabSelectionModeBar.height())
        self.albumTabSelectionModeBar.move(
            0, self.height() - self.albumTabSelectionModeBar.height())

    def scanTargetPathSongInfo(self,targetFolderPath_list:list):
        """ 重新扫描指定的歌曲文件夹列表中的歌曲信息并更新标签界面 """
        self.__targetFolderPath_list = targetFolderPath_list
        # 重新扫描歌曲信息和专辑信息
        self.__songInfoGetter.scanTargetFolderSongInfo(targetFolderPath_list)
        self.__albumInfoGetter.updateAlbumInfo(self.__songInfoGetter.songInfo_list)
        # 更新界面
        self.songCardListWidget.updateAllSongCards(self.__songInfoGetter.songInfo_list)

    def __connectSignalToSlot(self):
        """ 信号连接到槽 """
        # 将按钮点击信号连接到槽
        self.songTabButton.buttonSelected.connect(self.__buttonSelectedSlot)
        self.albumTabButton.buttonSelected.connect(self.__buttonSelectedSlot)
        # 将标签页面信号连接到槽
        self.stackedWidget.currentChanged.connect(
            self.__changeTabSlot)
        self.albumTab.sortModeChanged.connect(
            self.album_scrollBar.associateScrollBar)
        self.albumTab.columnChanged.connect(
            self.album_scrollBar.associateScrollBar)
        # 无序播放所有信号连接到槽函数
        self.songTab.randomPlayAllSig.connect(
            self.randomPlayAllSig)
        self.albumTab.randomPlayAllSig.connect(
            self.randomPlayAllSig)
        # 歌曲界面信号连接到槽函数
        self.songCardListWidget.selectionModeStateChanged.connect(
            self.__selectionModeStateChangedSlot)
        self.songCardListWidget.checkedSongCardNumChanged.connect(
            self.__checkedCardNumChangedSlot)
        # 歌曲界面选择栏各按钮信号连接到槽函数
        self.songTabSelectionModeBar.cancelButton.clicked.connect(
            self.__unCheckSongCards)
        self.songTabSelectionModeBar.checkAllButton.clicked.connect(
            self.__songTabSelectAllButtonSlot)
        self.songTabSelectionModeBar.playButton.clicked.connect(
            self.__emitSongTabPlaylist)
        self.songTabSelectionModeBar.nextToPlayButton.clicked.connect(
            self.__emitSongTabPlaylist)
        self.songTabSelectionModeBar.showAlbumButton.clicked.connect(
            self.__switchToAlbumInterface)
        self.songTabSelectionModeBar.editInfoButton.clicked.connect(
            self.__editCardInfo)
        self.songTabSelectionModeBar.propertyButton.clicked.connect(
            self.__showCheckedSongCardProperty)
        # 专辑界面信号连接到槽函数
        self.albumCardViewer.selectionModeStateChanged.connect(
            self.__selectionModeStateChangedSlot)
        self.albumCardViewer.checkedAlbumCardNumChanged.connect(
            self.__checkedCardNumChangedSlot)
        # 专辑界面选择栏信号连接到槽函数
        self.albumTabSelectionModeBar.cancelButton.clicked.connect(
            self.__unCheckAlbumCards)
        self.albumTabSelectionModeBar.playButton.clicked.connect(
            self.__emitAlbumTabPlaylist)
        self.albumTabSelectionModeBar.nextToPlayButton.clicked.connect(
            self.__emitAlbumTabPlaylist)
        self.albumTabSelectionModeBar.editInfoButton.clicked.connect(
            self.__editCardInfo)
        self.albumTabSelectionModeBar.checkAllButton.clicked.connect(
            self.__albumTabSelectAllButtonSlot)
