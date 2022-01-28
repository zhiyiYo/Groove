# coding:utf-8
from typing import List

from common.library import Library
from common.database.entity import SongInfo
from components.dialog_box.message_dialog import MessageDialog
from components.widgets.menu import AddToMenu
from components.widgets.stacked_widget import PopUpAniStackedWidget
from PyQt5.QtCore import QPoint, Qt, pyqtSignal
from PyQt5.QtGui import QPalette
from PyQt5.QtWidgets import QWidget

from .album_tab_interface import AlbumCardInterface, AlbumSelectionModeBar
from .song_tab_interface import SongListWidget, SongSelectionModeBar
from .tool_bar import ToolBar


class MyMusicInterface(QWidget):
    """ 我的音乐界面 """

    randomPlayAllSig = pyqtSignal()                          # 无序播放所有
    nextToPlaySig = pyqtSignal(list)                         # 接下来播放选中的所有歌曲
    removeSongSig = pyqtSignal(list)                         # 删除部分歌曲 (移动到回收站)
    currentIndexChanged = pyqtSignal(int)                    # 当前播放的歌曲索引变化
    playCheckedCardsSig = pyqtSignal(list)                   # 播放所有选中的歌曲
    selectionModeStateChanged = pyqtSignal(bool)             # 进入/退出 选择模式
    addSongsToPlayingPlaylistSig = pyqtSignal(list)          # 将歌曲添加到正在播放列表
    addSongsToNewCustomPlaylistSig = pyqtSignal(list)        # 将歌曲添加到新建播放列表
    addSongsToCustomPlaylistSig = pyqtSignal(str, list)      # 将歌曲添加到自定义播放列表
    showLabelNavigationInterfaceSig = pyqtSignal(list, str)  # 显示标签导航界面
    switchToAlbumInterfaceSig = pyqtSignal(str, str)         # 切换到专辑界面

    def __init__(self, library: Library, parent=None):
        super().__init__(parent=parent)
        self.library = library
        self.isInSelectionMode = False
        self.stackedWidget = PopUpAniStackedWidget(self)
        self.songListWidget = SongListWidget(self.library.songInfos, self)
        self.albumCardInterface = AlbumCardInterface(self.library, self)
        self.toolBar = ToolBar(self)

        self.songTabButton = self.toolBar.songTabButton
        self.singerTabButton = self.toolBar.singerTabButton
        self.albumTabButton = self.toolBar.albumTabButton
        self.currentSongSortAct = self.toolBar.songSortByCratedTimeAct
        self.currentAlbumSortAct = self.toolBar.albumSortByCratedTimeAct

        self.songSelectionModeBar = SongSelectionModeBar(self)
        self.albumSelectionModeBar = AlbumSelectionModeBar(self)
        self.__initWidget()

    def __initWidget(self):
        """ 初始化小部件的属性 """
        self.resize(1300, 970)

        self.stackedWidget.addWidget(self.songListWidget, 0, 30)
        self.stackedWidget.addWidget(self.albumCardInterface, 0, 30)
        self.songTabButton.setSelected(True)

        # 初始化按钮
        text = self.tr(" Shuffle all")
        self.toolBar.randomPlayAllButton.setText(
            text+f" ({self.songListWidget.songCardNum()})")
        self.toolBar.randomPlayAllButton.adjustSize()

        # 隐藏底部选择栏和磨砂背景
        self.songSelectionModeBar.hide()
        self.albumSelectionModeBar.hide()

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
                text+f" ({len(self.albumCardInterface.albumCards)})")

        self.toolBar.randomPlayAllButton.adjustSize()

    def __onCheckedCardNumChanged(self, num):
        """ 选中的卡数量发生改变时刷新选择栏 """
        if self.sender() is self.songListWidget:
            self.songSelectionModeBar.setPartButtonHidden(num > 1)
        elif self.sender() is self.albumCardInterface:
            self.albumSelectionModeBar.setPartButtonHidden(num > 1)
            # 隐藏部分按钮时会发生高度的改变，需要调整位置
            self.albumSelectionModeBar.move(
                0, self.height() - self.albumSelectionModeBar.height())

    def __onSelectionModeStateChanged(self, isOpen: bool):
        """ 选择模式状态变化槽函数 """
        self.isInSelectionMode = isOpen
        if self.sender() is self.songListWidget:
            self.songSelectionModeBar.setVisible(isOpen)
        elif self.sender() is self.albumCardInterface:
            self.albumSelectionModeBar.setVisible(isOpen)

        self.selectionModeStateChanged.emit(isOpen)

    def __onSongTabSelectAllButtonClicked(self):
        """ 歌曲卡全选/取消全选 """
        isChecked = not self.songListWidget.isAllSongCardsChecked
        self.songListWidget.setAllSongCardCheckedState(isChecked)
        self.songSelectionModeBar.checkAllButton.setCheckedState(isChecked)

    def __onAlbumTabSelectAllButtonClicked(self):
        """ 专辑卡全选/取消全选 """
        isChecked = not self.albumCardInterface.isAllAlbumCardsChecked
        self.albumCardInterface.setAllAlbumCardCheckedState(isChecked)
        self.albumSelectionModeBar.checkAllButton.setCheckedState(isChecked)

    def __unCheckSongCards(self):
        """ 取消已选中歌曲卡的选中状态并更新按钮图标 """
        self.songListWidget.unCheckSongCards()
        self.songSelectionModeBar.checkAllButton.setCheckedState(True)

    def __unCheckAlbumCards(self):
        """ 取消已选中的专辑卡的选中状态并更新按钮图标 """
        self.albumCardInterface.unCheckAlbumCards()
        self.albumSelectionModeBar.checkAllButton.setChecked(True)

    def __emitSongTabPlaylist(self):
        """ 发送歌曲界面选中的播放列表 """
        playlist = [i.songInfo for i in self.songListWidget.checkedSongCards]
        self.__unCheckSongCards()

        if self.sender() is self.songSelectionModeBar.playButton:
            self.playCheckedCardsSig.emit(playlist)
        elif self.sender() is self.songSelectionModeBar.nextToPlayButton:
            self.nextToPlaySig.emit(playlist)

    def __emitAlbumTabPlaylist(self):
        """ 发送专辑界面选中的播放列表 """
        playlist = self.__getSelectedAlbumSongInfos()
        self.__unCheckAlbumCards()

        if self.sender() is self.albumSelectionModeBar.playButton:
            self.playCheckedCardsSig.emit(playlist)
        elif self.sender() is self.albumSelectionModeBar.nextToPlayButton:
            self.nextToPlaySig.emit(playlist)

    def __onSwitchToAlbumInterfaceButtonClicked(self):
        """ 切换到专辑界面按钮点击槽函数 """
        songCard = self.songListWidget.checkedSongCards[0]
        self.__unCheckSongCards()
        self.switchToAlbumInterfaceSig.emit(songCard.album, songCard.singer)

    def __editCardInfo(self):
        """ 编辑卡片信息 """
        if self.sender() is self.songSelectionModeBar.editInfoButton:
            songCard = self.songListWidget.checkedSongCards[0]
            self.__unCheckSongCards()
            self.songListWidget.showSongInfoEditDialog(songCard)
        elif self.sender() is self.albumSelectionModeBar.editInfoButton:
            albumCard = self.albumCardInterface.checkedAlbumCards[0]
            self.__unCheckAlbumCards()
            albumCard.showAlbumInfoEditDialog()

    def __onAlbumTabShowSingerButtonClicked(self):
        """ 专辑选择模式栏显示歌手点击信号槽函数 """
        albumCard = self.albumCardInterface.checkedAlbumCards[0]
        self.__unCheckAlbumCards()
        self.albumCardInterface.switchToSingerInterfaceSig.emit(
            albumCard.singer)

    def __showCheckedSongCardProperty(self):
        """ 显示选中的歌曲卡的属性 """
        songInfo = self.songListWidget.checkedSongCards[0].songInfo
        self.__unCheckSongCards()
        self.songListWidget.showSongPropertyDialog(songInfo)

    def __showDeleteSongsDialog(self):
        """ 显示删除歌曲对话框 """
        if len(self.songListWidget.checkedSongCards) > 1:
            title = self.tr("Are you sure you want to delete these?")
            content = self.tr(
                "If you delete these songs, they won't be on be this device anymore.")
        else:
            name = self.songListWidget.checkedSongCards[0].songName
            title = self.tr("Are you sure you want to delete this?")
            content = self.tr("If you delete") + f' "{name}" ' + \
                self.tr("it won't be on be this device anymore.")

        w = MessageDialog(title, content, self.window())
        w.yesSignal.connect(self.__onDeleteSongsYesButtonClicked)
        w.exec()

    def __onDeleteSongsYesButtonClicked(self):
        """ 歌曲界面选择模式栏删除按钮点击槽函数 """
        songPaths = [
            i.songPath for i in self.songListWidget.checkedSongCards]

        for songCard in self.songListWidget.checkedSongCards.copy():
            songCard.setChecked(False)
            self.songListWidget.removeSongCard(songCard.itemIndex)

        self.removeSongSig.emit(songPaths)

    def deleteSongs(self, songPaths: List[str]):
        """ 删除歌曲 """
        self.songListWidget.removeSongCards(songPaths)
        self.albumCardInterface.deleteSongs(songPaths)

    def __showDeleteAlbumsDialog(self):
        """ 显示删除专辑对话框 """
        if len(self.albumCardInterface.checkedAlbumCards) > 1:
            title = self.tr("Are you sure you want to delete these?")
            content = self.tr(
                "If you delete these albums, they won't be on be this device anymore.")
        else:
            name = self.albumCardInterface.checkedAlbumCards[0].album
            title = self.tr("Are you sure you want to delete this?")
            content = self.tr("If you delete") + f' "{name}" ' + \
                self.tr("it won't be on be this device anymore.")

        w = MessageDialog(title, content, self.window())
        w.yesSignal.connect(self.__onDeleteAlbumsYesButtonClicked)
        w.exec()

    def __onDeleteAlbumsYesButtonClicked(self):
        """ 专辑界面选择模式栏删除按钮点击槽函数 """
        songInfos = self.__getSelectedAlbumSongInfos()
        songPaths = [i.file for i in songInfos]
        self.__unCheckAlbumCards()

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
        self.stackedWidget.resize(self.size())
        self.toolBar.resize(self.width()-10, self.toolBar.height())
        self.songSelectionModeBar.resize(
            self.width(), self.songSelectionModeBar.height())
        self.songSelectionModeBar.move(
            0, self.height() - self.songSelectionModeBar.height())
        self.albumSelectionModeBar.resize(
            self.width(), self.albumSelectionModeBar.height())
        self.albumSelectionModeBar.move(
            0, self.height() - self.albumSelectionModeBar.height())

    def updateOneSongInfo(self, oldSongInfo: SongInfo, newSongInfo: SongInfo):
        """ 更新一首歌的信息 """
        self.songListWidget.updateOneSongCard(newSongInfo)
        self.albumCardInterface.updateOneSongInfo(oldSongInfo, newSongInfo)

    def __showSortModeMenu(self):
        """ 显示排序方式菜单 """
        pos = self.sender().pos()
        if self.sender() is self.toolBar.songSortModeButton:
            self.toolBar.songSortModeMenu.setDefaultAction(
                self.currentSongSortAct)
            actIndex = self.toolBar.songSortActions.index(
                self.currentSongSortAct)
            self.toolBar.songSortModeMenu.exec(
                self.mapToGlobal(QPoint(pos.x(), pos.y() - 37 * actIndex - 1)))

        elif self.sender() is self.toolBar.albumSortModeButton:
            self.toolBar.albumSortModeMenu.setDefaultAction(
                self.currentAlbumSortAct)
            actIndex = self.toolBar.albumSortActions.index(
                self.currentAlbumSortAct)
            self.toolBar.albumSortModeMenu.exec(
                self.mapToGlobal(QPoint(pos.x(), pos.y() - 37 * actIndex - 1)))

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
        self.toolBar.albumSortModeButton.setText(sender.text())
        self.albumCardInterface.setSortMode(sender.property('mode'))

    def __showAddToMenu(self):
        """ 显示添加到菜单 """
        menu = AddToMenu(parent=self)
        addToButton = self.sender()

        # 获取选中的播放列表
        if self.sender() is self.songSelectionModeBar.addToButton:
            selectionModeBar = self.songSelectionModeBar
            songInfos = [
                i.songInfo for i in self.songListWidget.checkedSongCards]
        else:
            selectionModeBar = self.albumSelectionModeBar
            songInfos = self.__getSelectedAlbumSongInfos()

        # 计算菜单弹出位置
        pos = selectionModeBar.mapToGlobal(addToButton.pos())
        x = pos.x() + addToButton.width() + 5
        y = pos.y() + int(
            addToButton.height() / 2 - (13 + 38 * menu.actionCount()) / 2)

        # 信号连接到槽
        for act in menu.action_list:
            act.triggered.connect(self.exitSelectionMode)

        menu.playingAct.triggered.connect(
            lambda: self.addSongsToPlayingPlaylistSig.emit(songInfos))
        menu.newPlaylistAct.triggered.connect(
            lambda: self.addSongsToNewCustomPlaylistSig.emit(songInfos))
        menu.addSongsToPlaylistSig.connect(
            lambda name: self.addSongsToCustomPlaylistSig.emit(name, songInfos))
        menu.exec(QPoint(x, y))

    def scrollToLabel(self, label: str):
        """ 滚动到label指定的位置 """
        self.stackedWidget.currentWidget().scrollToLabel(label)

    def __getSelectedAlbumSongInfos(self):
        """ 获取选中的所有专辑的歌曲信息 """
        singers = []
        albums = []
        for albumCard in self.albumCardInterface.checkedAlbumCards.copy():
            singers.append(albumCard.singer)
            albums.append(albumCard.album)

        songInfos = self.library.songInfoController.getSongInfosBySingerAlbum(
            singers, albums)

        return songInfos

    def __getAlbumSongInfos(self, singer: str, album: str):
        """ 获取专辑的歌曲信息 """
        albumInfo = self.library.albumInfoController.getAlbumInfo(
            singer, album)

        if not albumInfo:
            return []

        return albumInfo.songInfos

    def updateWindow(self):
        """ 更新界面 """
        self.songListWidget.updateAllSongCards(self.library.songInfos)
        self.albumCardInterface.updateAllAlbumCards(self.library.albumInfos)

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
        for act in self.toolBar.songSortActions:
            act.triggered.connect(self.__sortSongCard)
        for act in self.toolBar.albumSortActions:
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
        self.songListWidget.switchToAlbumInterfaceSig.connect(
            self.switchToAlbumInterfaceSig)
        self.songListWidget.songCardNumChanged.connect(
            lambda: self.__onCurrentTabChanged(self.stackedWidget.currentIndex()))
        self.songListWidget.isAllCheckedChanged.connect(
            lambda x: self.songSelectionModeBar.checkAllButton.setCheckedState(not x))
        self.songListWidget.removeSongSignal.connect(
            lambda songPath: self.removeSongSig.emit([songPath]))

        # 专辑卡界面信号连接到槽函数
        self.albumCardInterface.selectionModeStateChanged.connect(
            self.__onSelectionModeStateChanged)
        self.albumCardInterface.checkedAlbumCardNumChanged.connect(
            self.__onCheckedCardNumChanged)
        self.albumCardInterface.showLabelNavigationInterfaceSig.connect(
            self.showLabelNavigationInterfaceSig)
        self.albumCardInterface.nextPlaySignal.connect(self.nextToPlaySig)
        self.albumCardInterface.albumNumChanged.connect(
            lambda: self.__onCurrentTabChanged(self.stackedWidget.currentIndex()))
        self.albumCardInterface.isAllCheckedChanged.connect(
            lambda x: self.albumSelectionModeBar.checkAllButton.setCheckedState(not x))
        self.albumCardInterface.deleteAlbumSig.connect(lambda s, a: self.removeSongSig.emit(
            [i.file for i in self.__getAlbumSongInfos(s, a)]))
        self.albumCardInterface.addAlbumToPlayingSignal.connect(
            self.addSongsToPlayingPlaylistSig)
        self.albumCardInterface.addAlbumToCustomPlaylistSig.connect(
            self.addSongsToCustomPlaylistSig)
        self.albumCardInterface.addAlbumToNewCustomPlaylistSig.connect(
            self.addSongsToNewCustomPlaylistSig)

        # 歌曲界面选择栏各按钮信号连接到槽函数
        self.songSelectionModeBar.cancelButton.clicked.connect(
            self.__unCheckSongCards)
        self.songSelectionModeBar.checkAllButton.clicked.connect(
            self.__onSongTabSelectAllButtonClicked)
        self.songSelectionModeBar.playButton.clicked.connect(
            self.__emitSongTabPlaylist)
        self.songSelectionModeBar.nextToPlayButton.clicked.connect(
            self.__emitSongTabPlaylist)
        self.songSelectionModeBar.showAlbumButton.clicked.connect(
            self.__onSwitchToAlbumInterfaceButtonClicked)
        self.songSelectionModeBar.editInfoButton.clicked.connect(
            self.__editCardInfo)
        self.songSelectionModeBar.propertyButton.clicked.connect(
            self.__showCheckedSongCardProperty)
        self.songSelectionModeBar.addToButton.clicked.connect(
            self.__showAddToMenu)
        self.songSelectionModeBar.deleteButton.clicked.connect(
            self.__showDeleteSongsDialog)

        # 专辑界面选择栏信号连接到槽函数
        self.albumSelectionModeBar.cancelButton.clicked.connect(
            self.__unCheckAlbumCards)
        self.albumSelectionModeBar.playButton.clicked.connect(
            self.__emitAlbumTabPlaylist)
        self.albumSelectionModeBar.nextToPlayButton.clicked.connect(
            self.__emitAlbumTabPlaylist)
        self.albumSelectionModeBar.editInfoButton.clicked.connect(
            self.__editCardInfo)
        self.albumSelectionModeBar.checkAllButton.clicked.connect(
            self.__onAlbumTabSelectAllButtonClicked)
        self.albumSelectionModeBar.addToButton.clicked.connect(
            self.__showAddToMenu)
        self.albumSelectionModeBar.deleteButton.clicked.connect(
            self.__showDeleteAlbumsDialog)
        self.albumSelectionModeBar.showSingerButton.clicked.connect(
            self.__onAlbumTabShowSingerButtonClicked)
