# coding:utf-8
from common.os_utils import getCoverPath, adjustName


class AlbumInfoReader:
    """ 从歌曲信息列表中整理出专辑信息的类 """

    def __init__(self, songInfos: list):
        self.albumInfos = self.getAlbumInfo(songInfos)
        self.sortByModifiedTime()

    def getAlbumInfo(self, songInfos: list):
        """ 从歌曲信息列表中来获取专辑信息 """
        albumInfos = []
        albumSonger_list = []

        for songInfo in songInfos:
            album = songInfo["album"]  # type:str
            singer = songInfo["singer"]  # type:str
            coverName = songInfo["coverName"]  # type:str
            # 如果(专辑名,歌手名)不在列表中，就往列表中插入新的专辑信息字典
            if (album, singer) not in albumSonger_list:
                albumSonger_list.append((album, singer))
                coverPath = getCoverPath(coverName, 'album_big')
                albumInfos.append(
                    {
                        "album": album,
                        "singer": singer,
                        "songInfos": [songInfo],
                        "coverName": coverName,
                        "coverPath": coverPath,
                        "genre": songInfo["genre"],
                        "year": songInfo["year"],
                        "modifiedTime": songInfo["createTime"]
                    }
                )
            else:
                index = albumSonger_list.index((album, singer))
                albumInfo = albumInfos[index]
                albumInfo["songInfos"].append(songInfo)
                # 更新专辑的更新时间
                if albumInfo["modifiedTime"] < songInfo["createTime"]:
                    albumInfo["modifiedTime"] = songInfo["createTime"]

        # 根据曲目序号排序每一个专辑
        for albumInfo in albumInfos:
            albumInfo["songInfos"].sort(key=self.sortAlbum)
        return albumInfos

    def updateAlbumInfo(self, songInfos: list):
        """ 更新专辑信息 """
        self.albumInfos = self.getAlbumInfo(songInfos)

    def sortAlbum(self, songInfo):
        trackNum = songInfo["tracknumber"]  # type:str
        # 处理m4a
        if not trackNum[0].isnumeric():
            return eval(trackNum)[0]
        return int(trackNum)

    def sortByModifiedTime(self):
        """ 依据修改日期排序专辑信息列表 """
        self.albumInfos.sort(
            key=lambda albumInfo: albumInfo["modifiedTime"], reverse=True)

    def sortByDictOrder(self):
        """ 以字典序排序专辑信息列表 """
        self.albumInfos.sort(key=lambda albumInfo: albumInfo["songName"])

    def sortBySonger(self):
        """ 以歌手名排序专辑信息列表 """
        self.albumInfos.sort(key=lambda albumInfo: albumInfo["singer"])

    @staticmethod
    def getAlbumInfoByOneSong(songInfo: dict):
        """ 从一首歌创建一个专辑信息 """
        album = songInfo["album"]
        singer = songInfo["singer"]
        coverName = adjustName(singer+'_'+album)

        coverPath = getCoverPath(coverName, 'album_big')
        albumInfo = {
            "album": album,
            "singer": singer,
            "genre": songInfo["genre"],
            "year": songInfo["year"],
            "songInfos": [songInfo.copy()],
            "modifiedTime": songInfo["createTime"],
            "coverPath": coverPath,
            "coverName": coverName,
        }
        return albumInfo
