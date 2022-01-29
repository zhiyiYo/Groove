# coding:utf-8
from pathlib import Path
from typing import List, Union

from PyQt5.QtSql import QSqlDatabase

from ..entity import SongInfo, Playlist
from ..service import SongInfoService, PlaylistService


class PlaylistController:
    """ 播放列表控制器 """

    def __init__(self, db: QSqlDatabase = None):
        self.songInfoService = SongInfoService(db)
        self.playlistService = PlaylistService(db)

    def getAllPlaylists(self):
        """ 获取所有播放列表 """
        playlists = self.playlistService.listAll()

        for playlist in playlists:
            files = [i.file for i in playlist.songInfos]
            playlist.songInfos = self.songInfoService.listByIds(files)

        return playlists

    def getPlaylist(self, name: str):
        """ 获取一张播放列表 """
        playlist = self.playlistService.findByName(name)
        files = [i.file for i in playlist.songInfos]
        playlist.songInfos = self.songInfoService.listByIds(files)
        return playlist

    def getPlaylists(self, names: List[str]):
        """ 获取多张播放列表 """
        playlists = self.playlistService.listByNames(names)
        
        for playlist in playlists:
            files = [i.file for i in playlist.songInfos]
            playlist.songInfos = self.songInfoService.listByIds(files)

        return playlists

    def create(self, playlist: Playlist):
        """ 创建播放列表 """
        return self.playlistService.add(playlist)

    def rename(self, old: str, new: str):
        """ 重命名播放列表 """
        return self.playlistService.modifyName(old, new)

    def delete(self, name: str):
        """ 删除一个播放列表 """
        return self.playlistService.remove(name)

    def deleteBatch(self, names: List[str]):
        """ 删除多张播放列表 """
        return self.playlistService.removeBatch(names)
