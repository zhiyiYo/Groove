# coding:utf-8
from typing import List

from ..dao import AlbumInfoDao
from ..entity import AlbumInfo

from.service_base import ServiceBase


class AlbumInfoService(ServiceBase):
    """ 专辑信息服务类 """

    def __init__(self):
        super().__init__()
        self.albumInfoDao = AlbumInfoDao()

    def createTable(self) -> bool:
        return self.albumInfoDao.createTable()

    def findBy(self, **condition) -> AlbumInfo:
        return self.albumInfoDao.selectBy(**condition)

    def listBy(self, **condition) -> List[AlbumInfo]:
        return self.albumInfoDao.listBy(**condition)

    def listAll(self) -> List[AlbumInfo]:
        return self.albumInfoDao.listAll()

    def modify(self, id: str, field: str, value) -> bool:
        return self.albumInfoDao.update(id, field, value)

    def modifyById(self, albumInfo: AlbumInfo) -> bool:
        return self.albumInfoDao.updateById(albumInfo)

    def modifyByIds(self, albumInfos: List[AlbumInfo]) -> bool:
        return self.albumInfoDao.updateByIds(albumInfos)

    def add(self, albumInfo: AlbumInfo) -> bool:
        return self.albumInfoDao.insert(albumInfo)

    def addBatch(self, albumInfos: List[AlbumInfo]) -> bool:
        return self.albumInfoDao.insertBatch(albumInfos)

    def removeById(self, id: str) -> bool:
        return self.albumInfoDao.deleteById(id)

    def removeByIds(self, ids: List[str]) -> bool:
        return self.albumInfoDao.deleteByIds(ids)

    def clearTable(self) -> bool:
        """ 清空表格数据 """
        return self.albumInfoDao.clearTable()
