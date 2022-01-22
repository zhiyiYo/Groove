# coding:utf-8
from typing import List

from ..dao import SongInfoDao
from ..entity import SongInfo

from.service_base import ServiceBase


class SongInfoService(ServiceBase):
    """ 歌曲信息服务类 """

    def __init__(self):
        super().__init__()
        self.songInfoDao = SongInfoDao()

    def createTable(self) -> bool:
        return self.songInfoDao.createTable()

    def findBy(self, **condition) -> SongInfo:
        return self.songInfoDao.selectBy(condition)

    def findByFile(self, file: str):
        """ 通过文件路径查询歌曲信息 """
        return self.songInfoDao.selectByFile(str(file))

    def listBy(self, **condition) -> List[SongInfo]:
        return self.songInfoDao.listBy(condition)

    def listAll(self) -> List[SongInfo]:
        return self.songInfoDao.listAll()

    def listBySingerAlbum(self, singer: str, album: str) -> List[SongInfo]:
        """ 通过歌手和专辑查询所有歌曲信息 """
        return self.songInfoDao.listBySingerAlbum(singer, album)

    def modify(self, file: str, field: str, value) -> bool:
        return self.songInfoDao.update(file, field, value)

    def modifyById(self, songInfo: SongInfo) -> bool:
        return self.songInfoDao.updateById(songInfo)

    def add(self, songInfo: SongInfo) -> bool:
        return self.songInfoDao.insert(songInfo)

    def addBatch(self, songInfos: List[SongInfo]) -> bool:
        return self.songInfoDao.insertBatch(songInfos)

    def removeById(self, file: str) -> bool:
        return self.songInfoDao.deleteById(file)

    def removeByIds(self, files: List[str]) -> bool:
        return self.songInfoDao.deleteByIds(files)
