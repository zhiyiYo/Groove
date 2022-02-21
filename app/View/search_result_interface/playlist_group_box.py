# coding:utf-8
from typing import List

from common.database.entity import Playlist
from common.library import Library
from components.playlist_card import HorizonPlaylistCardView, PlaylistCardType
from PyQt5.QtCore import QMargins, pyqtSignal

from .group_box import GroupBox


class PlaylistGroupBox(GroupBox):
    """ Playlist card group  """

    qss = 'playlist_group_box.qss'

    def __init__(self, library: Library, parent=None):
        self.playlists = []
        self.playlistCardView = HorizonPlaylistCardView(
            library,
            self.playlists,
            PlaylistCardType.LOCAL_SEARCHED_PLAYLIST_CARD,
            margins=QMargins(35, 47, 65, 0),
        )
        super().__init__(library, self.playlistCardView, parent)
        self.titleButton.setText(self.tr('Playlists'))
        self.titleButton.adjustSize()

        self.playlistCards = self.playlistCardView.playlistCards

    def updateWindow(self, playlists: List[Playlist]):
        """ update playlist card group box """
        if playlists == self.playlists:
            return

        # 显示遮罩
        self.horizontalScrollBar().setValue(0)
        self.leftMask.hide()
        self.rightMask.show()

        # 更新播放列表卡
        self.playlists = playlists
        self.playlistCardView.updateAllCards(playlists)
