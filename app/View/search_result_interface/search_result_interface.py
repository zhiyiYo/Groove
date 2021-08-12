# coding:utf-8
from copy import deepcopy

from app.components.layout.v_box_layout import VBoxLayout
from app.components.scroll_area import ScrollArea
from PyQt5.QtCore import Qt, pyqtSignal
from PyQt5.QtGui import QPixmap
from PyQt5.QtWidgets import QLabel, QWidget, QVBoxLayout

from .album_group_box import AlbumGroupBox
from .playlist_group_box import PlaylistGroupBox
from .song_group_box import SongGroupBox


class SearchResultInterface(ScrollArea):

    def __init__(self, parent=None):
        super().__init__(parent=parent)
        self.playlists = {}
        self.songInfo_list = []
        self.albumInfo_list = []
        self.titleLabel = QLabel(self)
        self.searchLabel = QLabel(self)
        self.scrollWidget = QWidget(self)
        self.vBox = VBoxLayout(self.scrollWidget)
        self.songGroupBox = SongGroupBox(self.scrollWidget)
        self.albumGroupBox = AlbumGroupBox(self.scrollWidget)
        self.playlistGroupBox = PlaylistGroupBox(self.scrollWidget)
        self.searchOthersLabel = QLabel("请尝试搜索其他内容。", self)
        self.checkSpellLabel = QLabel('请检查拼写情况，或搜索其他内容', self)
        self.__initWidget()

    def __initWidget(self):
        """ 初始化小部件 """
        self.vBox.setSpacing(50)
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

    def search(self, keyWord: str, songInfo_list: list, albumInfo_list: list, playlists: dict):
        """ 搜索与关键词相匹配的专辑、歌曲和播放列表 """
        self.songInfo_list = deepcopy(songInfo_list)
        self.albumInfo_list = deepcopy(albumInfo_list)
        self.playlists = deepcopy(playlists)

        # 对专辑进行匹配
        matchedAlbumInfo_list = []
        for albumInfo in self.albumInfo_list:
            album = albumInfo['album']
            songer = albumInfo["songer"]
            if album.find(keyWord) >= 0 or songer.find(keyWord) >= 0:
                matchedAlbumInfo_list.append(albumInfo)

        # 对歌曲进行匹配
        matchedSongInfo_list = []
        for songInfo in self.songInfo_list:
            songName = songInfo["songName"]
            songer = songInfo["songer"]
            if songName.find(keyWord) >= 0 or songer.find(keyWord) >= 0:
                matchedSongInfo_list.append(songInfo)

        # 对播放列表进行匹配
        matchedPlaylists = {}
        for name, playlist in playlists.items():
            if name.find(keyWord) >= 0:
                matchedPlaylists[name] = playlist

        # 更新界面
        self.titleLabel.setText(f'"{keyWord}"的搜索结果')
        self.titleLabel.adjustSize()
        self.albumGroupBox.updateWindow(matchedAlbumInfo_list)
        self.songGroupBox.updateWindow(matchedSongInfo_list)
        self.playlistGroupBox.updateWindow(matchedPlaylists)
        self.albumGroupBox.setHidden(len(matchedAlbumInfo_list) == 0)
        self.songGroupBox.setHidden(len(matchedSongInfo_list) == 0)
        self.playlistGroupBox.setHidden(len(matchedPlaylists) == 0)
        self.scrollWidget.adjustSize()