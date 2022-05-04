# coding:utf-8
from typing import List

from PyQt5.QtSql import QSqlDatabase

from ..dao import SongInfoDao
from ..entity import SongInfo

from.service_base import ServiceBase


class SongInfoService(ServiceBase):
    """ Song information service """

    def __init__(self, db: QSqlDatabase = None):
        super().__init__()
        self.songInfoDao = SongInfoDao(db)

    def createTable(self) -> bool:
        return self.songInfoDao.createTable()

    def findBy(self, **condition) -> SongInfo:
        return self.songInfoDao.selectBy(**condition)

    def findByFile(self, file: str):
        """ find song information by the path of audio file """
        return self.songInfoDao.selectByFile(str(file))

    def listBy(self, **condition) -> List[SongInfo]:
        return self.songInfoDao.listBy(**condition)

    def listLike(self, **condition) -> List[SongInfo]:
        return self.songInfoDao.listLike(**condition)

    def listAll(self) -> List[SongInfo]:
        return self.songInfoDao.listAll()

    def listByIds(self, files: list, repeat=False) -> List[SongInfo]:
        """ list song information by the path of audio files

        Parameters
        ----------
        files: List[str]
            the path of audio files

        repeat: bool
            allow song information to repeat or not
        """
        songInfos = self.songInfoDao.listByIds(files)
        k = self.songInfoDao.fields[0]
        songInfos.sort(key=lambda i: files.index(i[k]))

        if len(songInfos) < len(files) and repeat:
            songInfoMap = {i.file: i for i in songInfos}
            songInfos = [songInfoMap[i].copy() for i in files if i in songInfoMap]

        return songInfos

    def listBySingers(self, singers: List[str])-> List[SongInfo]:
        """ list song information by singer names """
        return self.songInfoDao.listBySingers(singers)

    def listBySingerAlbum(self, singer: str, album: str) -> List[SongInfo]:
        """ list song information by singer name and album name """
        return self.songInfoDao.listBySingerAlbum(singer, album)

    def listBySingerAlbums(self, singers: List[str], albums: List[str]):
        """ list song information by singer names and album names  """
        return self.songInfoDao.listBySingerAlbums(singers, albums)

    def modify(self, file: str, field: str, value) -> bool:
        return self.songInfoDao.update(file, field, value)

    def modifyById(self, songInfo: SongInfo) -> bool:
        return self.songInfoDao.updateById(songInfo)

    def modifyByIds(self, songInfos: List[SongInfo]) -> bool:
        return self.songInfoDao.updateByIds(songInfos)

    def add(self, songInfo: SongInfo) -> bool:
        return self.songInfoDao.insert(songInfo)

    def addBatch(self, songInfos: List[SongInfo]) -> bool:
        return self.songInfoDao.insertBatch(songInfos)

    def removeById(self, file: str) -> bool:
        return self.songInfoDao.deleteById(file)

    def removeByIds(self, files: List[str]) -> bool:
        return self.songInfoDao.deleteByIds(files)

    def clearTable(self) -> bool:
        return self.songInfoDao.clearTable()

    def setDatabase(self, db: QSqlDatabase):
        """ use the specified database """
        self.songInfoDao.setDatabase(db)
