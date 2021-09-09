# coding:utf-8
from copy import deepcopy

from common.meta_data_getter import *
from common.thread.get_info_thread import GetInfoThread
from components.dialog_box.message_dialog import MessageDialog
from components.menu import AddToMenu
from components.pop_up_ani_stacked_widget import PopUpAniStackedWidget
from components.state_tooltip import StateTooltip
from View.my_music_interface.album_tab_interface import AlbumCardInterface
from View.my_music_interface.album_tab_interface.selection_mode_bar import \
    SelectionModeBar as AlbumTabSelectionBar
from View.my_music_interface.song_tab_interface import SongListWidget
from View.my_music_interface.song_tab_interface.selection_mode_bar import \
    SelectionModeBar as SongTabSelectionModeBar
from PyQt5.QtCore import QPoint, Qt, pyqtSignal
from PyQt5.QtGui import QPalette
from PyQt5.QtWidgets import QWidget

from .tool_bar import ToolBar


class MyMusicInterface(QWidget):
    """ 创建一个本地音乐分组界面 """

    randomPlayAllSig = pyqtSignal()                         # 无序播放所有
    removeSongSig = pyqtSignal(list)                        # 删除部分歌曲 (移动到回收站)
    currentIndexChanged = pyqtSignal(int)                   # 当前播放的歌曲索引变化
    playCheckedCardsSig = pyqtSignal(list)                  # 播放所有选中的歌曲
    selectionModeStateChanged = pyqtSignal(bool)            # 进入/退出 选择模式
    nextToPlayCheckedCardsSig = pyqtSignal(list)            # 接下来播放选中的所有歌曲
    addSongsToPlayingPlaylistSig = pyqtSignal(list)         # 将歌曲添加到正在播放列表
    addSongsToNewCustomPlaylistSig = pyqtSignal(list)       # 将歌曲添加到新建播放列表
    addSongsToCustomPlaylistSig = pyqtSignal(str, list)     # 将歌曲添加到自定义播放列表
    showLabelNavigationInterfaceSig = pyqtSignal(list, str)  # 显示标签导航界面

    def __init__(self, folderPaths: list, parent=None):
        """
        Parameters
        ----------
        folderPaths: list
            歌曲文件夹列表

        parent:
            父级窗口 """
        super().__init__(parent)
        self.folderPaths = folderPaths
        # 初始化标志位
        self.isInSelectionMode = False
        # 创建小部件
        self.__createWidgets()
        # 初始化
        self.__initWidget()

    def __createWidgets(self):
        """ 创建小部件 """
        self.stackedWidget = PopUpAniStackedWidget(self)

        # 扫描文件夹列表下的音频文件信息，顺序不能改动
        self.songInfoGetter = SongInfoGetter(self.folderPaths)
        self.albumCoverGetter = AlbumCoverGetter(
            self.songInfoGetter.songInfo_list)
        self.albumInfoGetter = AlbumInfoGetter(
            self.songInfoGetter.songInfo_list)
        self.singerInfoGetter = SingerInfoGetter(
            self.albumInfoGetter.albumInfo_list)

        self.songListWidget = SongListWidget(
            self.songInfoGetter.songInfo_list, self)
        self.albumCardInterface = AlbumCardInterface(
            self.albumInfoGetter.albumInfo_list, self)

        # 创建工具栏
        self.toolBar = ToolBar(self)

        # 引用小部件
        self.__referenceWidgets()

        # 创建底部选择栏
        self.songTabSelectionModeBar = SongTabSelectionModeBar(self)
        self.albumTabSelectionModeBar = AlbumTabSelectionBar(self)

    def __initWidget(self):
        """ 初始化小部件的属性 """
        self.resize(1300, 970)
        # 将标签页面添加到stackedWidget中
        self.stackedWidget.addWidget(self.songListWidget, 0, 30)
        self.stackedWidget.addWidget(self.albumCardInterface, 0, 30)
        self.songTabButton.setSelected(True)

        # 初始化按钮
        text = self.tr(" Shuffle all")
        self.toolBar.randomPlayAllButton.setText(
            text+f" ({self.songListWidget.songCardNum()})")
        self.toolBar.randomPlayAllButton.adjustSize()

        # 隐藏底部选择栏和磨砂背景
        self.songTabSelectionModeBar.hide()
        self.albumTabSelectionModeBar.hide()
        # 设置背景色
        palette = QPalette()
        palette.setColor(self.backgroundRole(), Qt.white)
        self.setPalette(palette)
        # 信号连接到槽
        self.__connectSignalToSlot()

    def __onCurrentTabChanged(self, index):
        """ 当前标签窗口改变时刷新工具栏 """
        self.toolBar.songSortModeButton.setVisible(index == 0)
        self.toolBar.albumSortModeButton.setVisible(index == 1)

        text = self.tr(" Shuffle all")
        if index == 0:
            self.toolBar.randomPlayAllButton.setText(
                text+f" ({self.songListWidget.songCardNum()})")
        elif index == 1:
            self.toolBar.randomPlayAllButton.setText(
                text+f" ({len(self.albumCardInterface.albumCard_list)})")

        self.toolBar.randomPlayAllButton.adjustSize()

    def __onCheckedCardNumChanged(self, num):
        """ 选中的卡数量发生改变时刷新选择栏 """
        if self.sender() is self.songListWidget:
            self.songTabSelectionModeBar.setPartButtonHidden(num > 1)
        elif self.sender() is self.albumCardInterface:
            self.albumTabSelectionModeBar.setPartButtonHidden(num > 1)
            # 隐藏部分按钮时会发生高度的改变，需要调整位置
            self.albumTabSelectionModeBar.move(
                0, self.height() - self.albumTabSelectionModeBar.height())

    def __onSelectionModeStateChanged(self, isOpenSelectionMode: bool):
        """ 选择模式状态变化槽函数 """
        self.isInSelectionMode = isOpenSelectionMode
        if self.sender() is self.songListWidget:
            self.songTabSelectionModeBar.setVisible(isOpenSelectionMode)
        elif self.sender() is self.albumCardInterface:
            self.albumTabSelectionModeBar.setVisible(isOpenSelectionMode)
        self.selectionModeStateChanged.emit(isOpenSelectionMode)

    def __referenceWidgets(self):
        """ 引用小部件 """
        # 引用按钮
        self.songTabButton = self.toolBar.songTabButton
        self.singerTabButton = self.toolBar.singerTabButton
        self.albumTabButton = self.toolBar.albumTabButton
        # 引用当前排序动作
        self.currentSongSortAct = self.toolBar.songSortByCratedTimeAct
        self.currentAlbumSortAct = self.toolBar.albumSortByCratedTimeAct

    def __onSongTabSelectAllButtonClicked(self):
        """ 歌曲卡全选/取消全选 """
        isChecked = not self.songListWidget.isAllSongCardsChecked
        self.songListWidget.setAllSongCardCheckedState(isChecked)
        self.songTabSelectionModeBar.checkAllButton.setCheckedState(isChecked)

    def __onAlbumTabSelectAllButtonClicked(self):
        """ 专辑卡全选/取消全选 """
        isChecked = not self.albumCardInterface.isAllAlbumCardsChecked
        self.albumCardInterface.setAllAlbumCardCheckedState(isChecked)
        self.albumTabSelectionModeBar.checkAllButton.setCheckedState(isChecked)

    def __unCheckSongCards(self):
        """ 取消已选中歌曲卡的选中状态并更新按钮图标 """
        self.songListWidget.unCheckSongCards()
        # 更新按钮的图标为全选
        self.songTabSelectionModeBar.checkAllButton.setCheckedState(True)

    def __unCheckAlbumCards(self):
        """ 取消已选中的专辑卡的选中状态并更新按钮图标 """
        self.albumCardInterface.unCheckAlbumCards()
        self.albumTabSelectionModeBar.checkAllButton.setChecked(True)

    def __emitSongTabPlaylist(self):
        """ 发送歌曲界面选中的播放列表 """
        playlist = [
            songCard.songInfo
            for songCard in self.songListWidget.checkedSongCard_list
        ]
        self.__unCheckSongCards()
        if self.sender() is self.songTabSelectionModeBar.playButton:
            self.playCheckedCardsSig.emit(playlist)
        elif self.sender() is self.songTabSelectionModeBar.nextToPlayButton:
            self.nextToPlayCheckedCardsSig.emit(playlist)

    def __emitAlbumTabPlaylist(self):
        """ 发送专辑界面选中的播放列表 """
        # 将选中的所有专辑中的歌曲合成为一个列表
        playlist = []
        for albumCard in self.albumCardInterface.checkedAlbumCard_list:
            playlist.extend(albumCard.albumInfo["songInfo_list"])
        self.__unCheckAlbumCards()
        if self.sender() is self.albumTabSelectionModeBar.playButton:
            self.playCheckedCardsSig.emit(playlist)
        elif self.sender() is self.albumTabSelectionModeBar.nextToPlayButton:
            self.nextToPlayCheckedCardsSig.emit(playlist)

    def __switchToAlbumInterface(self):
        """ 切换到专辑界面 """
        if self.sender() is self.songTabSelectionModeBar.showAlbumButton:
            songCard = self.songListWidget.checkedSongCard_list[0]
            # 取消选中的歌曲卡的选中状态，隐藏选择栏并显示播放栏
            self.__unCheckSongCards()
            self.songListWidget.switchToAlbumInterfaceSig.emit(
                songCard.album, songCard.singer)

    def __editCardInfo(self):
        """ 编辑卡片信息 """
        if self.sender() is self.songTabSelectionModeBar.editInfoButton:
            songCard = self.songListWidget.checkedSongCard_list[0]
            self.__unCheckSongCards()
            self.songListWidget.showSongInfoEditDialog(songCard)
        elif self.sender() is self.albumTabSelectionModeBar.editInfoButton:
            albumCard = self.albumCardInterface.checkedAlbumCard_list[0]
            self.__unCheckAlbumCards()
            albumCard.showAlbumInfoEditDialog()

    def __onAlbumTabShowSingerButtonClicked(self):
        """ 专辑选择模式栏显示歌手点击信号槽函数 """
        albumCard = self.albumCardInterface.checkedAlbumCard_list[0]
        self.__unCheckAlbumCards()
        self.albumCardInterface.switchToSingerInterfaceSig.emit(
            albumCard.singerName)

    def __showCheckedSongCardProperty(self):
        """ 显示选中的歌曲卡的属性 """
        songInfo = self.songListWidget.checkedSongCard_list[0].songInfo
        self.__unCheckSongCards()
        self.songListWidget.showSongPropertyDialog(songInfo)

    def __showDeleteSongsDialog(self):
        """ 显示删除歌曲对话框 """
        if len(self.songListWidget.checkedSongCard_list) > 1:
            title = self.tr("Are you sure you want to delete these?")
            content = self.tr(
                "If you delete these songs, they won't be on be this device anymore.")
        else:
            name = self.songListWidget.checkedSongCard_list[0].songName
            title = self.tr("Are you sure you want to delete this?")
            content = self.tr("If you delete") + f' "{name}" ' + \
                self.tr("it won't be on be this device anymore.")

        w = MessageDialog(title, content, self.window())
        w.yesSignal.connect(self.__onDeleteSongsYesButtonClicked)
        w.exec()

    def __onDeleteSongsYesButtonClicked(self):
        """ 歌曲界面选择模式栏删除按钮点击槽函数 """
        songPaths = [
            i.songPath for i in self.songListWidget.checkedSongCard_list]

        for songCard in self.songListWidget.checkedSongCard_list.copy():
            songCard.setChecked(False)
            self.songListWidget.removeSongCard(songCard.itemIndex)

        self.__deleteSongs(songPaths)

    def __deleteSongs(self, songPaths):
        """ 删除指定的歌曲并发送删除信号 """
        self.albumCardInterface.deleteSongs(songPaths)
        self.singerInfoGetter.updateSingerInfos(
            self.albumCardInterface.albumInfo_list)
        self.removeSongSig.emit(songPaths)

    def deleteSongs(self, songPaths: list):
        """ 删除歌曲 """
        self.songListWidget.removeSongCards(songPaths)
        self.albumCardInterface.deleteSongs(songPaths)
        self.singerInfoGetter.updateSingerInfos(
            self.albumCardInterface.albumInfo_list)

    def __showDeleteAlbumsDialog(self):
        """ 显示删除专辑对话框 """
        if len(self.albumCardInterface.checkedAlbumCard_list) > 1:
            title = self.tr("Are you sure you want to delete these?")
            content = self.tr(
                "If you delete these albums, they won't be on be this device anymore.")
        else:
            name = self.albumCardInterface.checkedAlbumCard_list[0].albumName
            title = self.tr("Are you sure you want to delete this?")
            content = self.tr("If you delete") + f' "{name}" ' + \
                self.tr("it won't be on be this device anymore.")

        w = MessageDialog(title, content, self.window())
        w.yesSignal.connect(self.__onDeleteAlbumsYesButtonClicked)
        w.exec()

    def __onDeleteAlbumsYesButtonClicked(self):
        """ 专辑界面选择模式栏删除按钮点击槽函数 """
        albumNames = []
        songPaths = []
        for albumCard in self.albumCardInterface.checkedAlbumCard_list.copy():
            albumNames.append(albumCard.albumName)
            songPaths.extend([i["songPath"] for i in albumCard.songInfo_list])
            albumCard.setChecked(False)

        self.albumCardInterface.deleteAlbums(albumNames)
        self.__deleteAlbums(songPaths)

    def __deleteAlbums(self, songPaths: list):
        """ 删除指定的专辑并发送删除信号 """
        self.songListWidget.removeSongCards(songPaths)
        self.singerInfoGetter.updateSingerInfos(
            self.albumCardInterface.albumInfo_list)
        self.removeSongSig.emit(songPaths)

    def exitSelectionMode(self):
        """ 退出选择模式 """
        self.__unCheckSongCards()
        self.__unCheckAlbumCards()

    def setCurrentTab(self, index: int):
        """ 设置当前的标签窗口 """
        self.setSelectedButton(index)
        self.stackedWidget.setCurrentIndex(index, duration=300)

    def setSelectedButton(self, index):
        """ 设置选中的按钮 """
        for button in [self.songTabButton, self.albumTabButton]:
            button.setSelected(button.tabIndex == index)

    def __onButtonSelected(self, tabIndex: int):
        """ 按钮点击时切换界面 """
        if self.isInSelectionMode:
            return
        self.setCurrentTab(tabIndex)
        self.currentIndexChanged.emit(tabIndex)

    def resizeEvent(self, e):
        """ 当窗口大小发生改变时隐藏小部件 """
        # 调整标签页面尺寸
        self.stackedWidget.resize(self.width(), self.height())
        self.toolBar.resize(self.width()-10, self.toolBar.height())
        # 调整选中模式栏的位置和宽度
        self.songTabSelectionModeBar.resize(
            self.width(), self.songTabSelectionModeBar.height())
        self.songTabSelectionModeBar.move(
            0, self.height() - self.songTabSelectionModeBar.height())
        self.albumTabSelectionModeBar.resize(
            self.width(), self.albumTabSelectionModeBar.height())
        self.albumTabSelectionModeBar.move(
            0, self.height() - self.albumTabSelectionModeBar.height())

    def scanTargetPathSongInfo(self, folderPaths: list):
        """ 重新扫描指定的歌曲文件夹列表中的歌曲信息并更新标签界面 """
        self.folderPaths = folderPaths

        # 创建线程来扫描信息
        thread = GetInfoThread(folderPaths, self)
        thread.scanFinished.connect(self.__onScanFinished)

        # 创建状态提示条
        if folderPaths:
            title = self.tr("Scanning song information")
            content = self.tr("Please wait patiently")
            w = StateTooltip(title, content, self.window())
            thread.scanFinished.connect(lambda: w.setState(True))
            thread.scanFinished.connect(self.__adjustWindowWidth)
            w.move(self.window().width() - w.width() - 30, 63)
            w.show()

        thread.start()

    def __onScanFinished(self, songInfo_list: list, albumInfo_list: list, singerInfos: dict):
        """ 扫描线程完成 """
        # 删除线程
        self.sender().quit()
        self.sender().wait()
        self.sender().deleteLater()

        # 更新界面
        self.songListWidget.updateAllSongCards(songInfo_list)
        self.albumCardInterface.updateAllAlbumCards(albumInfo_list)
        self.singerInfoGetter.singerInfos = singerInfos

    def rescanSongInfo(self):
        """ 重新当前的歌曲文件夹的歌曲信息 """
        if not self.songInfoGetter.rescanSongInfo():
            return

        self.albumCoverGetter.updateAlbumCover(
            self.songInfoGetter.songInfo_list)
        self.albumInfoGetter.updateAlbumInfo(
            self.songInfoGetter.songInfo_list)
        self.singerInfoGetter.updateSingerInfos(
            self.albumInfoGetter.albumInfo_list)

        # 更新界面
        self.songListWidget.updateAllSongCards(
            self.songInfoGetter.songInfo_list)
        self.albumCardInterface.updateAllAlbumCards(
            self.albumInfoGetter.albumInfo_list)

        # 强制调整窗口宽度，防止时长显示异常
        self.__adjustWindowWidth()

    def __adjustWindowWidth(self):
        """ 调整窗口宽度 """
        if not self.window().isMaximized():
            self.window().resize(self.window().width()+1, self.window().height())

    def hasSongModified(self):
        return self.songInfoGetter.hasSongModified()

    def updateOneSongInfo(self, oldSongInfo: dict, newSongInfo: dict):
        """ 更新一首歌的信息 """
        self.songListWidget.updateOneSongCard(newSongInfo)
        self.albumCardInterface.updateOneSongInfo(oldSongInfo, newSongInfo)
        self.singerInfoGetter.updateSingerInfos(
            self.albumCardInterface.albumInfo_list)
        self.songInfoGetter.songInfo_list = deepcopy(
            self.songListWidget.songInfo_list)
        self.albumInfoGetter.albumInfo_list = deepcopy(
            self.albumCardInterface.albumInfo_list)

    def __showSortModeMenu(self):
        """ 显示排序方式菜单 """
        if self.sender() is self.toolBar.songSortModeButton:
            self.toolBar.songSortModeMenu.setDefaultAction(
                self.currentSongSortAct)
            actIndex = self.toolBar.songSortAction_list.index(
                self.currentSongSortAct)
            self.toolBar.songSortModeMenu.exec(
                self.mapToGlobal(
                    QPoint(self.sender().x(),
                           self.sender().y() - 37 * actIndex - 1)
                )
            )
        elif self.sender() is self.toolBar.albumSortModeButton:
            self.toolBar.albumSortModeMenu.setDefaultAction(
                self.currentAlbumSortAct)
            actIndex = self.toolBar.albumSortAction_list.index(
                self.currentAlbumSortAct)
            self.toolBar.albumSortModeMenu.exec(
                self.mapToGlobal(
                    QPoint(self.sender().x(),
                           self.sender().y() - 37 * actIndex - 1)
                )
            )

    def __sortSongCard(self):
        """ 根据所选的排序方式对歌曲卡进行重新排序 """
        sender = self.sender()
        self.currentSongSortAct = sender
        self.toolBar.songSortModeButton.setText(sender.text())
        self.songListWidget.setSortMode(sender.property('mode'))

    def __sortAlbumCard(self):
        """ 根据所选的排序方式对歌曲卡进行重新排序 """
        sender = self.sender()
        self.currentAlbumSortAct = sender
        self.albumCardInterface.albumBlurBackground.hide()
        self.toolBar.albumSortModeButton.setText(sender.text())
        self.albumCardInterface.setSortMode(sender.property('mode'))

    def __showAddToMenu(self):
        """ 显示添加到菜单 """
        menu = AddToMenu(parent=self)
        addToButton = self.sender()

        # 获取选中的播放列表
        songInfo_list = []
        if self.sender() is self.songTabSelectionModeBar.addToButton:
            selectionModeBar = self.songTabSelectionModeBar
            songInfo_list = [
                i.songInfo for i in self.songListWidget.checkedSongCard_list]
        else:
            selectionModeBar = self.albumTabSelectionModeBar
            for albumCard in self.albumCardInterface.checkedAlbumCard_list:
                songInfo_list.extend(albumCard.songInfo_list)

        # 计算菜单弹出位置
        pos = selectionModeBar.mapToGlobal(addToButton.pos())
        x = pos.x() + addToButton.width() + 5
        y = pos.y() + int(
            addToButton.height() / 2 - (13 + 38 * menu.actionCount()) / 2)

        # 信号连接到槽
        for act in menu.action_list:
            act.triggered.connect(self.exitSelectionMode)
        menu.playingAct.triggered.connect(
            lambda: self.addSongsToPlayingPlaylistSig.emit(songInfo_list))
        menu.newPlaylistAct.triggered.connect(
            lambda: self.addSongsToNewCustomPlaylistSig.emit(songInfo_list))
        menu.addSongsToPlaylistSig.connect(
            lambda name: self.addSongsToCustomPlaylistSig.emit(name, songInfo_list))
        menu.exec(QPoint(x, y))

    def scrollToLabel(self, label: str):
        """ 滚动到label指定的位置 """
        self.stackedWidget.currentWidget().scrollToLabel(label)

    def findSingerInfo(self, singerName: str):
        """ 获取歌手信息 """
        return self.singerInfoGetter.singerInfos.get(singerName, {})

    def __connectSignalToSlot(self):
        """ 信号连接到槽 """
        # 将按钮点击信号连接到槽
        self.songTabButton.buttonSelected.connect(self.__onButtonSelected)
        self.albumTabButton.buttonSelected.connect(self.__onButtonSelected)

        # 将工具栏信号连接到槽函数
        self.toolBar.songSortModeButton.clicked.connect(
            self.__showSortModeMenu)
        self.toolBar.albumSortModeButton.clicked.connect(
            self.__showSortModeMenu)
        self.toolBar.randomPlayAllButton.clicked.connect(self.randomPlayAllSig)
        for act in self.toolBar.songSortAction_list:
            act.triggered.connect(self.__sortSongCard)
        for act in self.toolBar.albumSortAction_list:
            act.triggered.connect(self.__sortAlbumCard)

        # 将标签页面信号连接到槽
        self.stackedWidget.currentChanged.connect(self.__onCurrentTabChanged)

        # 歌曲界面信号连接到槽函数
        self.songListWidget.selectionModeStateChanged.connect(
            self.__onSelectionModeStateChanged)
        self.songListWidget.checkedSongCardNumChanged.connect(
            self.__onCheckedCardNumChanged)
        self.songListWidget.addSongsToCustomPlaylistSig.connect(
            self.addSongsToCustomPlaylistSig)
        self.songListWidget.addSongsToNewCustomPlaylistSig.connect(
            self.addSongsToNewCustomPlaylistSig)
        self.songListWidget.songCardNumChanged.connect(
            lambda: self.__onCurrentTabChanged(self.stackedWidget.currentIndex()))
        self.songListWidget.isAllCheckedChanged.connect(
            lambda x: self.songTabSelectionModeBar.checkAllButton.setCheckedState(not x))
        self.songListWidget.removeSongSignal.connect(
            lambda songPath: self.__deleteSongs([songPath]))

        # 专辑卡界面信号连接到槽函数
        self.albumCardInterface.addAlbumToCustomPlaylistSig.connect(
            self.addSongsToCustomPlaylistSig)
        self.albumCardInterface.addAlbumToNewCustomPlaylistSig.connect(
            self.addSongsToNewCustomPlaylistSig)
        self.albumCardInterface.addAlbumToPlayingSignal.connect(
            self.addSongsToPlayingPlaylistSig)
        self.albumCardInterface.selectionModeStateChanged.connect(
            self.__onSelectionModeStateChanged)
        self.albumCardInterface.checkedAlbumCardNumChanged.connect(
            self.__onCheckedCardNumChanged)
        self.albumCardInterface.showLabelNavigationInterfaceSig.connect(
            self.showLabelNavigationInterfaceSig)
        self.albumCardInterface.albumNumChanged.connect(
            lambda: self.__onCurrentTabChanged(self.stackedWidget.currentIndex()))
        self.albumCardInterface.isAllCheckedChanged.connect(
            lambda x: self.albumTabSelectionModeBar.checkAllButton.setCheckedState(not x))
        self.albumCardInterface.deleteAlbumSig.connect(self.__deleteAlbums)

        # 歌曲界面选择栏各按钮信号连接到槽函数
        self.songTabSelectionModeBar.cancelButton.clicked.connect(
            self.__unCheckSongCards)
        self.songTabSelectionModeBar.checkAllButton.clicked.connect(
            self.__onSongTabSelectAllButtonClicked)
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
        self.songTabSelectionModeBar.addToButton.clicked.connect(
            self.__showAddToMenu)
        self.songTabSelectionModeBar.deleteButton.clicked.connect(
            self.__showDeleteSongsDialog)

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
            self.__onAlbumTabSelectAllButtonClicked)
        self.albumTabSelectionModeBar.addToButton.clicked.connect(
            self.__showAddToMenu)
        self.albumTabSelectionModeBar.deleteButton.clicked.connect(
            self.__showDeleteAlbumsDialog)
        self.albumTabSelectionModeBar.showSingerButton.clicked.connect(
            self.__onAlbumTabShowSingerButtonClicked)
