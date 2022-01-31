# coding:utf-8
from pathlib import Path
from time import time
from typing import List, Union

from common.meta_data.reader import SongInfoReader
from common.singleton import Singleton
from PyQt5.QtSql import QSqlDatabase

from ..entity import SongInfo
from ..service import SongInfoService


class SongInfoController:
    """ 歌曲信息控制器 """

    def __init__(self, db: QSqlDatabase = None):
        self.songInfoService = SongInfoService(db)

    def getSongInfosFromCache(self, files: List[Path]):
        """ 从缓存获取并更新歌曲信息

        Parameters
        ----------
        files: List[Path]
            音频文件路径列表s

        Returns
        -------
        songInfos: List[SongInfo]
            歌曲信息列表
        """
        # 从数据库中获取所有歌曲信息
        cacheSongInfos = self.songInfoService.listAll()
        cacheSongInfoMap = {Path(i.file): i for i in cacheSongInfos}

        cacheFiles = set(cacheSongInfoMap.keys())
        currentFiles = set(files)
        addedFiles = currentFiles - cacheFiles
        commonFiles = currentFiles & cacheFiles
        removedFiles = cacheFiles - currentFiles

        reader = SongInfoReader()
        songInfos = []          # type:List[SongInfo]
        expiredSongInfos = []   # type:List[SongInfo]
        for file in commonFiles:
            songInfo = cacheSongInfoMap[file]
            if songInfo.modifiedTime == int(file.stat().st_mtime):
                songInfos.append(songInfo)
            else:
                songInfo = reader.read(file)
                songInfos.append(songInfo)
                expiredSongInfos.append(songInfo)

        newSongInfos = [reader.read(i) for i in addedFiles]
        songInfos.extend(newSongInfos)
        songInfos.sort(key=lambda i: i.createTime, reverse=True)

        # 更新数据库
        self.songInfoService.modifyByIds(expiredSongInfos)
        self.songInfoService.addBatch(newSongInfos)
        self.songInfoService.removeByIds(
            [str(i).replace('\\', '/') for i in removedFiles])

        return songInfos

    def getSongInfosBySingerAlbum(self, singers: List[str], albums: List[str]):
        """ 通过歌手和专辑列表查询歌曲信息

        Parameters
        ----------
        singers: List[str]
            歌手列表

        albums: List[str]
            专辑列表

        Returns
        -------
        songInfos: List[SongInfo]
            歌曲信息列表
        """
        return self.songInfoService.listBySingerAlbums(singers, albums)

    def getSongInfosByFile(self, files: List[str]):
        """ 通过文件路径查询歌曲信息列表 """
        return self.songInfoService.listByIds(files)

    def getSongInfoByFile(self, file: str):
        """ 通过文件路径查询歌曲信息 """
        return self.songInfoService.findByFile(file)

    def getSongInfosLike(self, **condition):
        """ 模糊查询符合条件的歌曲信息 """
        return self.songInfoService.listLike(**condition)

    def addSongInfos(self, files: List[Path]):
        """ 向数据库中添加歌曲信息 """
        reader = SongInfoReader()
        songInfos = [reader.read(i) for i in files]
        songInfos.sort(key=lambda i: i.createTime, reverse=True)

        # 更新数据库
        self.songInfoService.addBatch(songInfos)
        return songInfos

    def removeSongInfos(self, files: List[Path]) -> List[str]:
        """ 从数据库中移除歌曲信息 """
        files = [str(i).replace('\\', '/') for i in files]
        self.songInfoService.removeByIds(files)
        return files

    def updateSongInfo(self, songInfo: SongInfo):
        """ 更新一首歌曲信息 """
        return self.songInfoService.modifyById(songInfo)

    def updateMultiSongInfos(self, songInfos: List[SongInfo]):
        """ 更新多首歌曲信息 """
        return self.songInfoService.modifyByIds(songInfos)