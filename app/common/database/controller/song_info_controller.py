# coding:utf-8
from typing import Union, List
from pathlib import Path

from common.meta_data.reader import SongInfoReader
from common.singleton import Singleton

from ..entity import SongInfo
from ..service import SongInfoService


class SongInfoController(Singleton):
    """ 歌曲信息控制器 """

    def __init__(self):
        super().__init__()
        self.songInfoService = SongInfoService()

    def getSongInfos(self, files: List[Path]):
        """ 获取歌曲信息

        Parameters
        ----------
        files: List[Path]
            音频文件路径列表

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
        self.songInfoService.removeByIds(
            [str(i).replace('\\', '/') for i in removedFiles])
        self.songInfoService.addBatch(newSongInfos)
        for songInfo in expiredSongInfos:
            self.songInfoService.modifyById(songInfo)

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
