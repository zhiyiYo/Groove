# coding:utf-8
import os
from app.common.get_cover_path import getCoverPath


class GetAlbumInfo:
    """ 从歌曲信息列表中整理出专辑信息的类 """

    def __init__(self, songInfo_list: list):
        self.albumInfo_list = self.getAlbumInfo(songInfo_list)
        self.sortByModifiedTime()

    def getAlbumInfo(self, songInfo_list: list):
        """ 从歌曲信息列表中来获取专辑信息 """
        albumInfo_list = []
        albumSonger_list = []

        for songInfo in songInfo_list:
            album = songInfo["album"]  # type:str
            songer = songInfo["songer"]  # type:str
            modifiedAlbum = songInfo["modifiedAlbum"]  # type:str
            # 如果(专辑名,歌手名)不在列表中，就往列表中插入新的专辑信息字典
            if (album, songer) not in albumSonger_list:
                albumSonger_list.append((album, songer))
                coverPath = getCoverPath(modifiedAlbum, 'album_big')
                albumInfo_list.append(
                    {
                        "modifiedTime": songInfo["createTime"],
                        "album": album,
                        "songer": songer,
                        "tcon": songInfo["tcon"],
                        "year": songInfo["year"],
                        "coverPath": coverPath,
                        "songInfo_list": [songInfo],
                        "modifiedAlbum": modifiedAlbum,
                    }
                )
            else:
                index = albumSonger_list.index((album, songer))
                albumInfo = albumInfo_list[index]
                albumInfo["songInfo_list"].append(songInfo)
                # 更新专辑的更新时间
                if albumInfo["modifiedTime"] < songInfo["createTime"]:
                    albumInfo["modifiedTime"] = songInfo["createTime"]

        # 根据曲目序号排序每一个专辑
        for albumInfo in albumInfo_list:
            albumInfo["songInfo_list"].sort(key=self.sortAlbum)
        return albumInfo_list

    def updateAlbumInfo(self, songInfo_list: list):
        """ 更新专辑信息 """
        self.albumInfo_list = self.getAlbumInfo(songInfo_list)

    def sortAlbum(self, songInfo):
        trackNum = songInfo["tracknumber"]  # type:str
        # 处理m4a
        if not trackNum[0].isnumeric():
            return eval(trackNum)[0]
        return int(trackNum)

    def sortByModifiedTime(self):
        """ 依据修改日期排序专辑信息列表 """
        self.albumInfo_list.sort(
            key=lambda albumInfo: albumInfo["modifiedTime"], reverse=True)

    def sortByDictOrder(self):
        """ 以字典序排序专辑信息列表 """
        self.albumInfo_list.sort(key=lambda albumInfo: albumInfo["songName"])

    def sortBySonger(self):
        """ 以歌手名排序专辑信息列表 """
        self.albumInfo_list.sort(key=lambda albumInfo: albumInfo["songer"])
