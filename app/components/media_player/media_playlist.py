# coding:utf-8
import json
from enum import Enum
from pathlib import Path
from typing import List

from common.database.entity import SongInfo
from common.library import Library
from common.url import url
from PyQt5.QtMultimedia import QMediaContent, QMediaPlaylist


class PlaylistType(Enum):
    """ 播放列表种类枚举 """

    SONG_CARD_PLAYLIST = 0      # 播放列表为一首歌
    SONGER_CARD_PLAYLIST = 1    # 播放列表为选中歌手的歌
    ALBUM_CARD_PLAYLIST = 2     # 播放列表为选中专辑的歌
    LAST_PLAYLIST = 3           # 上一次的播放列表
    NO_PLAYLIST = 4             # 没有播放列表
    CUSTOM_PLAYLIST = 5         # 自定义播放列表
    ALL_SONG_PLAYLIST = 6       # 播放列表为歌曲文件夹中的所有歌曲


class MediaPlaylist(QMediaPlaylist):
    """ Media playlist class """

    folder = Path('cache/last_playlist')

    def __init__(self, library: Library, parent=None):
        super().__init__(parent=parent)
        self.library = library
        self.playlist = []  # type:List[SongInfo]
        self.lastSongInfo = SongInfo()
        self.playlistType = PlaylistType(PlaylistType.LAST_PLAYLIST)

        self.setPlaybackMode(QMediaPlaylist.Sequential)
        self.prePlayMode = self.playbackMode()
        self.randPlayBtnPressed = False
        self.__readLastPlaylist()

    def addSong(self, songInfo: SongInfo):
        """ append song to playlist """
        if not songInfo:
            return

        self.playlist.append(songInfo)
        super().addMedia(QMediaContent(url(songInfo.file)))

    def addSongs(self, songInfos: list):
        """ append multi songs to playlist """
        if not songInfos:
            return

        self.playlist.extend(songInfos)
        for songInfo in songInfos:
            super().addMedia(QMediaContent(url(songInfo.file)))

    def insertSong(self, index: int, songInfo: SongInfo):
        """ insert song to playlist  """
        super().insertMedia(index, QMediaContent(url(songInfo.file)))
        self.playlist.insert(index, songInfo)

    def insertSongs(self, index: int, songInfos: List[SongInfo]):
        """ insert multi songs to playlist """
        if not songInfos:
            return

        self.playlist = self.playlist[:index] + \
            songInfos + self.playlist[index:]

        medias = [QMediaContent(url(i.file)) for i in songInfos]
        super().insertMedia(index, medias)

    def clear(self):
        """ clear playlist """
        self.playlist.clear()
        super().clear()

    def next(self):
        """ play next song """
        if self.currentIndex() == self.mediaCount() - 1:
            if self.playbackMode() == QMediaPlaylist.Loop:
                self.setCurrentIndex(0)
            elif self.playbackMode() == QMediaPlaylist.Random:
                super().next()
        else:
            if self.playbackMode() == QMediaPlaylist.CurrentItemInLoop:
                self.setCurrentIndex(self.currentIndex()+1)
            else:
                super().next()

    def previous(self):
        """ play previous song """
        if self.currentIndex() == 0:
            if self.playbackMode() == QMediaPlaylist.Loop:
                self.setCurrentIndex(self.mediaCount() - 1)
        else:
            if self.playbackMode() == QMediaPlaylist.CurrentItemInLoop:
                self.setCurrentIndex(self.currentIndex()-1)
            else:
                super().previous()

    def getCurrentSong(self) -> SongInfo:
        """ get current song information """
        if self.currentIndex() >= 0:
            return self.playlist[self.currentIndex()]

        return SongInfo(file='__invalid__')

    def setCurrentSong(self, songInfo: SongInfo):
        """ set the song currently played """
        if not songInfo:
            return

        self.setCurrentIndex(self.playlist.index(songInfo))

    def playAlbum(self, songInfos: List[SongInfo], index=0):
        """ play songs in an alum """
        self.playlistType = PlaylistType.ALBUM_CARD_PLAYLIST
        self.setPlaylist(songInfos, index)

    def setRandomPlay(self, isRandomPlay=False):
        """ set whether to play randomly """
        if isRandomPlay:
            self.randPlayBtnPressed = True
            self.prePlayMode = self.playbackMode()
            if self.playbackMode() != QMediaPlaylist.CurrentItemInLoop:
                self.setPlaybackMode(QMediaPlaylist.Random)
        else:
            self.randPlayBtnPressed = False
            self.setPlaybackMode(self.prePlayMode)

    def setLoopMode(self, loopMode: QMediaPlaylist.PlaybackMode):
        self.prePlayMode = loopMode
        if not self.randPlayBtnPressed:
            self.setPlaybackMode(loopMode)
        elif loopMode == QMediaPlaylist.CurrentItemInLoop:
            self.setPlaybackMode(QMediaPlaylist.CurrentItemInLoop)
        else:
            self.setPlaybackMode(QMediaPlaylist.Random)

    def setPlaylist(self, songInfos: List[SongInfo], index=0):
        """ set songs in playlist """
        if songInfos == self.playlist:
            return

        self.clear()
        self.addSongs(songInfos)
        self.setCurrentIndex(index)

    def save(self):
        """ save playlist to json file """
        self.folder.mkdir(exist_ok=True, parents=True)
        files = [i.file for i in self.playlist]
        playlist = {
            "files": files,
            "last": files[self.currentIndex()] if files else ''
        }
        with open(self.folder/'last_playlist.json', 'w', encoding='utf-8') as f:
            json.dump(playlist, f)

    def __readLastPlaylist(self):
        """ read last playlist from json file """
        file = self.folder/"last_playlist.json"
        try:
            with open(file, encoding='utf-8') as f:
                playlist = json.load(f)
                files = playlist['files']
                last = playlist["last"]
        except:
            return

        self.playlist = self.library.songInfoController.getSongInfosByFile(
            files)
        self.lastSongInfo = self.library.songInfoController.getSongInfoByFile(
            last) or SongInfo()

        for songInfo in self.playlist:
            super().addMedia(QMediaContent(url(songInfo.file)))

    def removeSong(self, index):
        """ remove song from playlist """
        currentIndex = self.currentIndex()
        if currentIndex >= index:
            currentIndex -= 1

        self.playlist.pop(index)
        super().removeMedia(index)
        self.setCurrentIndex(currentIndex)

    def removeOnlineSong(self, index: int):
        """ remove online song from playlist """
        self.playlist.pop(index)
        super().removeMedia(index)

    def updateSongInfo(self, newSongInfo: SongInfo):
        """ update song information """
        for i, songInfo in enumerate(self.playlist):
            if songInfo.file == newSongInfo.file:
                self.playlist[i] = newSongInfo

    def updateMultiSongInfos(self, songInfos: SongInfo):
        """ update multi song information """
        for songInfo in songInfos:
            self.updateSongInfo(songInfo)
