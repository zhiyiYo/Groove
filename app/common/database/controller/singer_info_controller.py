# coding:utf-8
from typing import List, Dict

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

        addedSingerInfos = []    # type: List[SingerInfo]
        expiredAlbumInfos = {}  # type: Dict[str, SingerInfo]
        currentSingerInfos = {}  # type: Dict[str, SingerInfo]
        for albumInfo in albumInfos:
            singer = albumInfo.singer
            genre = albumInfo.genre

            if singer in cacheSingerInfos:
                currentSingerInfos[singer] = cacheSingerInfos[singer]

                if not currentSingerInfos[singer].genre and genre:
                    currentSingerInfos[singer].genre = genre
                    expiredAlbumInfos[singer] = cacheSingerInfos[singer]

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
        self.singerInfoService.modifyByIds(list(expiredAlbumInfos.values()))
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

        for albumInfo in albumInfos:
            singer = albumInfo.singer
            genre = albumInfo.genre

            if singer not in albumInfos:
                singerInfos[singer] = SingerInfo(
                    id=UUIDUtils.getUUID(),
                    singer=singer,
                    genre=genre
                )
            elif not singerInfos[singer].genre and genre:
                singerInfos[singer].genre = genre

        singerInfos = list(singerInfos.values())

        # update database
        self.singerInfoService.clearTable()
        self.singerInfoService.addBatch(singerInfos)

        return singerInfos

    def getSingerInfoByName(self, singer: str):
        """ get singer information by singer name """
        return self.singerInfoService.findBy(singer=singer)