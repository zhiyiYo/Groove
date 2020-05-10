# coding:utf-8
import os
import re

from mutagen import File
from mutagen.flac import Picture

from get_song_info import SongInfo


class AlbumCover():
    """ 定义一个遍历音频文件和封面文件夹获取专辑封面的类 """

    def __init__(self, target_path):
        """ 初始化类的属性 """
        self.cwd = os.getcwd()
        self.album_cover_folder = os.path.join(
            self.cwd, 'resource\\Album Cover')
        self.target_path = target_path
        # 实例化一个用于获取歌曲信息的类
        self.songInfo = SongInfo(target_path)
        # 获取封面
        self.get_album()

    def get_album(self):
        """ 获取封面 """
        # 检查当前目录下是否存在用于储存所有封面的目录,没有就创建
        if not os.path.exists(self.album_cover_folder):
            os.mkdir(self.album_cover_folder)
        # 开始获取封面
        for info_dict in self.songInfo.songInfo_list:
            # 实例化一个File实例
            id_card = File(info_dict['song_path'])
            # 根据后缀名选择获取封面的方式
            if info_dict['suffix'] == '.mp3':
                self.getID3AlbumCover(info_dict, id_card)
            elif info_dict['suffix'] == '.flac':
                self.getFlacAlbumCover(info_dict, id_card)
            elif info_dict['suffix'] == '.m4a':
                self.getM4aAlbumCover(info_dict, id_card)

    def getID3AlbumCover(self, info_dict, id_card):
        """ 获取mp3文件的封面并写入文件夹 """
        rex = r'APIC.*'

        for key in id_card.tags.keys():
            Match = re.match(rex, key)
            if Match:
                # 如果不存在专辑对应的目录,就新建一个并写入专辑封面
                sub_album_cover_folder = os.path.join(
                    self.album_cover_folder, info_dict['album'])
                if not os.path.exists(sub_album_cover_folder):
                    os.mkdir(sub_album_cover_folder)
                    # 提取封面数据
                    pic_data = id_card[Match.group()].data
                    # 封面路径
                    pic_path = os.path.join(
                        sub_album_cover_folder, info_dict['album'] + '.jpg')
                    # 写入封面
                    with open(pic_path, 'wb') as f:
                        f.write(pic_data)

    def getFlacAlbumCover(self, info_dict, id_card):
        """ 获取flac文件的封面并写入文件夹 """
        # 确认是否存在封面数据
        if id_card.pictures:
            # 如果不存在专辑对应的目录,就新建一个并写入专辑封面
            sub_album_cover_folder = os.path.join(
                self.album_cover_folder, info_dict['album'])
            if not os.path.exists(sub_album_cover_folder):
                os.mkdir(sub_album_cover_folder)
                pic_path = os.path.join(
                    sub_album_cover_folder, info_dict['album'] + '.jpg')
                # 提取封面数据
                pic_data = id_card.pictures[0].data
                # 写入封面
                with open(pic_path, 'wb') as f:
                    f.write(pic_data)

    def getM4aAlbumCover(self, info_dict, id_card):
        if id_card.get('covr'):
            # 如果不存在专辑对应的目录,就新建一个并写入专辑封面
            sub_album_cover_folder = os.path.join(
                self.album_cover_folder, info_dict['album'])
            if not os.path.exists(sub_album_cover_folder):
                os.mkdir(sub_album_cover_folder)
                pic_path = os.path.join(
                    sub_album_cover_folder, info_dict['album'] + '.jpg')
                # 提取封面数据
                pic_data = bytes(id_card['covr'][0])
                # 写入封面
                with open(pic_path, 'wb') as f:
                    f.write(pic_data)


if __name__ == "__main__":
    albumCover = AlbumCover('D:\\KuGou')
