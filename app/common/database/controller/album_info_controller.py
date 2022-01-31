# coding:utf-8
from typing import Dict, List

from common.singleton import Singleton
from PyQt5.QtSql import QSqlDatabase

from ..entity import AlbumInfo, SongInfo
from ..service import AlbumInfoService, SongInfoService
from ..utils import UUIDUtils


class AlbumInfoController:
    """ 专辑信息控制器 """

    def __init__(self, db: QSqlDatabase = None):
        self.albumInfoService = AlbumInfoService(db)
        self.songInfoService = SongInfoService(db)

    def getAlbumInfosFromCache(self, songInfos: List[SongInfo]):
        """ 从缓存获取专辑信息列表

        Parameters
        ----------
        songInfos: List[SongInfo]
            歌曲信息列表

        Returns
        -------
        albumInfos: List[AlbumInfo]
            专辑信息列表，不包含歌曲信息
        """
        # 从数据库获取所有专辑信息
        cacheAlbumInfos = {
            (i.singer+'_'+i.album): i for i in self.albumInfoService.listAll()
        }

        addedAlbumInfos = []    # type: List[AlbumInfo]
        expiredAlbumInfos = {}  # type:Dict[str, AlbumInfo]
        currentAlbumInfos = {}  # type:Dict[str, AlbumInfo]
        for songInfo in songInfos:
            key = songInfo.singer + '_' + songInfo.album
            year = songInfo.year
            genre = songInfo.genre
            t = songInfo.modifiedTime

            if key in cacheAlbumInfos:
                currentAlbumInfos[key] = cacheAlbumInfos[key]

                if currentAlbumInfos[key].modifiedTime < t:
                    currentAlbumInfos[key].modifiedTime = t
                    expiredAlbumInfos[key] = cacheAlbumInfos[key]

                if not currentAlbumInfos[key].year and year:
                    currentAlbumInfos[key].year = year
                    expiredAlbumInfos[key] = cacheAlbumInfos[key]

                if not currentAlbumInfos[key].genre and genre:
                    currentAlbumInfos[key].genre = genre
                    expiredAlbumInfos[key] = cacheAlbumInfos[key]

            elif key not in currentAlbumInfos:
                albumInfo = AlbumInfo(
                    id=UUIDUtils.getUUID(),
                    singer=songInfo.singer,
                    album=songInfo.album,
                    year=songInfo.year,
                    genre=songInfo.genre,
                    modifiedTime=t
                )
                currentAlbumInfos[key] = albumInfo
                addedAlbumInfos.append(albumInfo)

            else:
                if currentAlbumInfos[key].modifiedTime < t:
                    currentAlbumInfos[key].modifiedTime = t

                if not currentAlbumInfos[key].year and year:
                    currentAlbumInfos[key].year = year

                if not currentAlbumInfos[key].genre and genre:
                    currentAlbumInfos[key].genre = genre

        removedIds = []
        for i in set(cacheAlbumInfos.keys())-set(currentAlbumInfos.keys()):
            removedIds.append(cacheAlbumInfos[i].id)

        # 更新数据库
        self.albumInfoService.removeByIds(removedIds)
        self.albumInfoService.modifyByIds(list(expiredAlbumInfos.values()))
        self.albumInfoService.addBatch(addedAlbumInfos)

        # 排序专辑信息
        albumInfos = sorted(
            currentAlbumInfos.values(),
            key=lambda i: i.modifiedTime,
            reverse=True
        )

        return albumInfos

    def getAlbumInfo(self, singer: str, album: str):
        """ 从数据库获取一张专辑信息

        Paramters
        ---------
        singer: str
            歌手

        album: str
            专辑

        Returns
        -------
        albumInfo: AlbumInfo
            专辑信息，包含歌曲信息列表，没有找到则返回 None
        """
        albumInfo = self.albumInfoService.findBy(singer=singer, album=album)
        if not albumInfo:
            return None

        albumInfo.songInfos = self.songInfoService.listBySingerAlbum(
            singer, album)

        albumInfo.songInfos.sort(key=lambda i: i.track or 0)
        return albumInfo

    def getAlbumInfosBySinger(self, singer: str):
        """ 从数据库获取一张空专辑信息

        Paramters
        ---------
        singer: str
            歌手

        Returns
        -------
        albumInfo: AlbumInfo
            专辑信息，不包含歌曲信息列表，没有找到则返回 None
        """
        albumInfos = self.albumInfoService.listBy(singer=singer)
        albumInfos.sort(key=lambda i: i.year or 0, reverse=True)
        return albumInfos

    def getAlbumInfosLike(self, **condition):
        """ 模糊查询专辑信息 """
        return self.albumInfoService.listLike(**condition)

    def getAlbumInfos(self, songInfos: List[SongInfo]) -> List[AlbumInfo]:
        """ 从新的歌曲信息列表获取专辑信息并更新数据库

        Parameters
        ----------
        songInfos: List[SongInfo]
            歌曲信息列表

        Returns
        -------
        albumInfos: List[AlbumInfo]
            专辑信息列表，不包含歌曲信息
        """
        albumInfos = {}  # type:Dict[str, AlbumInfo]

        for songInfo in songInfos:
            key = songInfo.singer + '_' + songInfo.album
            year = songInfo.year
            genre = songInfo.genre
            t = songInfo.modifiedTime

            if key not in albumInfos:
                albumInfos[key] = AlbumInfo(
                    id=UUIDUtils.getUUID(),
                    singer=songInfo.singer,
                    album=songInfo.album,
                    year=songInfo.year,
                    genre=songInfo.genre,
                    modifiedTime=t
                )
            else:
                if albumInfos[key].modifiedTime < t:
                    albumInfos[key].modifiedTime = t

                if not albumInfos[key].year and year:
                    albumInfos[key].year = year

                if not albumInfos[key].genre and genre:
                    albumInfos[key].genre = genre

        # 排序专辑信息
        albumInfos = sorted(
            albumInfos.values(),
            key=lambda i: i.modifiedTime,
            reverse=True
        )

        # 更新数据库
        self.albumInfoService.clearTable()
        self.albumInfoService.addBatch(albumInfos)

        return albumInfos
