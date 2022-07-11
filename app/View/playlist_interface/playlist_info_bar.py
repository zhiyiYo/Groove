# coding:utf-8
from math import ceil

from common.database.entity import Playlist, SongInfo
from common.os_utils import getCoverPath
from components.app_bar import AppBarButtonFactory as BF
from components.app_bar import CollapsingAppBarBase
from PyQt5.QtCore import QObject, pyqtSignal
from PyQt5.QtGui import QColor, QPalette


class PlaylistInfoBar(CollapsingAppBarBase):
    """ Playlist information bar """

    def __init__(self, playlist: Playlist, parent=None):
        self.__getPlaylistInfo(playlist)
        content = str(len(self.songInfos)) + \
            QObject().tr(" songs")+f' • {self.duration}'
        super().__init__(self.playlistName, content,
                         self.playlistCoverPath, 'playlist', parent)

        self.setButtons([BF.PLAY, BF.ADD_TO, BF.RENAME,
                        BF.PIN_TO_START, BF.DELETE])

    def __getPlaylistInfo(self, playlist: Playlist):
        """ get playlist information """
        obj = QObject()
        self.playlist = playlist
        self.playlistName = playlist.name or ''

        self.songInfos = playlist.songInfos
        songInfo = self.songInfos[0] if self.songInfos else SongInfo()
        self.playlistCoverPath = getCoverPath(
            songInfo.singer, songInfo.album, "playlist_big")

        # calculate the total duration of playlist
        seconds = sum(i.duration for i in self.songInfos)
        self.hours = seconds//3600
        self.minutes = ceil((seconds % 3600)/60)
        h = obj.tr('hrs')
        m = obj.tr('mins')
        self.duration = f"{self.hours} {h} {self.minutes} {m}" if self.hours > 0 else f"{self.minutes} {m}"

    def updateWindow(self, playlist: Playlist):
        """ update playlist information bar """
        self.__getPlaylistInfo(playlist)
        content = str(len(self.songInfos)) + \
            self.tr(" songs")+f' • {self.duration}'
        super().updateWindow(self.playlistName, content, self.playlistCoverPath)

    def setBackgroundColor(self):
        """ set background color """
        path = ":/images/default_covers/playlist_113_113.png"
        if self.playlistCoverPath != path:
            super().setBackgroundColor()
        else:
            palette = QPalette()
            palette.setColor(self.backgroundRole(), QColor(24, 24, 24))
            self.setPalette(palette)
