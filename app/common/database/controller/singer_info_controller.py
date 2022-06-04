# coding:utf-8
from typing import Dict, List

from common.meta_data.reader import SongInfoReader
from PyQt5.QtSql import QSqlDatabase

from ..entity import AlbumInfo, SingerInfo
from ..service import SingerInfoService
from ..utils import UUIDUtils


class SingerInfoController:
    """ Singer information controller """

    def __init__(self, db: QSqlDatabase = None) -> None:
        self.singerInfoService = SingerInfoService(db)

    def getSingerInfosFromCache(self, albumInfos: List[AlbumInfo]) -> List[SingerInfo]:
        """ get singer infortion from cache

        Parameters
        ----------
        albumInfos: List[AlbumInfo]
            album information list

        Returns
        -------
        singerInfos: List[SingerInfo]
            singer information list
        """
        cacheSingerInfos = {
            i.singer: i for i in self.singerInfoService.listAll()
        }

        reader = SongInfoReader()
        addedSingerInfos = []    # type: List[SingerInfo]
        expiredSingerInfos = {}  # type: Dict[str, SingerInfo]
        currentSingerInfos = {}  # type: Dict[str, SingerInfo]

        for albumInfo in albumInfos:
            singer = albumInfo.singer
            genre = albumInfo.genre

            if singer in cacheSingerInfos:
                singerInfo = currentSingerInfos[singer] = cacheSingerInfos[singer]

                if (not singerInfo.genre and genre) or (
                        singerInfo.genre == reader.genre and genre != reader.genre):
                    singerInfo.genre = genre
                    expiredSingerInfos[singer] = cacheSingerInfos[singer]

            elif singer not in currentSingerInfos:
                singerInfo = SingerInfo(
                    id=UUIDUtils.getUUID(),
                    singer=singer,
                    genre=genre
                )
                currentSingerInfos[singer] = singerInfo
                addedSingerInfos.append(singerInfo)

        removedIds = []
        for i in set(cacheSingerInfos.keys())-set(currentSingerInfos.keys()):
            removedIds.append(cacheSingerInfos[i].id)

        # update database
        self.singerInfoService.removeByIds(removedIds)
        self.singerInfoService.modifyByIds(list(expiredSingerInfos.values()))
        self.singerInfoService.addBatch(addedSingerInfos)

        return list(currentSingerInfos.values())

    def getSingerInfos(self, albumInfos: List[AlbumInfo]) -> List[SingerInfo]:
        """ get singer information from album information and update database

        Parameters
        ----------
        albumInfos: List[AlbumInfo]
            album information list

        Returns
        -------
        singerInfos: List[SingerInfo]
            singer information list
        """
        singerInfos = {}  # type:Dict[str, SingerInfo]
        reader = SongInfoReader()

        for albumInfo in albumInfos:
            singer = albumInfo.singer
            genre = albumInfo.genre

            if singer not in albumInfos:
                singerInfos[singer] = SingerInfo(
                    id=UUIDUtils.getUUID(),
                    singer=singer,
                    genre=genre
                )
            elif (not singerInfos[singer].genre and genre) or (
                    singerInfos[singer].genre == reader.genre and genre != reader.genre):
                singerInfos[singer].genre = genre

        singerInfos = list(singerInfos.values())

        # update database
        self.singerInfoService.clearTable()
        self.singerInfoService.addBatch(singerInfos)

        return singerInfos

    def getSingerInfoByName(self, singer: str):
        """ get singer information by singer name """
        return self.singerInfoService.findBy(singer=singer)

    def getSingerInfosLike(self, **condition):
        """ fuzzy search album information """
        return self.singerInfoService.listLike(**condition)
