# coding:utf-8
from copy import deepcopy

from app.components.layout.v_box_layout import VBoxLayout
from app.components.scroll_area import ScrollArea
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QLabel, QWidget

from .album_group_box import AlbumGroupBox
from .playlist_group_box import PlaylistGroupBox
from .song_group_box import SongGroupBox


class SearchResultInterface(ScrollArea):

    playSongSig = pyqtSignal(int)                        # 播放歌曲
    playAlbumSig = pyqtSignal(list)                      # 播放专辑
    playPlaylistSig = pyqtSignal(list)                   # 播放自定义播放列表
    nextToPlaySig = pyqtSignal(list)                     # 下一首播放
    deleteSongSig = pyqtSignal(str)                      # 删除一首歌
    deleteAlbumSig = pyqtSignal(list)                    # 删除整张专辑
    deletePlaylistSig = pyqtSignal(str)                  # 删除整张播放列表
    playOneSongCardSig = pyqtSignal(dict)                # 将播放列表重置为一首歌
    renamePlaylistSig = pyqtSignal(dict, dict)           # 重命名播放列表
    switchToPlaylistInterfaceSig = pyqtSignal(str)       # 切换到播放列表界面
    switchToAlbumInterfaceSig = pyqtSignal(str, str)     # 切换到专辑界面
    addSongsToPlayingPlaylistSig = pyqtSignal(list)      # 添加歌曲到正在播放
    addSongsToNewCustomPlaylistSig = pyqtSignal(list)    # 添加歌曲到新的自定义的播放列表中
    addSongsToCustomPlaylistSig = pyqtSignal(str, list)  # 添加歌曲到自定义的播放列表中

    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.matchedPlaylists = {}
        self.matchedAlbumInfo_list = []
        self.matchedSongInfo_list = []
        self.titleLabel = QLabel(self)
        self.searchLabel = QLabel(self)
        self.scrollWidget = QWidget(self)
        self.vBox = VBoxLayout(self.scrollWidget)
        self.songGroupBox = SongGroupBox(self.scrollWidget)
        self.albumGroupBox = AlbumGroupBox(self.scrollWidget)
        self.playlistGroupBox = PlaylistGroupBox(self.scrollWidget)
        self.searchOthersLabel = QLabel("请尝试搜索其他内容。", self)
        self.checkSpellLabel = QLabel('请检查拼写情况，或搜索其他内容', self)
        self.songListWidget = self.songGroupBox.songListWidget
        self.__initWidget()

    def __initWidget(self):
        """ 初始化小部件 """
        self.vBox.setSpacing(20)
        self.vBox.setContentsMargins(0, 10, 0, 116)
        self.vBox.addWidget(self.albumGroupBox)
        self.vBox.addWidget(self.songGroupBox)
        self.vBox.addWidget(self.playlistGroupBox)
        self.songGroupBox.hide()
        self.setWidget(self.scrollWidget)
        self.setViewportMargins(0, 110, 0, 0)
        self.__setQss()
        self.searchLabel.setPixmap(
            QPixmap("app/resource/images/search_result_interface/Search.png"))
        self.__setHintsLabelVisible(False)
        self.titleLabel.move(30, 55)
        self.titleLabel.raise_()
        self.resize(1200, 500)
        self.__connectSignalToSlot()

    def resizeEvent(self, e):
        self.scrollWidget.resize(self.width(), self.scrollWidget.height())
        self.albumGroupBox.resize(self.width(), self.albumGroupBox.height())
        self.songGroupBox.resize(self.width(), self.songGroupBox.height())
        self.searchLabel.move(self.width()//2-self.searchLabel.width()//2, 138)
        self.checkSpellLabel.move(
            self.width()//2-self.checkSpellLabel.width()//2, 225)
        self.searchOthersLabel.move(
            self.width()//2-self.searchOthersLabel.width()//2, 300)
        self.playlistGroupBox.resize(
            self.width(), self.playlistGroupBox.height())

    def __setQss(self):
        """ 设置层叠样式 """
        self.titleLabel.setObjectName('titleLabel')
        self.checkSpellLabel.setObjectName('checkSpellLabel')
        self.searchOthersLabel.setObjectName('searchOthersLabel')
        with open('app/resource/css/search_result_interface.qss', encoding='utf-8') as f:
            self.setStyleSheet(f.read())
        self.checkSpellLabel.adjustSize()
        self.searchOthersLabel.adjustSize()

    def __setHintsLabelVisible(self, isVisible: bool):
        """ 设置提示标签的可见性 """
        self.searchLabel.setVisible(isVisible)
        self.checkSpellLabel.setVisible(isVisible)
        self.searchOthersLabel.setVisible(isVisible)

    def __onDeletePlaylist(self, playlistName: str):
        """ 删除一个播放列表槽函数 """
        self.matchedPlaylists.pop(playlistName)
        self.__updateWidgetsVisible()
        self.deletePlaylistSig.emit(playlistName)

    def __onDeleteAlbum(self, songPaths: list):
        """ 删除一张专辑槽函数 """
        self.songListWidget.removeSongCards(songPaths)
        self.playlistGroupBox.deleteSongs(songPaths)
        self.matchedSongInfo_list = deepcopy(self.songListWidget.songInfo_list)
        self.matchedAlbumInfo_list = deepcopy(
            self.albumGroupBox.albumInfo_list)
        self.matchedPlaylists = deepcopy(self.playlistGroupBox.playlists)
        self.__updateWidgetsVisible()
        self.deleteAlbumSig.emit(songPaths)

    def __onDeleteOneSong(self, songPath: str):
        """ 删除一首歌槽函数 """
        self.albumGroupBox.deleteSongs([songPath])
        self.matchedAlbumInfo_list=deepcopy(self.albumGroupBox.albumInfo_list)
        self.matchedSongInfo_list = deepcopy(self.songListWidget.songInfo_list)
        self.__updateWidgetsVisible()
        self.deleteSongSig.emit(songPath)

    def search(self, keyWord: str, songInfo_list: list, albumInfo_list: list, playlists: dict):
        """ 搜索与关键词相匹配的专辑、歌曲和播放列表 """
        keyWord_ = keyWord
        keyWord = keyWord.lower()

        # 对专辑进行匹配
        self.matchedAlbumInfo_list = []
        for albumInfo in albumInfo_list:
            album = albumInfo['album'].lower()
            songer = albumInfo["songer"].lower()
            if album.find(keyWord) >= 0 or songer.find(keyWord) >= 0:
                self.matchedAlbumInfo_list.append(albumInfo)

        # 对歌曲进行匹配
        self.matchedSongInfo_list = []
        for songInfo in songInfo_list:
            songName = songInfo["songName"].lower()
            songer = songInfo["songer"].lower()
            if songName.find(keyWord) >= 0 or songer.find(keyWord) >= 0:
                self.matchedSongInfo_list.append(songInfo)

        # 对播放列表进行匹配
        self.matchedPlaylists = {}
        for name, playlist in playlists.items():
            if name.lower().find(keyWord) >= 0:
                self.matchedPlaylists[name] = playlist

        # 更新界面
        self.titleLabel.setText(f'"{keyWord_}"的搜索结果')
        self.titleLabel.adjustSize()
        self.albumGroupBox.updateWindow(self.matchedAlbumInfo_list)
        self.songGroupBox.updateWindow(self.matchedSongInfo_list)
        self.playlistGroupBox.updateWindow(self.matchedPlaylists)

        # 调整窗口大小
        isAlbumVisible = len(self.matchedAlbumInfo_list) > 0
        isSongVisible = len(self.matchedSongInfo_list) > 0
        isPlaylistVisible = len(self.matchedPlaylists) > 0
        self.albumGroupBox.setVisible(isAlbumVisible)
        self.songGroupBox.setVisible(isSongVisible)
        self.playlistGroupBox.setVisible(isPlaylistVisible)

        visibleNum = isAlbumVisible+isSongVisible+isPlaylistVisible
        spacing = 0 if not visibleNum else (visibleNum-1)*20
        self.scrollWidget.resize(
            self.width(),
            236 + isAlbumVisible*self.albumGroupBox.height() +
            isSongVisible*self.songGroupBox.height() +
            isPlaylistVisible*self.playlistGroupBox.height() + spacing
        )

        # 显示/隐藏 提示标签
        self.__setHintsLabelVisible(visibleNum == 0)
        self.verticalScrollBar().setValue(0)

    def __updateWidgetsVisible(self):
        """ 更新小部件的可见性 """
        self.songGroupBox.setVisible(bool(self.matchedSongInfo_list))
        self.albumGroupBox.setVisible(bool(self.matchedAlbumInfo_list))
        self.playlistGroupBox.setVisible(bool(self.matchedPlaylists))
        if self.albumGroupBox.isHidden() and self.songGroupBox.isHidden() and self.playlistGroupBox.isHidden():
            self.__setHintsLabelVisible(True)

    def __connectSignalToSlot(self):
        """ 信号连接到槽 """
        # 专辑分组框信号连接到槽
        self.albumGroupBox.playSig.connect(self.playAlbumSig)
        self.albumGroupBox.nextToPlaySig.connect(self.nextToPlaySig)
        self.albumGroupBox.deleteAlbumSig.connect(self.__onDeleteAlbum)
        self.albumGroupBox.switchToAlbumInterfaceSig.connect(
            self.switchToAlbumInterfaceSig)
        self.albumGroupBox.addAlbumToPlayingSig.connect(
            self.addSongsToPlayingPlaylistSig)
        self.albumGroupBox.addAlbumToCustomPlaylistSig.connect(
            self.addSongsToCustomPlaylistSig)
        self.albumGroupBox.addAlbumToNewCustomPlaylistSig.connect(
            self.addSongsToNewCustomPlaylistSig)

        # 歌曲分组框信号连接到槽
        self.songListWidget.playSignal.connect(self.playSongSig)
        self.songListWidget.playOneSongSig.connect(self.playOneSongCardSig)
        self.songListWidget.nextToPlayOneSongSig.connect(
            lambda songInfo: self.nextToPlaySig.emit([songInfo]))
        self.songListWidget.addSongsToCustomPlaylistSig.connect(
            self.addSongsToCustomPlaylistSig)
        self.songListWidget.addSongsToNewCustomPlaylistSig.connect(
            self.addSongsToNewCustomPlaylistSig)
        self.songListWidget.addSongToPlayingSignal.connect(
            lambda songInfo: self.addSongsToPlayingPlaylistSig.emit([songInfo]))
        self.songListWidget.switchToAlbumInterfaceSig.connect(
            self.switchToAlbumInterfaceSig)
        self.songListWidget.removeSongSignal.connect(self.__onDeleteOneSong)

        # 播放列表分组框信号连接到槽函数
        self.playlistGroupBox.playSig.connect(self.playPlaylistSig)
        self.playlistGroupBox.nextToPlaySig.connect(self.nextToPlaySig)
        self.playlistGroupBox.deletePlaylistSig.connect(
            self.__onDeletePlaylist)
        self.playlistGroupBox.renamePlaylistSig.connect(self.renamePlaylistSig)
        self.playlistGroupBox.switchToPlaylistInterfaceSig.connect(
            self.switchToPlaylistInterfaceSig)
        self.playlistGroupBox.addSongsToPlayingPlaylistSig.connect(
            self.addSongsToPlayingPlaylistSig)
        self.playlistGroupBox.addSongsToCustomPlaylistSig.connect(
            self.addSongsToCustomPlaylistSig)
        self.playlistGroupBox.addSongsToNewCustomPlaylistSig.connect(
            self.addSongsToNewCustomPlaylistSig)
