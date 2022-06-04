# coding:utf-8
from typing import Dict, List

from common.meta_data.reader import SongInfoReader
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

        reader = SongInfoReader()
        addedAlbumInfos = []    # type: List[AlbumInfo]
        expiredAlbumInfos = {}  # type:Dict[str, AlbumInfo]
        currentAlbumInfos = {}  # type:Dict[str, AlbumInfo]
        for songInfo in songInfos:
            key = songInfo.singer + '_' + songInfo.album
            year = songInfo.year
            genre = songInfo.genre
            t = songInfo.createTime

            if key in cacheAlbumInfos:
                albumInfo = currentAlbumInfos[key] = cacheAlbumInfos[key]

                if albumInfo.modifiedTime < t:
                    albumInfo.modifiedTime = t
                    expiredAlbumInfos[key] = cacheAlbumInfos[key]

                if not albumInfo.year and year:
                    albumInfo.year = year
                    expiredAlbumInfos[key] = cacheAlbumInfos[key]

                if (not albumInfo.genre and genre) or (albumInfo.genre == reader.genre and genre != reader.genre):
                    albumInfo.genre = genre
                    expiredAlbumInfos[key] = cacheAlbumInfos[key]

            # create new album info
            elif key not in currentAlbumInfos:
                albumInfo = self.__createAlbumInfo(songInfo)
                currentAlbumInfos[key] = albumInfo
                addedAlbumInfos.append(albumInfo)

            else:
                albumInfo = currentAlbumInfos[key]
                if albumInfo.modifiedTime < t:
                    albumInfo.modifiedTime = t

                if not albumInfo.year and year:
                    albumInfo.year = year

                if (not albumInfo.genre and genre) or (albumInfo.genre == reader.genre and genre != reader.genre):
                    albumInfo.genre = genre

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

    def updateBySongInfo(self, old: SongInfo, new: SongInfo):
        """ update album information by song information, you should call
        this function after updating song info table

        Parameters
        ----------
        old: SongInfo
            old song information

        new: SongInfo
            new song information

        Returns
        -------
        albumInfos: List[AlbumInfo]
            album information list, not contain song information
        """
        oldKey = old.singer + '_' + old.album
        newKey = new.singer + '_' + new.album
        reader = SongInfoReader()

        if oldKey == newKey:
            albumInfo = self.albumInfoService.findBy(
                singer=old.singer, album=old.album)
            if albumInfo:
                albumInfo.year = new.year
                albumInfo.genre = new.genre
                self.albumInfoService.modifyById(albumInfo)
        else:
            # remove empty album info or update its modified time
            albumInfo = self.getAlbumInfo(old.singer, old.album)
            if albumInfo:
                if len(albumInfo.songInfos) == 0:
                    self.albumInfoService.removeById(albumInfo.id)
                else:
                    albumInfo.modifiedTime = max(
                        i.createTime for i in albumInfo.songInfos)
                    self.albumInfoService.modifyById(albumInfo)

            # create new album info or add song info to existing album
            albumInfo = self.albumInfoService.findBy(
                singer=new.singer, album=new.album)
            if not albumInfo:
                self.albumInfoService.add(self.__createAlbumInfo(new))
            else:
                albumInfo.modifiedTime = max(
                    albumInfo.modifiedTime, new.createTime)
                if albumInfo.year == reader.year and new.year != reader.year:
                    albumInfo.year = new.year
                if albumInfo.genre == reader.genre and new.genre != reader.genre:
                    albumInfo.genre = new.genre

                self.albumInfoService.modifyById(albumInfo)

        albumInfos = sorted(
            self.albumInfoService.listAll(),
            key=lambda i: i.modifiedTime,
            reverse=True
        )
        return albumInfos

    def updateBySongInfos(self, olds: List[SongInfo], news: List[SongInfo]):
        """ update album information by multi song information, you should call
        this function after updating song info table

        Parameters
        ----------
        olds: List[SongInfo]
            old song information

        news: List[SongInfo]
            new song information

        Returns
        -------
        albumInfos: List[AlbumInfo]
            album information list, not contain song information
        """
        # remove old album information
        singers = [i.singer for i in olds]
        albums = [i.album for i in olds]
        oldAlbumIds = [
            i.id for i in self.albumInfoService.listBySingerAlbums(singers, albums)]
        self.albumInfoService.removeByIds(oldAlbumIds)

        # insert new album information
        newAlbumInfos = {}  # type:Dict[str, AlbumInfo]
        reader = SongInfoReader()

        for songInfo in news:
            key = songInfo.singer + '_' + songInfo.album
            year = songInfo.year
            genre = songInfo.genre
            t = songInfo.createTime

            if key not in newAlbumInfos:
                newAlbumInfos[key] = self.__createAlbumInfo(songInfo)
            else:
                albumInfo = newAlbumInfos[key]
                if albumInfo.modifiedTime < t:
                    albumInfo.modifiedTime = t

                if not albumInfo.year and year:
                    albumInfo.year = year

                if (not albumInfo.genre and genre) or (
                        albumInfo.genre == reader.genre and genre != reader.genre):
                    albumInfo.genre = genre

        # update database
        singers = [i.singer for i in news]
        albums = [i.album for i in news]
        self.albumInfoService.removeBySingerAlbums(singers, albums)
        self.albumInfoService.addBatch(list(newAlbumInfos.values()))

        albumInfos = sorted(
            self.albumInfoService.listAll(),
            key=lambda i: i.modifiedTime,
            reverse=True
        )
        return albumInfos

    def __createAlbumInfo(self, songInfo: SongInfo):
        return AlbumInfo(
            id=UUIDUtils.getUUID(),
            singer=songInfo.singer,
            album=songInfo.album,
            year=songInfo.year,
            genre=songInfo.genre,
            modifiedTime=songInfo.createTime
        )
