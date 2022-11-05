# coding:utf-8
from math import ceil

from common.picture import Cover, CoverType
from common.translator import Translator
from common.database.entity import Playlist, SongInfo
from components.app_bar import AppBarButtonFactory as BF
from components.app_bar import CollapsingAppBarBase
from PyQt5.QtCore import QObject
from PyQt5.QtGui import QColor, QPalette


class PlaylistInfoBar(CollapsingAppBarBase):
    """ Playlist information bar """

    def __init__(self, playlist: Playlist, parent=None):
        self.__getPlaylistInfo(playlist)
        content = str(len(self.songInfos)) + \
            QObject().tr(" songs")+f' • {self.duration}'
        super().__init__(self.playlistName, content,
                         self.playlistCoverPath, 'playlist', parent)

        self.setButtons([
            BF.PLAY, BF.ADD_FAVORITE, BF.ADD_TO,
            BF.RENAME, BF.PIN_TO_START, BF.DELETE
        ])

    def __getPlaylistInfo(self, playlist: Playlist):
        """ get playlist information """
        self.playlist = playlist
        self.playlistName = playlist.name or ''

        self.songInfos = playlist.songInfos
        songInfo = self.songInfos[0] if self.songInfos else SongInfo()
        self.playlistCoverPath = Cover(
            songInfo.singer, songInfo.album).path(CoverType.PLAYLIST_BIG)

        # calculate the total duration of playlist
        seconds = sum(i.duration for i in self.songInfos)
        self.hours = seconds//3600
        self.minutes = ceil((seconds % 3600)/60)
        translator = Translator()
        h = translator.hrs
        m = translator.mins
        self.duration = f"{self.hours} {h} {self.minutes} {m}" if self.hours > 0 else f"{self.minutes} {m}"

    def updateWindow(self, playlist: Playlist):
        """ update playlist information bar """
        self.__getPlaylistInfo(playlist)
        content = str(len(self.songInfos)) + \
            self.tr(" songs")+f' • {self.duration}'
        super().updateWindow(self.playlistName, content, self.playlistCoverPath)

    def setBackgroundColor(self):
        """ set background color """
        if self.playlistCoverPath != CoverType.PLAYLIST_BIG.value:
            super().setBackgroundColor()
        else:
            palette = QPalette()
            palette.setColor(self.backgroundRole(), QColor(24, 24, 24))
            self.setPalette(palette)
