# coding:utf-8

import json
import os


class AlbumInfo():
    """ 定义一个获取专辑信息和将专辑信息写入json文件的类 """

    def __init__(self):
        self.albumInfo_list = self.getAlbumInfo()
        self.sortByUpdateTime()

    def getAlbumInfo(self):
        """ 从json文件读入信息 """
        return self.updateAlbumInfo()

    def updateAlbumInfo(self):
        """ 遍历songInfo.json文件来获取专辑信息 """
        albumInfo_list = []
        album_set = set()

        if not os.path.exists('Data\\songInfo.json'):
            return None
        # 从json文件读取信息
        with open('Data\\songInfo.json', encoding='utf-8') as f:
            songInfo_list = json.load(f)
        # 先将专辑信息字典插到列表中
        for songInfo in songInfo_list:
            # songInfo的'album'对应的值是一个列表，可能包含修改前和修改后的专辑名
            album_list = songInfo['album']
            # 如果专辑名不在集合中，就往列表中插入专辑信息字典
            if album_list[0] not in album_set:
                pic_list = os.listdir(
                    f'resource\\Album_Cover\\{album_list[-1]}')
                if pic_list:
                    # 如果目录下有封面就用这个封面作为albumCard的背景
                    cover_path = os.path.join(
                        f'resource\\Album_Cover\\{album_list[-1]}', pic_list[0])
                else:
                    # 否则用默认的封面
                    cover_path = 'resource\\images\\未知专辑封面_200_200.png'
                albumInfo_list.append(
                    {'album': album_list[0], 'songer': songInfo['songer'],
                     'songInfo_list': [], 'tcon': songInfo['tcon'],
                     'year': songInfo['year'], 'updateTime': '0',
                     'cover_path': cover_path})
                album_set.add(album_list[0])

        # 再将同一个专辑的歌曲添加到字典的歌曲列表中
        for songInfo in songInfo_list:
            for albumInfo_dict in albumInfo_list:
                # songInfo['album']的一个元素存的是原始专辑名
                if albumInfo_dict['album'] == songInfo['album'][0]:
                    # 如果专辑名匹配就将歌曲信息插到字典的列表中
                    albumInfo_dict['songInfo_list'].append(songInfo)
                    # 更新专辑的更新时间
                    if albumInfo_dict['updateTime'] < songInfo['createTime']:
                        albumInfo_dict['updateTime'] = songInfo['createTime']
                    break
        # 根据曲目序号排序每一个专辑
        for albumInfo_dict in albumInfo_list:
            albumInfo_dict['songInfo_list'].sort(key=self.sortAlbum)
        # 将专辑信息写入文件
        """ with open('Data\\albumInfo.json', 'w', encoding='utf-8') as f:
            json.dump(albumInfo_list, f) """

        return albumInfo_list

    def sortAlbum(self, songInfo):
        trackNum = songInfo['tracknumber']  # type:str
        # 处理m4a
        if not trackNum[0].isnumeric():
            return eval(trackNum)[0]
        return int(trackNum)

    def sortByUpdateTime(self):
        """ 依据文件创建日期排序文件信息列表 """
        self.albumInfo_list.sort(
            key=lambda albumInfo: albumInfo['updateTime'], reverse=True)

    def sortByDictOrder(self):
        """ 以字典序排序文件信息列表 """
        self.albumInfo_list.sort(key=lambda albumInfo: albumInfo['songName'])

    def sortBySonger(self):
        """ 以歌手名排序文件信息列表 """
        self.albumInfo_list.sort(key=lambda albumInfo: albumInfo['songer'])

    def updateOneAlbumSongInfo(self, newSongInfo: dict) -> dict:
        """ 更新专辑中的一首歌的信息，并返回一个更新后的专辑信息 """
        for albumInfo in self.albumInfo_list:
            if albumInfo['album'] == newSongInfo['album'][0] and albumInfo['songer'] == newSongInfo['songer']:
                for songInfo in albumInfo['songInfo_list']:
                    if songInfo['songPath'] == newSongInfo['songPath']:
                        songInfo = newSongInfo.copy()
                        return albumInfo
        return {}

    def getOneAlbumInfo(self, albumName: str) -> dict:
        """ 根据专辑名返回一个专辑信息字典 """
        for albumInfo in self.albumInfo_list:
            if albumInfo['album'] == albumName:
                return albumInfo
        return {}


if __name__ == "__main__":
    albumInfo = AlbumInfo()
