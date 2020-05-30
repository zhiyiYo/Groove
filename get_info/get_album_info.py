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
            album_list = songInfo['album']
            # 如果专辑名不在集合中，就往列表中插入专辑信息字典
            if album_list[0] not in album_set:
                pic_list=os.listdir(f'resource\\Album Cover\\{album_list[-1]}')
                if pic_list:
                    cover_path = os.path.join(f'resource\\Album Cover\\{album_list[-1]}', pic_list[0])
                else:
                    cover_path = 'resource\\Album Cover\\未知专辑封面.png'
                albumInfo_list.append(
                    {'album': album_list[0], 'songer': songInfo['songer'],
                     'songInfo_list': [], 'tcon': songInfo['tcon'],
                     'year': songInfo['year'], 'updateTime': '0',
                     'cover_path':cover_path})
                album_set.add(album_list[0])

        # 再将同一个专辑的歌曲添加到字典的歌曲列表中
        for songInfo in songInfo_list:
            for albumInfo_dict in albumInfo_list:
                # 更新专辑的更新时间
                if albumInfo_dict['updateTime'] < songInfo['createTime']:
                    albumInfo_dict['updateTime'] = songInfo['createTime']

                if albumInfo_dict['album'] == songInfo['album'][0]:
                    # 如果专辑名匹配就将歌曲信息插到字典的列表中
                    albumInfo_dict['songInfo_list'].append(songInfo)
                    break
        with open('Data\\albumInfo.json', 'w', encoding='utf-8') as f:
            json.dump(albumInfo_list, f)

        return albumInfo_list

    def sortByUpdateTime(self):
        """ 依据文件创建日期排序文件信息列表 """
        self.albumInfo_list.sort(
            key=lambda albumInfo: albumInfo['updateTime'], reverse=True)

    def sortByDictOrder(self):
        """ 以字典序排序文件信息列表 """
        self.albumInfo_list.sort(key=lambda albumInfo: albumInfo['songname'])

    def sortBySonger(self):
        """ 以歌手名排序文件信息列表 """
        self.albumInfo_list.sort(key=lambda albumInfo: albumInfo['songer'])


if __name__ == "__main__":
    albumInfo = AlbumInfo()
