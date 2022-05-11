# coding:utf-8
from pathlib import Path
from typing import List, Union

from common.meta_data.reader import SongInfoReader
from PyQt5.QtSql import QSqlDatabase

from ..entity import SongInfo
from ..service import SongInfoService


class SongInfoController:
    """ Song information controller """

    def __init__(self, db: QSqlDatabase = None):
        self.songInfoService = SongInfoService(db)

    def getSongInfosFromCache(self, files: List[Path]):
        """ get song information from cache and update database

        Parameters
        ----------
        files: List[Path]
            path of audio files

        Returns
        -------
        songInfos: List[SongInfo]
            song information list
        """
        # get all song information from database
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

        # update database
        self.songInfoService.modifyByIds(expiredSongInfos)
        self.songInfoService.addBatch(newSongInfos)
        self.songInfoService.removeByIds(
            [str(i).replace('\\', '/') for i in removedFiles])

        return songInfos

    def getSongInfosBySingers(self, singers: List[str]):
        """ get song information by singer names

        Parameters
        ----------
        singers: str
            singer name list

        Returns
        -------
        songInfos: List[SongInfo]
            song information list
        """
        return self.songInfoService.listBySingers(singers)

    def getSongInfosBySingerAlbum(self, singers: List[str], albums: List[str]):
        """ get song information by singer names and album names

        Parameters
        ----------
        singers: List[str]
            singer list

        albums: List[str]
            album list

        Returns
        -------
        songInfos: List[SongInfo]
            song information list
        """
        return self.songInfoService.listBySingerAlbums(singers, albums)

    def getSongInfosByFile(self, files: List[str]):
        """ get song information list by path of audio files """
        return self.songInfoService.listByIds(files)

    def getSongInfoByFile(self, file: str):
        """ get song information by path of audio file """
        return self.songInfoService.findByFile(file)

    def getSongInfosLike(self, **condition):
        """ fuzzy search song information """
        return self.songInfoService.listLike(**condition)

    def addSongInfos(self, files: List[Path]):
        """ add song information to database """
        reader = SongInfoReader()
        songInfos = [reader.read(i) for i in files]
        songInfos.sort(key=lambda i: i.createTime, reverse=True)

        # 更新数据库
        self.songInfoService.addBatch(songInfos)
        return songInfos

    def removeSongInfos(self, files: List[Path]) -> List[str]:
        """ remove song information from database """
        files = [str(i).replace('\\', '/') for i in files]
        self.songInfoService.removeByIds(files)
        return files

    def updateSongInfo(self, songInfo: SongInfo):
        """ update song information """
        return self.songInfoService.modifyById(songInfo)

    def updateMultiSongInfos(self, songInfos: List[SongInfo]):
        """ update multi song information """
        return self.songInfoService.modifyByIds(songInfos)

    def getSongInfosFromFile(self, files: List[Union[str, Path]]):
        """ get song information from files and do not operate the database """
        reader = SongInfoReader()
        return [reader.read(i) for i in files]
