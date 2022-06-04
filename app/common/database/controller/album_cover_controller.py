# coding:utf-8
from typing import List

from common.database.entity import SongInfo
from common.meta_data.reader import AlbumCoverReader


class AlbumCoverController:
    """ Album cover controller """

    def __init__(self):
        self.albumCoverReader = AlbumCoverReader()

    def getAlbumCovers(self, songInfos: List[SongInfo]):
        self.albumCoverReader.getAlbumCovers(songInfos)

    def getAlbumCover(self, songInfo: SongInfo):
        self.albumCoverReader.getAlbumCover(songInfo)