# coding:utf-8
from time import time

from app.View.my_music_interface.album_tab_interface import AlbumCardViewer
from app.View.my_music_interface.album_tab_interface.selection_mode_bar import (
    SelectionModeBar as AlbumTabSelectionBar,
)
from app.View.my_music_interface.song_tab_interface import SongCardListWidget
from app.View.my_music_interface.song_tab_interface.selection_mode_bar import (
    SelectionModeBar as SongTabSelectionModeBar,
)
from app.components.menu import AddToMenu
from app.components.pop_up_ani_stacked_widget import PopUpAniStackedWidget
from PyQt5.QtCore import QPoint, Qt, pyqtSignal
from PyQt5.QtGui import QPalette
from PyQt5.QtWidgets import QWidget

from .get_info.get_album_cover import GetAlbumCover
from .get_info.get_album_info import GetAlbumInfo
from .get_info.get_song_info import GetSongInfo
from .tool_bar import ToolBar


class MyMusicInterface(QWidget):
    """ 创建一个本地音乐分组界面 """

    randomPlayAllSig = pyqtSignal()
    currentIndexChanged = pyqtSignal(int)
    playCheckedCardsSig = pyqtSignal(list)
    selectionModeStateChanged = pyqtSignal(bool)
    nextToPlayCheckedCardsSig = pyqtSignal(list)
    addSongsToPlayingPlaylistSig = pyqtSignal(list)  # 将歌曲添加到正在播放列表
    addSongsToNewCustomPlaylistSig = pyqtSignal(list)  # 将歌曲添加到新建播放列表中
    addSongsToCustomPlaylistSig = pyqtSignal(str, list)  # 将歌曲添加到已存在的自定义播放列表中
    showLabelNavigationInterfaceSig = pyqtSignal(list, str)  # 显示标签导航界面

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
        self.stackedWidget = PopUpAniStackedWidget(self)
        # 扫描文件夹列表下的音频文件信息，顺序不能改动
        self.__songInfoGetter = GetSongInfo(self.__targetFolderPath_list)
        self.__albumCoverGetter = GetAlbumCover(self.__targetFolderPath_list)
        self.__albumInfoGetter = GetAlbumInfo(self.__songInfoGetter.songInfo_list)
        t1 = time()
        self.songCardListWidget = SongCardListWidget(
            self.__songInfoGetter.songInfo_list, self
        )
        t2 = time()
        self.albumCardViewer = AlbumCardViewer(
            self.__albumInfoGetter.albumInfo_list, self
        )
        t3 = time()
        print("创建歌曲标签界面耗时：".ljust(17), t2 - t1)
        print("创建专辑标签界面耗时：".ljust(17), t3 - t2)
        # 创建工具栏
        self.toolBar = ToolBar(self)
        # 引用小部件
        self.__referenceWidgets()
        # 实例化底部选择栏
        self.songTabSelectionModeBar = SongTabSelectionModeBar(self)
        self.albumTabSelectionModeBar = AlbumTabSelectionBar(self)

    def __initWidget(self):
        """ 初始化小部件的属性 """
        self.resize(1300, 970)
        # 将标签页面添加到stackedWidget中
        self.stackedWidget.addWidget(self.songCardListWidget, 0, 30)
        self.stackedWidget.addWidget(self.albumCardViewer, 0, 30)
        self.songTabButton.setSelected(True)
        # 初始化按钮
        self.toolBar.randomPlayAllButton.setText(
            f"({len(self.songCardListWidget.songCard_list)})"
        )
        # 隐藏底部选择栏和磨砂背景
        self.songTabSelectionModeBar.hide()
        self.albumTabSelectionModeBar.hide()
        # 设置背景色
        palette = QPalette()
        palette.setColor(self.backgroundRole(), Qt.white)
        self.setPalette(palette)
        # 信号连接到槽
        self.__connectSignalToSlot()

    def __changeTabSlot(self, index):
        """ 当前标签窗口改变时刷新工具栏 """
        self.toolBar.songSortModeButton.setVisible(index == 0)
        self.toolBar.albumSortModeButton.setVisible(index == 1)
        if index == 0:
            self.toolBar.randomPlayAllButton.setText(
                f"({len(self.songCardListWidget.songCard_list)})"
            )
        elif index == 1:
            self.toolBar.randomPlayAllButton.setText(
                f"({len(self.albumCardViewer.albumCard_list)})"
            )
        self.toolBar.randomPlayAllButton.adjustSize()

    def __checkedCardNumChangedSlot(self, num):
        """ 选中的卡数量发生改变时刷新选择栏 """
        if self.sender() == self.songCardListWidget:
            self.songTabSelectionModeBar.setPartButtonHidden(num > 1)
        elif self.sender() == self.albumCardViewer:
            self.albumTabSelectionModeBar.setPartButtonHidden(num > 1)
            # 隐藏部分按钮时会发生高度的改变，需要调整位置
            self.albumTabSelectionModeBar.move(
                0, self.height() - self.albumTabSelectionModeBar.height()
            )

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
        # 引用按钮
        self.songTabButton = self.toolBar.songTabButton
        self.songerTabButton = self.toolBar.songerTabButton
        self.albumTabButton = self.toolBar.albumTabButton
        # 引用当前排序动作
        self.currentSongSortAct = self.toolBar.songSortByCratedTimeAct
        self.currentAlbumSortAct = self.toolBar.albumSortByCratedTimeAct

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
            songCard.songInfo
            for songCard in self.songCardListWidget.checkedSongCard_list
        ]
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
            playlist.extend(albumCard.albumInfo["songInfo_list"])
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
                songCard.album, songCard.songer
            )

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
        self.stackedWidget.setCurrentIndex(tabIndex, duration=300)
        self.currentIndexChanged.emit(tabIndex)

    def resizeEvent(self, e):
        """ 当窗口大小发生改变时隐藏小部件 """
        # 调整标签页面尺寸
        self.stackedWidget.resize(self.width(), self.height())
        self.toolBar.resize(self.width() - 30, self.toolBar.height())
        # 调整选中模式栏的位置和宽度
        self.songTabSelectionModeBar.resize(
            self.width(), self.songTabSelectionModeBar.height()
        )
        self.songTabSelectionModeBar.move(
            0, self.height() - self.songTabSelectionModeBar.height()
        )
        self.albumTabSelectionModeBar.resize(
            self.width(), self.albumTabSelectionModeBar.height()
        )
        self.albumTabSelectionModeBar.move(
            0, self.height() - self.albumTabSelectionModeBar.height()
        )

    def scanTargetPathSongInfo(self, targetFolderPath_list: list):
        """ 重新扫描指定的歌曲文件夹列表中的歌曲信息并更新标签界面 """
        self.__targetFolderPath_list = targetFolderPath_list
        # 重新扫描歌曲信息和专辑信息
        self.__songInfoGetter.scanTargetFolderSongInfo(targetFolderPath_list)
        self.__albumCoverGetter.updateAlbumCover(self.__targetFolderPath_list)
        self.__albumInfoGetter.updateAlbumInfo(self.__songInfoGetter.songInfo_list)
        # 更新界面
        self.songCardListWidget.updateAllSongCards(self.__songInfoGetter.songInfo_list)
        self.albumCardViewer.updateAllAlbumCards(self.__albumInfoGetter.albumInfo_list)

    def rescanSongInfo(self):
        """ 重新当前的歌曲文件夹的歌曲信息 """
        if not self.__songInfoGetter.rescanSongInfo():
            return
        self.__albumCoverGetter.updateAlbumCover(self.__targetFolderPath_list)
        self.__albumInfoGetter.updateAlbumInfo(self.__songInfoGetter.songInfo_list)
        # 更新界面
        self.songCardListWidget.updateAllSongCards(self.__songInfoGetter.songInfo_list)
        self.albumCardViewer.updateAllAlbumCards(self.__albumInfoGetter.albumInfo_list)

    def hasSongModified(self):
        return self.__songInfoGetter.hasSongModified()

    def updateWindow(self, songInfo_list: list):
        """ 更新我的音乐界面 """
        self.__songInfoGetter.songInfo_list = songInfo_list
        self.songCardListWidget.updateAllSongCards(songInfo_list)
        self.updateAlbumCardViewer(songInfo_list)

    def updateAlbumCardViewer(self, songInfo_list: list):
        """ 更新专辑卡界面 """
        self.__albumCoverGetter.updateAlbumCover(self.__targetFolderPath_list)
        self.__albumInfoGetter.updateAlbumInfo(songInfo_list)
        self.albumCardViewer.updateAllAlbumCards(self.__albumInfoGetter.albumInfo_list)

    def __showSortModeMenu(self):
        """ 显示排序方式菜单 """
        if self.sender() is self.toolBar.songSortModeButton:
            self.toolBar.songSortModeMenu.setDefaultAction(self.currentSongSortAct)
            actIndex = self.toolBar.songSortAction_list.index(self.currentSongSortAct)
            self.toolBar.songSortModeMenu.exec(
                self.mapToGlobal(
                    QPoint(self.sender().x(), self.sender().y() - 37 * actIndex - 1)
                )
            )
        elif self.sender() is self.toolBar.albumSortModeButton:
            self.toolBar.albumSortModeMenu.setDefaultAction(self.currentAlbumSortAct)
            actIndex = self.toolBar.albumSortAction_list.index(self.currentAlbumSortAct)
            self.toolBar.albumSortModeMenu.exec(
                self.mapToGlobal(
                    QPoint(self.sender().x(), self.sender().y() - 37 * actIndex - 1)
                )
            )

    def __sortSongCard(self):
        """ 根据所选的排序方式对歌曲卡进行重新排序 """
        sender = self.sender()
        self.currentSongSortAct = sender
        # 更新列表
        if (
            sender is self.toolBar.songSortByCratedTimeAct
            and self.songCardListWidget.sortMode != "添加时间"
        ):
            self.toolBar.songSortModeButton.setText("添加时间")
            self.songCardListWidget.setSortMode("添加时间")
        elif (
            sender is self.toolBar.songSortByDictOrderAct
            and self.songCardListWidget.sortMode != "A到Z"
        ):
            self.toolBar.songSortModeButton.setText("A到Z")
            self.songCardListWidget.setSortMode("A到Z")
        elif (
            sender is self.toolBar.songSortBySongerAct
            and self.songCardListWidget.sortMode != "歌手"
        ):
            self.toolBar.songSortModeButton.setText("歌手")
            self.songCardListWidget.setSortMode("歌手")

    def __sortAlbumCard(self):
        """ 根据所选的排序方式对歌曲卡进行重新排序 """
        sender = self.sender()
        self.currentAlbumSortAct = sender
        self.albumCardViewer.albumBlurBackground.hide()
        # 更新分组
        if (
            sender is self.toolBar.albumSortByCratedTimeAct
            and self.albumCardViewer.sortMode != "添加时间"
        ):
            self.toolBar.albumSortModeButton.setText("添加时间")
            self.albumCardViewer.sortByAddTime()
        elif (
            sender is self.toolBar.albumSortByDictOrderAct
            and self.albumCardViewer.sortMode != "A到Z"
        ):
            self.toolBar.albumSortModeButton.setText("A到Z")
            self.albumCardViewer.sortByFirstLetter()
        elif (
            sender is self.toolBar.albumSortByYearAct
            and self.albumCardViewer.sortMode != "发行年份"
        ):
            self.toolBar.albumSortModeButton.setText("发行年份")
            self.albumCardViewer.sortByYear()
        elif (
            sender is self.toolBar.albumSortBySongerAct
            and self.albumCardViewer.sortMode != "歌手"
        ):
            self.toolBar.albumSortModeButton.setText("歌手")
            self.albumCardViewer.sortBySonger()

    def __showAddToMenu(self):
        """ 显示添加到菜单 """
        # 动作触发标志位
        self.__actionTriggeredFlag = False
        addToMenu = AddToMenu(parent=self)
        addToButton = self.sender()
        # 获取选中的播放列表
        songInfo_list = []
        if self.sender() is self.songTabSelectionModeBar.addToButton:
            selectionModeBar = self.songTabSelectionModeBar
            songInfo_list = [
                songCard.songInfo
                for songCard in self.songCardListWidget.checkedSongCard_list
            ]
        else:
            selectionModeBar = self.albumTabSelectionModeBar
            for albumCard in self.albumCardViewer.checkedAlbumCard_list:
                songInfo_list.extend(albumCard.songInfo_list)
        # 计算菜单弹出位置
        addToGlobalPos = selectionModeBar.mapToGlobal(QPoint(0, 0)) + QPoint(
            addToButton.x(), addToButton.y()
        )
        x = addToGlobalPos.x() + addToButton.width() + 5
        y = addToGlobalPos.y() + int(
            addToButton.height() / 2 - (13 + 38 * addToMenu.actionCount()) / 2
        )
        # 信号连接到槽
        addToMenu.playingAct.triggered.connect(
            lambda: self.addSongsToPlayingPlaylistSig.emit(songInfo_list)
        )
        addToMenu.newPlayList.triggered.connect(
            lambda: self.addSongsToNewCustomPlaylistSig.emit(songInfo_list)
        )
        addToMenu.addSongsToPlaylistSig.connect(
            lambda name: self.addSongsToCustomPlaylistSig.emit(name, songInfo_list)
        )
        for act in addToMenu.action_list:
            act.triggered.connect(self.__addToMenuTriggeredSlot)
        addToMenu.exec(QPoint(x, y))
        # 退出选择状态
        if self.__actionTriggeredFlag:
            self.exitSelectionMode()

    def __addToMenuTriggeredSlot(self):
        """ 添加到菜单上的动作被触发时标志位置位 """
        self.__actionTriggeredFlag = True

    def scrollToLabel(self, label: str):
        """ 滚动到label指定的位置 """
        self.stackedWidget.currentWidget().scrollToLabel(label)

    def __connectSignalToSlot(self):
        """ 信号连接到槽 """
        # 将按钮点击信号连接到槽
        self.songTabButton.buttonSelected.connect(self.__buttonSelectedSlot)
        self.albumTabButton.buttonSelected.connect(self.__buttonSelectedSlot)
        # 将工具栏信号连接到槽函数
        self.toolBar.songSortModeButton.clicked.connect(self.__showSortModeMenu)
        self.toolBar.albumSortModeButton.clicked.connect(self.__showSortModeMenu)
        self.toolBar.randomPlayAllButton.clicked.connect(self.randomPlayAllSig)
        for act in self.toolBar.songSortAction_list:
            act.triggered.connect(self.__sortSongCard)
        for act in self.toolBar.albumSortAction_list:
            act.triggered.connect(self.__sortAlbumCard)
        # 将标签页面信号连接到槽
        self.stackedWidget.currentChanged.connect(self.__changeTabSlot)
        # 歌曲界面信号连接到槽函数
        self.songCardListWidget.selectionModeStateChanged.connect(
            self.__selectionModeStateChangedSlot
        )
        self.songCardListWidget.checkedSongCardNumChanged.connect(
            self.__checkedCardNumChangedSlot
        )
        self.songCardListWidget.addSongsToCustomPlaylistSig.connect(
            self.addSongsToCustomPlaylistSig
        )
        self.songCardListWidget.addSongsToNewCustomPlaylistSig.connect(
            self.addSongsToNewCustomPlaylistSig
        )
        self.songCardListWidget.songCardNumChanged.connect(
            lambda: self.__changeTabSlot(self.stackedWidget.currentIndex())
        )
        # 专辑卡界面信号连接到槽函数
        self.albumCardViewer.addAlbumToCustomPlaylistSig.connect(
            self.addSongsToCustomPlaylistSig
        )
        self.albumCardViewer.addAlbumToNewCustomPlaylistSig.connect(
            self.addSongsToNewCustomPlaylistSig
        )
        self.albumCardViewer.addAlbumToPlayingSignal.connect(
            self.addSongsToPlayingPlaylistSig
        )
        self.albumCardViewer.selectionModeStateChanged.connect(
            self.__selectionModeStateChangedSlot
        )
        self.albumCardViewer.checkedAlbumCardNumChanged.connect(
            self.__checkedCardNumChangedSlot
        )
        self.albumCardViewer.showLabelNavigationInterfaceSig.connect(
            self.showLabelNavigationInterfaceSig
        )
        self.albumCardViewer.albumNumChanged.connect(
            lambda: self.__changeTabSlot(self.stackedWidget.currentIndex())
        )
        # 歌曲界面选择栏各按钮信号连接到槽函数
        self.songTabSelectionModeBar.cancelButton.clicked.connect(
            self.__unCheckSongCards
        )
        self.songTabSelectionModeBar.checkAllButton.clicked.connect(
            self.__songTabSelectAllButtonSlot
        )
        self.songTabSelectionModeBar.playButton.clicked.connect(
            self.__emitSongTabPlaylist
        )
        self.songTabSelectionModeBar.nextToPlayButton.clicked.connect(
            self.__emitSongTabPlaylist
        )
        self.songTabSelectionModeBar.showAlbumButton.clicked.connect(
            self.__switchToAlbumInterface
        )
        self.songTabSelectionModeBar.editInfoButton.clicked.connect(self.__editCardInfo)
        self.songTabSelectionModeBar.propertyButton.clicked.connect(
            self.__showCheckedSongCardProperty
        )
        self.songTabSelectionModeBar.addToButton.clicked.connect(self.__showAddToMenu)
        # 专辑界面选择栏信号连接到槽函数
        self.albumTabSelectionModeBar.cancelButton.clicked.connect(
            self.__unCheckAlbumCards
        )
        self.albumTabSelectionModeBar.playButton.clicked.connect(
            self.__emitAlbumTabPlaylist
        )
        self.albumTabSelectionModeBar.nextToPlayButton.clicked.connect(
            self.__emitAlbumTabPlaylist
        )
        self.albumTabSelectionModeBar.editInfoButton.clicked.connect(
            self.__editCardInfo
        )
        self.albumTabSelectionModeBar.checkAllButton.clicked.connect(
            self.__albumTabSelectAllButtonSlot
        )
        self.albumTabSelectionModeBar.addToButton.clicked.connect(self.__showAddToMenu)

