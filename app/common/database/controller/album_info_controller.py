# coding:utf-8
from typing import Dict, List

from common.singleton import Singleton
from PyQt5.QtSql import QSqlDatabase

from ..entity import AlbumInfo, SongInfo
from ..service import AlbumInfoService, SongInfoService
from ..utils import UUIDUtils


class AlbumInfoController:
    """ Album information controller """

    def __init__(self, db: QSqlDatabase = None):
        self.albumInfoService = AlbumInfoService(db)
        self.songInfoService = SongInfoService(db)

    def getAlbumInfosFromCache(self, songInfos: List[SongInfo]):
        """ get album information list from cache

        Parameters
        ----------
        songInfos: List[SongInfo]
            song information list

        Returns
        -------
        albumInfos: List[AlbumInfo]
            album information list, not contain song information
        """
        # get all album information from database
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

        # update database
        self.albumInfoService.removeByIds(removedIds)
        self.albumInfoService.modifyByIds(list(expiredAlbumInfos.values()))
        self.albumInfoService.addBatch(addedAlbumInfos)

        # sort album information
        albumInfos = sorted(
            currentAlbumInfos.values(),
            key=lambda i: i.modifiedTime,
            reverse=True
        )

        return albumInfos

    def getAlbumInfo(self, singer: str, album: str):
        """ get an album information from the database

        Paramters
        ---------
        singer: str
            singer name

        album: str
            album name

        Returns
        -------
        albumInfo: AlbumInfo
            album information, contains song information, `None` if no album is found
        """
        albumInfo = self.albumInfoService.findBy(singer=singer, album=album)
        if not albumInfo:
            return None

        albumInfo.songInfos = self.songInfoService.listBySingerAlbum(
            singer, album)

        albumInfo.songInfos.sort(key=lambda i: i.track or 0)
        return albumInfo

    def getAlbumInfosBySinger(self, singer: str):
        """ get all albums of singer

        Paramters
        ---------
        singer: str
            singer name

        Returns
        -------
        albumInfos: List[AlbumInfo]
            album information list, not contain song information, empty if no albums if found
        """
        albumInfos = self.albumInfoService.listBy(singer=singer)
        albumInfos.sort(key=lambda i: i.year or 0, reverse=True)
        return albumInfos

    def getAlbumInfosLike(self, **condition):
        """ fuzzy search album information """
        return self.albumInfoService.listLike(**condition)

    def getAlbumInfos(self, songInfos: List[SongInfo]) -> List[AlbumInfo]:
        """ get album information from new song information and update the database

        Parameters
        ----------
        songInfos: List[SongInfo]
            song information list

        Returns
        -------
        albumInfos: List[AlbumInfo]
            album information list, not contain song information
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

        # sort album information
        albumInfos = sorted(
            albumInfos.values(),
            key=lambda i: i.modifiedTime,
            reverse=True
        )

        # update database
        self.albumInfoService.clearTable()
        self.albumInfoService.addBatch(albumInfos)

        return albumInfos
