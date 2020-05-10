import json
import os
import re
import time
from mutagen import File


class SongInfo():
    """ 创建一个获取和保存歌曲信息的类 """

    def __init__(self, target_path):
        self.target_path = target_path
        self.songInfo_list = []
        self.getInfo()

    def getInfo(self):
        """ 从指定的目录读取符合匹配规则的歌曲的标签卡信息 """

        for home, dirs, filename_list in os.walk(self.target_path):
            break

        
        # 获取符合匹配的歌曲列表及歌手名，歌名
        self.song_list = filename_list[:]
        self.split_song_list(filename_list)
        # 获取符合匹配规则的歌曲的路径
        self.song_path_list = [os.path.join(
            self.target_path, song) for song in self.song_list]

        argZip = zip(self.song_path_list, self.songname_list,
                     self.songer_list, self.suffix_list)
        for song_path, songname, songer, suffix in argZip:
            id_card = File(song_path)
            # 获取时间戳
            createTime = os.path.getctime(song_path)
            # 将时间戳转换为时间结构
            timeStruct = time.localtime(createTime)
            # 格式化时间结构
            createTime = time.strftime('%Y-%m-%d %H:%M:%S', timeStruct)
            album, tcon, year, duration = self.fetch_album_tcon_year(
                suffix, id_card)
            # 将歌曲的路径作为列表的第一个元素，歌曲信息作为第二个元素
            self.songInfo_list.append({'song_path':song_path,
                                        'songer': songer,
                                        'songname': songname,
                                        'album': album,
                                        'tcon': tcon,
                                        'year': year,
                                        'duration': duration,
                                        'createTime':createTime} )

    def split_song_list(self, filename_list):
        """分离歌手名，歌名和后缀名"""
        self.songer_list, self.songname_list, self.suffix_list = [], [], []
        rex = r'(.+) - (.+)(\.mp3)|(.+) - (.+)(\.flac)|(.+) - (.+)(\.m4a)'

        for filename in filename_list:
            Match = re.match(rex, filename)
            if Match:
                if Match.group(1):
                    self.songer_list.append(Match.group(1))
                    self.songname_list.append(Match.group(2))
                    self.suffix_list.append(Match.group(3))
                elif Match.group(4):
                    self.songer_list.append(Match.group(4))
                    self.songname_list.append(Match.group(5))
                    self.suffix_list.append(Match.group(6))
                else:
                    self.songer_list.append(Match.group(7))
                    self.songname_list.append(Match.group(8))
                    self.suffix_list.append(Match.group(9))
            else:
                self.song_list.remove(filename)

    def fetch_album_tcon_year(self, suffix, id_card):
        """ 根据文件的后缀名来获取专辑信息及时长 """

        if suffix == '.mp3':
            # 如果没有标题则添加标题
            album = str(id_card.get('TALB')) if id_card.get('TALB') else '未知专辑'
            tcon = str(id_card.get('TCON')) if id_card.get('TCON') else '未知流派'
            year = str(id_card.get('TDRC')) + \
                '年' if id_card.get('TDRC')[:4] else '未知年份'
            duration = f'{int(id_card.info.length//60)}:{int(id_card.info.length%60):02}'
        elif suffix == '.flac':
            album = id_card.get('album')[0] if id_card.get('album') else '未知专辑'
            tcon = id_card.get('genre')[0] if id_card.get('genre') else '未知流派'
            year = id_card.get('year')[0][:4] + \
                '年' if id_card.get('year') else '未知年份'
            duration = f'{int(id_card.info.length//60)}:{int(id_card.info.length%60):02}'
        elif suffix == '.m4a':
            album = id_card.get('©alb')[0] if id_card.get('©alb') else '未知专辑'
            tcon = id_card.get('©gen')[0] if id_card.get('©gen') else '未知流派'
            year = id_card.get('©day')[0][:4] + \
                '年' if id_card.get('©day') else '未知年份'
            duration = f'{int(id_card.info.length//60)}:{int(id_card.info.length%60):02}'

        return album, tcon, year, duration

    def sortByCreateTime(self):
        """ 依据文件创建日期排序文件信息列表 """
        self.songInfo_list.sort(key=lambda songInfo: songInfo['createTime'], reverse=True)

    def sortByDictOrder(self):
        """ 以字典序排序文件信息列表 """
        self.songInfo_list.sort(key=lambda songInfo: songInfo['songname'])

    def sortBySonger(self):
        """ 以歌手名排序文件信息列表 """
        self.songInfo_list.sort(key=lambda songInfo: songInfo['songer'])


if __name__ == "__main__":
    songInfo = SongInfo('D:\\KuGou')

    """ for info in songInfo.songInfo_list:
        print(info['song_path']+':'+info['createTime'])
        print('=='*30) """
