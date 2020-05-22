# coding:utf-8
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

        # 获取符合匹配音频文件名列表
        self.split_song_list(filename_list, update_songList=True)
        if os.path.exists('Data\\songInfo.json'):
            with open('Data\\songInfo.json', 'r', encoding='utf-8') as f:
                try:
                    # 尝试读取旧歌曲信息
                    oldData = json.load(f)
                except:
                    # 如果信息为空就创建一个空列表
                    oldData = [{}]
        else:
            oldData = [{}]

        oldFilename_list = [oldFileInfo.get('song') for oldFileInfo in oldData]

        # 判断旧文件名列表是否与新文件名列表相等
        if set(self.song_list) == set(oldFilename_list):
            # 如果文件名完全相等就直接获取以前的文件信息
            self.songInfo_list = oldData.copy()
        else:
            new_filename_set = set(self.song_list)
            old_filename_set = set(oldFilename_list)
            different_filename_list = list(new_filename_set - old_filename_set)
            # 找出文件名的并集和新的文件名列表
            common_filename_set = new_filename_set & old_filename_set

            # 根据文件名获取文件信息字典
            if common_filename_set:
                self.songInfo_list = [old_songInfo_dict for old_songInfo_dict in oldData
                                      if old_songInfo_dict['song'] in common_filename_set]

            # 如果新的文件名集合是旧的子集，公共部分就是新的文件信息
            if set(self.song_list) < set(oldFilename_list) and common_filename_set:
                pass
            else:
                # 获取后缀名，歌名，歌手名列表
                self.split_song_list(different_filename_list,
                                     flag=1, update_songList=True)
                # 获取符合匹配规则的歌曲的路径
                self.song_path_list = [os.path.join(
                    self.target_path, song) for song in self.song_list]

                argZip = zip(self.song_list, self.song_path_list, self.songname_list,
                             self.songer_list, self.suffix_list)

                for song, song_path, songname, songer, suffix in argZip:
                    id_card = File(song_path)
                    # 获取时间戳
                    createTime = os.path.getctime(song_path)
                    # 将时间戳转换为时间结构
                    timeStruct = time.localtime(createTime)
                    # 格式化时间结构
                    createTime = time.strftime('%Y-%m-%d %H:%M:%S', timeStruct)
                    album, tcon, year, duration, tracknumber = self.fetch_album_tcon_year_trkn(
                        suffix, id_card)
                    # 将歌曲信息字典插入列表
                    self.songInfo_list.append({'song': song,
                                               'song_path': song_path,
                                               'songer': songer,
                                               'songname': songname,
                                               'album': album,
                                               'tcon': tcon,
                                               'year': year,
                                               'tracknumber': tracknumber,
                                               'duration': duration,
                                               'suffix': suffix,
                                               'createTime': createTime})
            self.sortByCreateTime()
            # 更新json文件
            with open('Data\\songInfo.json', 'w', encoding='utf-8') as f:
                json.dump(self.songInfo_list, f)

    def split_song_list(self, filename_list, flag=0, update_songList=False):
        """分离歌手名，歌名和后缀名,flag用于表示是否将匹配到的音频文件拆开,
        flag = 1为拆开,flag=0为不拆开，update_songList用于更新歌曲文件列表"""

        if update_songList:
            self.song_list = filename_list.copy()

        self.songer_list, self.songname_list, self.suffix_list = [], [], []
        rex = r'(.+) - (.+)(\.mp3)|(.+) - (.+)(\.flac)|(.+) - (.+)(\.m4a)'

        for filename in filename_list:
            Match = re.match(rex, filename)
            if Match and flag == 1:
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
            elif not Match:
                self.song_list.remove(filename)

    def fetch_album_tcon_year_trkn(self, suffix, id_card):
        """ 根据文件的后缀名来获取专辑信息及时长 """

        if suffix == '.mp3':
            # 如果没有标题则添加标题
            album = str(id_card['TALB'][0]) if id_card.get('TALB') else '未知专辑'
            # 曲目
            tracknumber = str(id_card['TRCK'][0]) if id_card.get(
                'TRCK') else '0'
            tcon = str(id_card['TCON'][0]) if id_card.get('TCON') else '未知流派'
            if id_card.get('TDRC'):
                year = str(id_card['TDRC'][0]) + \
                    '年' if len(str(id_card['TDRC']))==4 else '未知年份'
            duration = f'{int(id_card.info.length//60)}:{int(id_card.info.length%60):02}'

        elif suffix == '.flac':
            album = id_card.get('album')[0] if id_card.get('album') else '未知专辑'
            tracknumber = id_card['tracknumber'][0] if id_card.get(
                'tracknumber') else '0'
            tcon = id_card.get('genre')[0] if id_card.get('genre') else '未知流派'
            year = id_card.get('year')[0][:4] + \
                '年' if id_card.get('year') else '未知年份'
            duration = f'{int(id_card.info.length//60)}:{int(id_card.info.length%60):02}'

        elif suffix == '.m4a':
            album = id_card.get('©alb')[0] if id_card.get('©alb') else '未知专辑'
            # m4a的曲目标签还应包括专辑中的总曲数,得到的是元胞数组
            tracknumber = str(id_card['trkn'][0]
                              ) if id_card.get('trkn') else '(0,0)'
            tcon = id_card.get('©gen')[0] if id_card.get('©gen') else '未知流派'
            year = id_card.get('©day')[0][:4] + \
                '年' if id_card.get('©day') else '未知年份'
            duration = f'{int(id_card.info.length//60)}:{int(id_card.info.length%60):02}'

        # 替换不符合命名规则的专辑名
        album = re.sub(r'[><:\\/\*\?]', ' ', album)
        album = re.sub(r'[\"]', "'", album)
        album = album.strip()
        return album, tcon, year, duration, tracknumber

    def sortByCreateTime(self):
        """ 依据文件创建日期排序文件信息列表 """

        self.songInfo_list.sort(
            key=lambda songInfo: songInfo['createTime'], reverse=True)

    def sortByDictOrder(self):
        """ 以字典序排序文件信息列表 """
        self.songInfo_list.sort(key=lambda songInfo: songInfo['songname'])

    def sortBySonger(self):
        """ 以歌手名排序文件信息列表 """
        self.songInfo_list.sort(key=lambda songInfo: songInfo['songer'])


if __name__ == "__main__":
    songInfo = SongInfo('D:\\KuGou')

