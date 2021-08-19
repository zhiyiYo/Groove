# coding:utf-8
from copy import deepcopy

from app.components.dialog_box.message_dialog import MessageDialog
from app.components.buttons.three_state_button import ThreeStatePushButton
from app.components.dialog_box.rename_playlist_dialog import \
    RenamePlaylistDialog
from app.components.menu import AddToMenu
from app.components.scroll_area import ScrollArea
from PyQt5.QtCore import QPoint, Qt, pyqtSignal
from PyQt5.QtWidgets import QVBoxLayout, QWidget, QLabel

from .playlist_info_bar import PlaylistInfoBar
from .selection_mode_bar import SelectionModeBar
from .song_list_widget import SongListWidget


class PlaylistInterface(ScrollArea):
    """ 播放列表界面 """

    playAllSig = pyqtSignal(list)                           # 播放整张播放列表
    songCardPlaySig = pyqtSignal(int)                       # 在当前播放列表中播放这首歌
    deletePlaylistSig = pyqtSignal(str)                     # 删除整张播放列表
    removeSongSig = pyqtSignal(str, list)                   # 从播放列表中移除歌曲
    playOneSongCardSig = pyqtSignal(dict)                   # 将播放列表重置为一首歌
    playCheckedCardsSig = pyqtSignal(list)                  # 播放选中的歌曲卡
    nextToPlayOneSongSig = pyqtSignal(dict)                 # 下一首播放一首歌
    addOneSongToPlayingSig = pyqtSignal(dict)               # 添加一首歌到正在播放
    renamePlaylistSig = pyqtSignal(dict, dict)              # 重命名播放列表
    editSongInfoSignal = pyqtSignal(dict, dict)             # 编辑歌曲信息信号
    switchToAlbumCardInterfaceSig = pyqtSignal()            # 切换到专辑卡界面
    selectionModeStateChanged = pyqtSignal(bool)            # 进入/退出 选择模式
    nextToPlayCheckedCardsSig = pyqtSignal(list)            # 将选中的多首歌添加到下一首播放
    addSongsToPlayingPlaylistSig = pyqtSignal(list)         # 添加歌曲到正在播放
    addSongsToNewCustomPlaylistSig = pyqtSignal(list)       # 添加歌曲到新建播放列表
    addSongsToCustomPlaylistSig = pyqtSignal(str, list)     # 添加歌曲到自定义的播放列表中
    switchToAlbumInterfaceSig = pyqtSignal(str, str)        # 切换到专辑界面

    def __init__(self, playlist: dict, parent=None):
        """
        Parameters
        ----------
        playlist: dict
            播放列表

        parent:
            父级窗口
        """
        super().__init__(parent=parent)
        self.__getPlaylistInfo(playlist)
        # 创建小部件
        self.scrollWidget = QWidget(self)
        self.vBox = QVBoxLayout(self.scrollWidget)
        self.songListWidget = SongListWidget(self.songInfo_list, self)
        self.playlistInfoBar = PlaylistInfoBar(self.playlist, self)
        self.selectionModeBar = SelectionModeBar(self)
        self.noMusicLabel = QLabel("播放列表中没有音乐？", self)
        self.addMusicButton = ThreeStatePushButton(
            {
                "normal": "app/resource/images/playlist_interface/album_normal.png",
                "hover": "app/resource/images/playlist_interface/album_hover.png",
                "pressed": "app/resource/images/playlist_interface/album_pressed.png",
            },
            " 从我的集锦中添加歌曲",
            (29, 29),
            self
        )
        # 初始化
        self.__initWidget()

    def __initWidget(self):
        """ 初始化小部件 """
        self.resize(1230, 900)
        self.setWidget(self.scrollWidget)
        self.selectionModeBar.hide()
        self.songListWidget.setHorizontalScrollBarPolicy(Qt.ScrollBarAlwaysOff)
        # 设置布局
        self.vBox.setContentsMargins(0, 430, 0, 0)
        self.vBox.addWidget(self.songListWidget)
        self.noMusicLabel.move(42, 455)
        self.addMusicButton.move(42, 515)
        # 设置层叠样式
        self.__setQss()
        # 信号连接到槽
        self.__connectSignalToSlot()

    def updateWindow(self, playlist: dict):
        """ 更新窗口 """
        if playlist == self.playlist:
            return
        self.verticalScrollBar().setValue(0)
        self.__getPlaylistInfo(playlist)
        self.playlistInfoBar.updateWindow(self.playlist)
        self.songListWidget.updateAllSongCards(self.songInfo_list)
        self.scrollWidget.resize(
            self.width(), self.songListWidget.height()+430)

    def resizeEvent(self, e):
        """ 改变尺寸时改变小部件大小 """
        super().resizeEvent(e)
        self.playlistInfoBar.resize(
            self.width(), self.playlistInfoBar.height())
        self.songListWidget.resize(self.width(), self.songListWidget.height())
        self.scrollWidget.resize(
            self.width(), self.songListWidget.height() + 430)
        self.selectionModeBar.resize(
            self.width(), self.selectionModeBar.height())
        self.selectionModeBar.move(
            0, self.height() - self.selectionModeBar.height())

    def updateOneSongCard(self, oldSongInfo: dict, newSongInfo: dict):
        """ 更新一个歌曲卡

        Parameters
        ----------
        oldSongInfo: dict
            旧的歌曲信息

        newSongInfo: dict
            更新后的歌曲信息
        """
        if oldSongInfo not in self.songInfo_list:
            return
        self.songListWidget.updateOneSongCard(newSongInfo, False)
        self.playlist["songInfo_list"] = self.songListWidget.songInfo_list
        self.songInfo_list = self.playlist["songInfo_list"]

    def updateMultiSongCards(self, newSongInfo_list: list):
        """ 更新多个歌曲卡 """
        self.songListWidget.updateMultiSongCards(newSongInfo_list)
        self.playlist["songInfo_list"] = self.songListWidget.songInfo_list
        self.songInfo_list = self.playlist["songInfo_list"]
        self.playlistInfoBar.updateWindow(self.playlist)

    def __setQss(self):
        """ 设置层叠样式 """
        self.setObjectName("playlistInterface")
        self.scrollWidget.setObjectName("scrollWidget")
        with open('app/resource/css/playlist_interface.qss', encoding="utf-8") as f:
            self.setStyleSheet(f.read())

    def __getPlaylistInfo(self, playlist: dict):
        """ 获取播放列表信息 """
        self.playlist = deepcopy(playlist)
        self.songInfo_list = self.playlist.get("songInfo_list", [])
        self.playlistName = self.playlist.get("playlistName", "未知播放列表")

    def __onSelectionModeStateChanged(self, isOpenSelectionMode: bool):
        """ 选择状态改变对应的槽函数 """
        self.selectionModeBar.setHidden(not isOpenSelectionMode)
        self.selectionModeStateChanged.emit(isOpenSelectionMode)

    def __unCheckSongCards(self):
        """ 取消已选中歌曲卡的选中状态并更新按钮图标 """
        self.songListWidget.unCheckSongCards()
        # 更新按钮的图标为全选
        self.selectionModeBar.checkAllButton.setCheckedState(True)

    def __emitPlaylist(self):
        """ 发送歌曲界面选中的播放列表 """
        playlist = [
            songCard.songInfo for songCard in self.songListWidget.checkedSongCard_list]
        self.__unCheckSongCards()
        if self.sender() is self.selectionModeBar.playButton:
            self.playCheckedCardsSig.emit(playlist)
        elif self.sender() is self.selectionModeBar.nextToPlayButton:
            self.nextToPlayCheckedCardsSig.emit(playlist)

    def __onSelectAllButtonClicked(self):
        """ 歌曲卡全选/取消全选 """
        isChecked = not self.songListWidget.isAllSongCardsChecked
        self.songListWidget.setAllSongCardCheckedState(isChecked)
        self.selectionModeBar.checkAllButton.setCheckedState(isChecked)

    def __editSongCardInfo(self):
        """ 编辑歌曲卡信息 """
        songCard = self.songListWidget.checkedSongCard_list[0]
        self.__unCheckSongCards()
        self.songListWidget.showSongInfoEditDialog(songCard)

    def __showCheckedSongCardProperty(self):
        """ 显示选中的歌曲卡的属性 """
        songInfo = self.songListWidget.checkedSongCard_list[0].songInfo
        self.__unCheckSongCards()
        self.songListWidget.showSongPropertyDialog(songInfo)

    def __checkedCardNumChangedSlot(self, num):
        """ 选中的卡数量发生改变时刷新选择栏 """
        self.selectionModeBar.setPartButtonHidden(num > 1)

    def __onSelectionModeBarAlbumButtonClicked(self):
        """ 选择栏显示专辑按钮点击槽函数 """
        songCard = self.songListWidget.checkedSongCard_list[0]
        songCard.setChecked(False)
        self.switchToAlbumInterfaceSig.emit(songCard.album, songCard.singer)

    def __onSelectionModeBarDeleteButtonClicked(self):
        """ 选择模式栏删除按钮槽函数 """
        for songCard in self.songListWidget.checkedSongCard_list.copy():
            songCard.setChecked(False)
            self.songListWidget.removeSongCard(songCard.itemIndex)

        self.playlist["songInfo_list"] = self.songListWidget.songInfo_list
        self.playlistInfoBar.updateWindow(self.playlist)
        self.removeSongSig.emit(
            self.playlistName, self.playlist["songInfo_list"])

    def exitSelectionMode(self):
        """ 退出选择模式 """
        self.__unCheckSongCards()

    def __showAddToMenu(self):
        """ 显示添加到菜单 """
        menu = AddToMenu(parent=self)
        # 计算菜单弹出位置
        pos = self.selectionModeBar.mapToGlobal(
            QPoint(self.selectionModeBar.addToButton.x(), 0))
        x = pos.x() + self.selectionModeBar.addToButton.width() + 5
        y = pos.y() + self.selectionModeBar.addToButton.height() // 2 - \
            (13 + 38 * menu.actionCount()) // 2
        # 信号连接到槽
        for act in menu.action_list:
            act.triggered.connect(self.exitSelectionMode)
        songInfo_list = [
            i.songInfo for i in self.songListWidget.checkedSongCard_list]
        menu.playingAct.triggered.connect(
            lambda: self.addSongsToPlayingPlaylistSig.emit(songInfo_list))
        menu.addSongsToPlaylistSig.connect(
            lambda name: self.addSongsToCustomPlaylistSig.emit(name, songInfo_list))
        menu.newPlaylistAct.triggered.connect(
            lambda: self.addSongsToNewCustomPlaylistSig.emit(songInfo_list))
        menu.exec(QPoint(x, y))

    def __onScrollBarValueChanged(self, value):
        """ 滚动时改变专辑信息栏高度 """
        h = 385 - value
        if h > 155:
            self.playlistInfoBar.resize(self.playlistInfoBar.width(), h)

    def __showDeletePlaylistDialog(self):
        """ 显示删除播放列表对话框 """
        name = self.playlistName
        title = "是否确定要删除此项？"
        content = f"""如果删除"{name}"，它将不再位于此设备上。"""
        w = MessageDialog(title, content, self.window())
        w.yesSignal.connect(lambda: self.deletePlaylistSig.emit(name))
        w.exec()

    def __showRenamePlaylistDialog(self, oldPlaylist: dict):
        """ 显示重命名播放列表面板 """
        w = RenamePlaylistDialog(oldPlaylist, self.window())
        w.renamePlaylistSig.connect(self.__renamePlaylist)
        w.exec()

    def __renamePlaylist(self, oldPlaylist: dict, newPlaylist):
        """ 重命名播放列表 """
        self.__getPlaylistInfo(newPlaylist)
        self.playlistInfoBar.updateWindow(newPlaylist)
        self.renamePlaylistSig.emit(oldPlaylist, newPlaylist)

    def __onSongListWidgetRemoveSongs(self, songPath: str):
        """ 从播放列表中移除歌曲 """
        self.playlist["songInfo_list"] = self.songListWidget.songInfo_list
        self.playlistInfoBar.updateWindow(self.playlist)
        self.removeSongSig.emit(
            self.playlistName, self.playlist["songInfo_list"])

    def __onSongListWidgetEmptyChanged(self, isEmpty):
        """ 歌曲卡数量改变槽函数 """
        self.addMusicButton.setVisible(isEmpty)
        self.noMusicLabel.setVisible(isEmpty)

    def __connectSignalToSlot(self):
        """ 信号连接到槽 """
        self.addMusicButton.clicked.connect(self.switchToAlbumCardInterfaceSig)

        # 专辑信息栏信号
        self.playlistInfoBar.playAllButton.clicked.connect(
            lambda: self.playAllSig.emit(self.songInfo_list))
        self.playlistInfoBar
        self.playlistInfoBar.addToPlayingPlaylistSig.connect(
            lambda: self.addSongsToPlayingPlaylistSig.emit(self.songInfo_list))
        self.playlistInfoBar.addToNewCustomPlaylistSig.connect(
            lambda: self.addSongsToNewCustomPlaylistSig.emit(self.songInfo_list))
        self.playlistInfoBar.addToCustomPlaylistSig.connect(
            lambda name: self.addSongsToCustomPlaylistSig.emit(name, self.songInfo_list))
        self.playlistInfoBar.renameButton.clicked.connect(
            lambda: self.__showRenamePlaylistDialog(self.playlist))
        self.playlistInfoBar.deleteButton.clicked.connect(
            self.__showDeletePlaylistDialog)

        # 歌曲列表信号
        self.songListWidget.playSignal.connect(self.songCardPlaySig)
        self.songListWidget.playOneSongSig.connect(self.playOneSongCardSig)
        self.songListWidget.editSongInfoSignal.connect(self.editSongInfoSignal)
        self.songListWidget.nextToPlayOneSongSig.connect(
            self.nextToPlayOneSongSig)
        self.songListWidget.addSongToPlayingSignal.connect(
            self.addOneSongToPlayingSig)
        self.songListWidget.selectionModeStateChanged.connect(
            self.__onSelectionModeStateChanged)
        self.songListWidget.checkedSongCardNumChanged.connect(
            self.__checkedCardNumChangedSlot)
        self.songListWidget.addSongsToCustomPlaylistSig.connect(
            self.addSongsToCustomPlaylistSig)
        self.songListWidget.addSongsToNewCustomPlaylistSig.connect(
            self.addSongsToNewCustomPlaylistSig)
        self.songListWidget.switchToAlbumInterfaceSig.connect(
            self.switchToAlbumInterfaceSig)
        self.songListWidget.removeSongSignal.connect(
            self.__onSongListWidgetRemoveSongs)
        self.songListWidget.emptyChangedSig.connect(
            self.__onSongListWidgetEmptyChanged)
        self.songListWidget.isAllCheckedChanged.connect(
            lambda x: self.selectionModeBar.checkAllButton.setCheckedState(not x))

        # 选择栏信号连接到槽函数
        self.selectionModeBar.cancelButton.clicked.connect(
            self.__unCheckSongCards)
        self.selectionModeBar.playButton.clicked.connect(self.__emitPlaylist)
        self.selectionModeBar.nextToPlayButton.clicked.connect(
            self.__emitPlaylist)
        self.selectionModeBar.editInfoButton.clicked.connect(
            self.__editSongCardInfo)
        self.selectionModeBar.propertyButton.clicked.connect(
            self.__showCheckedSongCardProperty)
        self.selectionModeBar.checkAllButton.clicked.connect(
            self.__onSelectAllButtonClicked)
        self.selectionModeBar.addToButton.clicked.connect(self.__showAddToMenu)
        self.selectionModeBar.showAlbumButton.clicked.connect(
            self.__onSelectionModeBarAlbumButtonClicked)
        self.selectionModeBar.deleteButton.clicked.connect(
            self.__onSelectionModeBarDeleteButtonClicked)

        # 将滚动信号连接到槽函数
        self.verticalScrollBar().valueChanged.connect(self.__onScrollBarValueChanged)
