# coding:utf-8
from typing import List

from PyQt5.QtCore import QDateTime
from PyQt5.QtSql import QSqlDatabase

from ..dao import PlaylistDao, SongPlaylistDao, SongInfoDao
from ..entity import Playlist, SongPlaylist, SongInfo
from ..utils import UUIDUtils

from.service_base import ServiceBase


class PlaylistService(ServiceBase):
    """ 播放列表服务类 """

    def __init__(self, db: QSqlDatabase = None):
        super().__init__()
        self.playlistDao = PlaylistDao(db)
        self.songPlaylistDao = SongPlaylistDao(db)
        self.songInfoDao = SongInfoDao(db)

    def createTable(self) -> bool:
        s1 = self.playlistDao.createTable()
        s2 = self.songPlaylistDao.createTable()
        return s1 and s2

    def findByName(self, name: str) -> Playlist:
        """ 通过名字查询单张播放列表，没找到返回 None """
        playlist = self.playlistDao.selectBy(name=name)  # type:Playlist
        if not playlist:
            return None

        for songPlaylist in self.songPlaylistDao.listBy(name=playlist.name):
            songInfo = SongInfo(songPlaylist.file)
            songInfo['id'] = songPlaylist.id
            playlist.songInfos.append(songInfo)

        return playlist

    def listByNames(self, names: str) -> List[Playlist]:
        """ 通过名字查询多张播放列表 """
        playlists = self.playlistDao.listByIds(names)  # type:Playlist

        for playlist in playlists:
            for songPlaylist in self.songPlaylistDao.listBy(name=playlist.name):
                songInfo = SongInfo(songPlaylist.file)
                songInfo['id'] = songPlaylist.id
                playlist.songInfos.append(songInfo)

        return playlists

    def listAll(self) -> List[Playlist]:
        """ 查询所有播放列表，不会查询出歌曲信息，只有歌曲文件位置 """
        return self.playlistDao.listAll()

    def modifyName(self, old: str, new: str) -> bool:
        """ 修改播放列表的名字 """
        s1 = self.playlistDao.update(old, 'name', new)
        if not s1:
            return False

        songPlaylists = self.songPlaylistDao.listBy(name=old)
        for songPlaylist in songPlaylists:
            songPlaylist.name = new

        return self.songPlaylistDao.updateByIds(songPlaylists)

    def add(self, playlist: Playlist) -> bool:
        """ 创建一个播放列表 """
        songInfo = playlist.songInfos[0] if playlist.songInfos else SongInfo()
        playlist.singer = songInfo.singer
        playlist.album = songInfo.album
        playlist.count = len(playlist.songInfos)
        playlist.modifiedTime = QDateTime.currentDateTime().toSecsSinceEpoch()

        s1 = self.playlistDao.insert(playlist)
        if not s1:
            return False

        songPlaylists = [SongPlaylist(
            UUIDUtils.getUUID(), i.file, playlist.name) for i in playlist.songInfos]
        return self.songPlaylistDao.insertBatch(songPlaylists)

    def addSongs(self, name: str, songInfos: List[SongInfo]) -> bool:
        """ 添加歌曲到指定的播放列表中 """
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

        s1 = self.playlistDao.updateById(playlist)
        if not s1:
            return False

        songPlaylists = [SongPlaylist(
            UUIDUtils.getUUID(), i.file, playlist.name) for i in songInfos]
        return self.songPlaylistDao.insertBatch(songPlaylists)

    def remove(self, name: str) -> bool:
        """ 移除一个播放列表 """
        s1 = self.playlistDao.deleteById(name)
        if not s1:
            return False

        songPlaylists = self.songPlaylistDao.listBy(name=name)
        return self.songPlaylistDao.deleteByIds([i.id for i in songPlaylists])

    def removeBatch(self, names: List[str]) -> bool:
        """ 移除多张播放列表 """
        s1 = self.playlistDao.deleteByIds(names)
        if not s1:
            return False

        songPlaylists = self.songPlaylistDao.listByFields('name', names)
        return self.songPlaylistDao.deleteByIds([i.id for i in songPlaylists])

    def removeSongs(self, name: str, songInfos: List[str]):
        """ 从指定的播放列表中移除歌曲 """
        ids = [i['id'] for i in songInfos]
        s1 = self.songPlaylistDao.deleteByIds(ids)
        if not s1:
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

    def clearTable(self) -> bool:
        s1 = self.playlistDao.clearTable()
        s2 = self.songPlaylistDao.clearTable()
        return s1 and s2

    def setDatabase(self, db: QSqlDatabase):
        self.playlistDao.setDatabase(db)
        self.songPlaylistDao.setDatabase(db)
        self.songInfoDao.setDatabase(db)
