# coding:utf-8
from typing import List

from PyQt5.QtCore import QDateTime
from PyQt5.QtSql import QSqlDatabase

from ..dao import PlaylistDao, SongPlaylistDao, PlaylistSongInfoDao
from ..entity import Playlist, SongPlaylist, SongInfo
from ..utils import UUIDUtils

from.service_base import ServiceBase


class PlaylistService(ServiceBase):
    """ Playlist service """

    def __init__(self, db: QSqlDatabase = None):
        super().__init__()
        self.playlistDao = PlaylistDao(db)
        self.songPlaylistDao = SongPlaylistDao(db)
        self.songInfoDao = PlaylistSongInfoDao(db)

    def createTable(self) -> bool:
        s1 = self.playlistDao.createTable()
        s2 = self.songPlaylistDao.createTable()
        s3 = self.songInfoDao.createTable()
        return s1 and s2 and s3

    def findByName(self, name: str) -> Playlist:
        """ list a playlists by name, return `None` if no one match """
        playlist = self.playlistDao.selectBy(name=name)  # type:Playlist
        if not playlist:
            return None

        files = [i.file for i in self.songPlaylistDao.listBy(name=name)]
        playlist.songInfos = self.songInfoDao.listByIds(files)
        k = self.songInfoDao.fields[0]
        playlist.songInfos.sort(key=lambda i: files.index(i[k]))
        return playlist

    def listByNames(self, names: List[str]) -> List[Playlist]:
        """ list multi playlists by their names """
        playlists = self.playlistDao.listByIds(names)  # type:Playlist

        for playlist in playlists:
            files = [i.file for i in self.songPlaylistDao.listBy(name=playlist.name)]
            playlist.songInfos = self.songInfoDao.listByIds(files)
            k = self.songInfoDao.fields[0]
            playlist.songInfos.sort(key=lambda i: files.index(i[k]))

        return playlists

    def listAll(self) -> List[Playlist]:
        """ list all playlists without detailed song information """
        return self.playlistDao.listAll()

    def listLike(self, **condition) -> List[Playlist]:
        return self.playlistDao.listLike(**condition)

    def modifyName(self, old: str, new: str) -> bool:
        """ modify the name of playlist """
        if not self.playlistDao.update(old, 'name', new):
            return False

        songPlaylists = self.songPlaylistDao.listBy(name=old)
        for songPlaylist in songPlaylists:
            songPlaylist.name = new

        return self.songPlaylistDao.updateByIds(songPlaylists)

    def add(self, playlist: Playlist) -> bool:
        """ create a new playlist """
        songInfo = playlist.songInfos[0] if playlist.songInfos else SongInfo()
        playlist.singer = songInfo.singer
        playlist.album = songInfo.album
        playlist.count = len(playlist.songInfos)
        playlist.modifiedTime = QDateTime.currentDateTime().toSecsSinceEpoch()

        if not self.playlistDao.insert(playlist):
            return False

        songPlaylists = [SongPlaylist(
            UUIDUtils.getUUID(), i.file, playlist.name) for i in playlist.songInfos]
        if not self.songPlaylistDao.insertBatch(songPlaylists):
            return False

        return self.songInfoDao.insertBatch(playlist.songInfos, ignore=True)

    def addSongs(self, name: str, songInfos: List[SongInfo]) -> bool:
        """ add songs to a playlist """
        if not songInfos:
            return False

        playlist = self.playlistDao.selectBy(name=name)  # type:Playlist
        if not playlist:
            return False

        if playlist.count == 0:
            songInfo = songInfos[0]
            playlist.singer = songInfo.singer
            playlist.album = songInfo.album

        playlist.count = playlist.count + len(songInfos)
        playlist.modifiedTime = QDateTime.currentDateTime().toSecsSinceEpoch()

        if not self.playlistDao.updateById(playlist):
            return False

        songPlaylists = [SongPlaylist(
            UUIDUtils.getUUID(), i.file, playlist.name) for i in songInfos]
        if not self.songPlaylistDao.insertBatch(songPlaylists):
            return False

        return self.songInfoDao.insertBatch(songInfos, ignore=True)

    def remove(self, name: str) -> bool:
        """ remove a playlist """
        if not self.playlistDao.deleteById(name):
            return False

        songPlaylists = self.songPlaylistDao.listBy(name=name)
        return self.songPlaylistDao.deleteByIds([i.id for i in songPlaylists])

    def removeBatch(self, names: List[str]) -> bool:
        """ remove multi playlists """
        if not self.playlistDao.deleteByIds(names):
            return False

        songPlaylists = self.songPlaylistDao.listByFields('name', names)
        return self.songPlaylistDao.deleteByIds([i.id for i in songPlaylists])

    def removeSongs(self, name: str, songInfos: List[SongInfo]):
        """ remove songs from playlist """
        files = [i.file for i in songInfos]
        if not self.songPlaylistDao.deleteByNameFiles(name, files):
            return False

        songPlaylist = self.songPlaylistDao.selectBy(name=name)
        if songPlaylist:
            songInfo = self.songInfoDao.selectBy(file=songPlaylist.file)
            count = len(self.songPlaylistDao.listBy(name=name))
        else:
            songInfo = SongInfo()
            count = 0

        playlist = self.playlistDao.selectBy(name=name)  # type:Playlist
        playlist.singer = songInfo.singer
        playlist.album = songInfo.album
        playlist.count = count
        playlist.modifiedTime = QDateTime.currentDateTime().toSecsSinceEpoch()
        return self.playlistDao.updateById(playlist)

    def updateOnlineSongUrl(self, old: str, new: str):
        """ update the url of online song

        Parameters
        ----------
        old: str
            old url

        new: str
            new url
        """
        if not self.songPlaylistDao.updateByField("file", old, new):
            return False

        return self.songInfoDao.updateByField("file", old, new)

    def clearTable(self) -> bool:
        s1 = self.playlistDao.clearTable()
        s2 = self.songPlaylistDao.clearTable()
        s3 = self.songInfoDao.clearTable()
        return s1 and s2 and s3

    def setDatabase(self, db: QSqlDatabase):
        self.playlistDao.setDatabase(db)
        self.songPlaylistDao.setDatabase(db)
        self.songInfoDao.setDatabase(db)
