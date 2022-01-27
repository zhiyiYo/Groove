# coding:utf-8
from typing import Dict, List

from common.database.entity import SongInfo
from common.meta_data.reader import AlbumCoverReader
from common.singleton import Singleton


class AlbumCoverController:
    """ 专辑封面控制器 """

    def __init__(self):
        super().__init__()
        self.albumCoverReader = AlbumCoverReader()

    def getAlbumCovers(self, songInfos: List[SongInfo]):
        """ 获取专辑封面 """
        self.albumCoverReader.getAlbumCovers(songInfos)