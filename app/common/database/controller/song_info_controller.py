# coding:utf-8
from typing import Union, List
from pathlib import Path

from common.meta_data.reader import SongInfoReader

from ..entity import SongInfo
from ..service import SongInfoService


class SongInfoController:
    """ 歌曲信息控制器 """

    def __init__(self):
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
        cacheSongInfoMaps = {Path(i.file): i for i in cacheSongInfos}

        cacheFiles = set(cacheSongInfoMaps.keys())
        currentFiles = set(files)
        newFiles = currentFiles - cacheFiles
        commonFiles = currentFiles & cacheFiles
        removedFiles = cacheFiles - currentFiles
        print(len(cacheSongInfos))

        reader = SongInfoReader()
        songInfos = []          # type:List[SongInfo]
        expiredSongInfos = []   # type:List[SongInfo]
        for file in commonFiles:
            songInfo = cacheSongInfoMaps[file]
            if songInfo.modifiedTime == int(file.stat().st_mtime):
                songInfos.append(songInfo)
            else:
                songInfo = reader.read(file)
                songInfos.append(songInfo)
                expiredSongInfos.append(songInfo)

        newSongInfos = [reader.read(i) for i in newFiles]
        songInfos.extend(newSongInfos)
        songInfos.sort(key=lambda i: i.createTime, reverse=True)

        # 更新数据库
        self.songInfoService.removeByIds(
            [str(i).replace('\\', '/') for i in removedFiles])
        self.songInfoService.addBatch(newSongInfos)
        for songInfo in expiredSongInfos:
            self.songInfoService.modifyById(songInfo)

        return songInfos