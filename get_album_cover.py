# coding:utf-8
import os
import re
import imghdr
from shutil import copyfile

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

        # 扫描文件夹，如果有专辑没有对应的文件夹就创建一个包含默认封面图像的文件夹
        for info_dict in self.songInfo.songInfo_list:
            # 封面目录
            sub_album_cover_folder = os.path.join(
                self.album_cover_folder, info_dict['album'])
            # 封面路径
            pic_path = os.path.join(
                sub_album_cover_folder, info_dict['album'] + '.png')
            if not os.path.exists(sub_album_cover_folder):
                os.mkdir(sub_album_cover_folder)
                copyfile('resource\\Album Cover\\未知专辑封面.png', pic_path)

    def getID3AlbumCover(self, info_dict, id_card):
        """ 获取mp3文件的封面并写入文件夹 """
        # 封面目录
        sub_album_cover_folder = os.path.join(
            self.album_cover_folder, info_dict['album'])

        # 如果已经存在封面目录就直接返回
        if os.path.exists(sub_album_cover_folder):
            return

        rex = r'APIC.*'
        for key in id_card.tags.keys():
            Match = re.match(rex, key)
            if Match:
                # 如果不存在专辑对应的目录,就新建一个并写入专辑封面
                os.mkdir(sub_album_cover_folder)
                # 提取封面数据
                pic_data = id_card[Match.group()].data
                try:
                    # 检测数据格式
                    suffix = '.' + imghdr.what(None, pic_data)
                    if suffix == '.jpeg':
                        suffix = '.jpg'
                except:
                    suffix = '.jpg'
                 # 封面路径
                pic_path = os.path.join(
                    sub_album_cover_folder, info_dict['album'] + suffix)
                # 写入封面
                with open(pic_path, 'wb') as f:
                    f.write(pic_data)
                break

    def getFlacAlbumCover(self, info_dict, id_card):
        """ 获取flac文件的封面并写入文件夹 """

        sub_album_cover_folder = os.path.join(
            self.album_cover_folder, info_dict['album'])

        # 如果已经存在封面目录就直接返回
        if os.path.exists(sub_album_cover_folder):
            return

        # 确认是否存在封面数据
        if id_card.pictures:
            # 如果不存在专辑对应的目录,就新建一个并写入专辑封面
            os.mkdir(sub_album_cover_folder)
            # 提取封面数据
            pic_data = id_card.pictures[0].data
            try:
                # 检测数据格式
                suffix = '.' + imghdr.what(None, pic_data)
                if suffix == '.jpeg':
                    suffix = '.jpg'
            except:
                suffix = '.jpg'
            # 封面路径
            pic_path = os.path.join(
                sub_album_cover_folder, info_dict['album'] + suffix)
            # 写入封面
            with open(pic_path, 'wb') as f:
                f.write(pic_data)

    def getM4aAlbumCover(self, info_dict, id_card):
        """ 获取m4a文件的封面 """
        sub_album_cover_folder = os.path.join(
            self.album_cover_folder, info_dict['album'])

        # 如果已经存在封面目录就直接返回
        if os.path.exists(sub_album_cover_folder):
            return

        if id_card.get('covr'):
            # 如果不存在专辑对应的目录,就新建一个并写入专辑封面
            os.mkdir(sub_album_cover_folder)
            # 提取封面数据
            pic_data = bytes(id_card['covr'][0])
            try:
                # 检测数据格式
                suffix = '.' + imghdr.what(None, pic_data)
                if suffix == '.jpeg':
                    suffix = '.jpg'
            except:
                suffix = '.jpg'
            # 封面路径
            pic_path = os.path.join(
                sub_album_cover_folder, info_dict['album'] + suffix)
            # 写入封面
            with open(pic_path, 'wb') as f:
                f.write(pic_data)


if __name__ == "__main__":
    albumCover = AlbumCover('D:\\KuGou')
