# coding:utf-8
from pathlib import Path
from typing import List, Union

from PyQt5.QtSql import QSqlDatabase

from ..entity import SongInfo, Playlist
from ..service import SongInfoService, PlaylistService


class PlaylistController:
    """ Playlist controller """

    def __init__(self, db: QSqlDatabase = None):
        self.songInfoService = SongInfoService(db)
        self.playlistService = PlaylistService(db)

    def getAllPlaylists(self):
        """ get all playlists, not contain song information """
        playlists = self.playlistService.listAll()
        playlists.sort(key=lambda i: i.modifiedTime, reverse=True)
        return playlists

    def getPlaylist(self, name: str):
        """ get a playlist, contain song information """
        playlist = self.playlistService.findByName(name)
        if not playlist:
            return None

        files = [i.file for i in playlist.songInfos]
        songInfos = self.songInfoService.listByIds(files, True)
        for songInfo, songInfo_ in zip(songInfos, playlist.songInfos):
            songInfo['id'] = songInfo_['id']

        playlist.songInfos = songInfos
        return playlist

    def getPlaylists(self, names: List[str]):
        """ get multi playlists, contain song information """
        playlists = self.playlistService.listByNames(names)

        for playlist in playlists:
            files = [i.file for i in playlist.songInfos]
            songInfos = self.songInfoService.listByIds(files, True)

            for songInfo, songInfo_ in zip(songInfos, playlist.songInfos):
                songInfo['id'] = songInfo_['id']

            playlist.songInfos = songInfos

        return playlists

    def getPlaylistsLike(self, **condition):
        """ fuzzy search playlist """
        return self.playlistService.listLike(**condition)

    def create(self, playlist: Playlist):
        """ create a playlist """
        return self.playlistService.add(playlist)

    def addSongs(self, name: str, songInfos: List[SongInfo]):
        """ add songs to a playlist """
        return self.playlistService.addSongs(name, songInfos)

    def removeSongs(self, name: str, songInfos: List[SongInfo]):
        """ remove songs from a playlist """
        return self.playlistService.removeSongs(name, songInfos)

    def rename(self, old: str, new: str):
        """ rename a playlist """
        return self.playlistService.modifyName(old, new)

    def delete(self, name: str):
        """ delete a playlist """
        return self.playlistService.remove(name)

    def deleteBatch(self, names: List[str]):
        """ delete multi playlists """
        return self.playlistService.removeBatch(names)
