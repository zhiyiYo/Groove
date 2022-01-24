# coding:utf-8
from copy import deepcopy
from typing import List, Dict


class SingerInfoReader:
    """ 获取歌手信息的类 """

    def __init__(self, albumInfos: list) -> None:
        self.albumInfos = deepcopy(albumInfos)    # type:List[dict]
        self.singerInfos = self.getSingerInfos(self.albumInfos)

    @staticmethod
    def getSingerInfos(albumInfos: list) -> Dict[str, dict]:
        """ 获取歌手信息 """
        singerInfos = {}

        year = '0'
        for albumInfo in albumInfos:
            singer = albumInfo['singer']
            genre = albumInfo['genre']
            year_ = albumInfo.get('year', '0')

            # 如果字典中没有该歌手的信息就插入一个
            if singer not in singerInfos:
                singerInfos[singer] = {
                    "singer": singer,
                    "genre": genre,
                    "albumInfos": [],
                }

            singerInfos[singer]["albumInfos"].append(albumInfo)

            # 使用最新的专辑流派作为歌手的流派
            if year_ >= year:
                singerInfos[singer]['genre'] = genre
                year = year_

        # 排序专辑信息
        for singerInfo in singerInfos.values():
            singerInfo["albumInfos"].sort(
                key=lambda i: i.get('year', '0'), reverse=True)

        return singerInfos

    def updateSingerInfos(self, albumInfos: list):
        """ 更新歌手信息 """
        self.albumInfos = deepcopy(albumInfos)    # type:List[dict]
        self.singerInfos = self.getSingerInfos(self.albumInfos)
