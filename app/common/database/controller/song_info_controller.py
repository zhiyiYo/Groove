# coding:utf-8
from time import time
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
        print('缓存歌曲信息数量：', len(cacheSongInfos))
        print('现存歌曲信息数量：', len(files))

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

        print('新增歌曲信息数量：', len(addedFiles))
        print('移除歌曲信息数量：', len(removedFiles))
        print('过期歌曲信息数量：', len(expiredSongInfos))

        # 更新数据库
        t0 = time()
        self.songInfoService.modifyByIds(expiredSongInfos)
        t1 = time()
        self.songInfoService.addBatch(newSongInfos)
        t2 = time()
        self.songInfoService.removeByIds(
            [str(i).replace('\\', '/') for i in removedFiles])
        t3 = time()
        print('修改歌曲信息耗时：', t1-t0)
        print('新增歌曲信息耗时：', t2-t1)
        print('移除歌曲信息耗时：', t3-t2)

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
