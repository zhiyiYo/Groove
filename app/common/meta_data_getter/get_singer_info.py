# coding:utf-8
from copy import deepcopy
from typing import List, Dict


class SingerInfoGetter:
    """ 获取歌手信息的类 """

    def __init__(self, albumInfo_list: list) -> None:
        self.albumInfo_list = deepcopy(albumInfo_list)    # type:List[dict]
        self.singerInfos = self.getSingerInfos(self.albumInfo_list)

    @staticmethod
    def getSingerInfos(albumInfo_list: list) -> Dict[str, dict]:
        """ 获取歌手信息 """
        singerInfos = {}

        year = '0'
        for albumInfo in albumInfo_list:
            singer = albumInfo['singer']
            genre = albumInfo['genre']
            year_ = albumInfo.get('year', '0')

            # 如果字典中没有该歌手的信息就插入一个
            if singer not in singerInfos:
                singerInfos[singer] = {
                    "singer": singer,
                    "genre": genre,
                    "albumInfo_list": [],
                    "coverPath": f'singer_avatar/{singer}.jpg'
                }

            singerInfos[singer]["albumInfo_list"].append(albumInfo)

            # 使用最新的专辑流派作为歌手的流派
            if year_ >= year:
                singerInfos[singer]['genre'] = genre
                year = year_

        # 排序专辑信息
        for singerInfo in singerInfos.values():
            singerInfo["albumInfo_list"].sort(
                key=lambda i: i.get('year', '0'), reverse=True)

        return singerInfos

    def updateSingerInfos(self, albumInfo_list: list):
        """ 更新歌手信息 """
        self.albumInfo_list = deepcopy(albumInfo_list)    # type:List[dict]
        self.singerInfos = self.getSingerInfos(self.albumInfo_list)
