# coding:utf-8
import os
import re
import imghdr
from shutil import copyfile,rmtree

from mutagen import File
from mutagen.flac import Picture

from .get_song_info import SongInfo


class GetAlbumCover():
    """ 定义一个遍历音频文件和封面文件夹获取专辑封面的类 """

    def __init__(self, target_path_list: list):
        """ 初始化类的属性 """
        self.cwd = os.getcwd()
        self.album_cover_folder = os.path.join(
            self.cwd, r'resource\Album Cover')
        self.target_path_list = target_path_list
        # 实例化一个用于获取歌曲信息的类
        self.songInfo = SongInfo(target_path_list)
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
            if id_card.mime[0].split('/')[-1] == 'mp3':
                self.getID3AlbumCover(info_dict, id_card)
            elif id_card.mime[0].split('/')[-1] == 'flac':
                self.getFlacAlbumCover(info_dict, id_card)
            elif id_card.mime[0].split('/')[-1] == 'mp4':
                self.getM4aAlbumCover(info_dict, id_card)
        # 扫描文件夹，如果有专辑没有对应的文件夹就创建一个包含默认封面图像的文件夹
        for info_dict in self.songInfo.songInfo_list:
            # 封面目录
            sub_album_cover_folder = os.path.join(
                self.album_cover_folder, info_dict['album'][-1])
            # 封面路径
            pic_path = os.path.join(
                sub_album_cover_folder, info_dict['album'][-1] + '.png')
            if not os.path.exists(sub_album_cover_folder):
                os.mkdir(sub_album_cover_folder)
                copyfile('resource\\Album Cover\\未知专辑封面_200_200.png', pic_path)

    def getID3AlbumCover(self, info_dict, id_card):
        """ 获取mp3文件的封面并写入文件夹 """
        # 封面目录
        isPicExist, sub_album_cover_folder = self.__isPicExist(info_dict)
        if isPicExist:
            return
        rex = r'APIC.*'
        for key in id_card.tags.keys():
            Match = re.match(rex, key)
            if Match:
                # 如果不存在专辑对应的目录,就新建一个并写入专辑封面
                os.mkdir(sub_album_cover_folder)
                # 提取封面数据
                pic_data = id_card[Match.group()].data
                self.__savePic(sub_album_cover_folder,info_dict,pic_data)
                break

    def getFlacAlbumCover(self, info_dict, id_card):
        """ 获取flac文件的封面并写入文件夹 """
        isPicExist, sub_album_cover_folder = self.__isPicExist(info_dict)
        if isPicExist:
            return
        # 确认是否存在封面数据
        if id_card.pictures:
            # 如果不存在专辑对应的目录,就新建一个并写入专辑封面
            os.mkdir(sub_album_cover_folder)
            # 提取封面数据
            pic_data = id_card.pictures[0].data
            self.__savePic(sub_album_cover_folder, info_dict, pic_data)

    def getM4aAlbumCover(self, info_dict, id_card):
        """ 获取m4a文件的封面 """
        isPicExist, sub_album_cover_folder = self.__isPicExist(info_dict)
        if isPicExist:
            return
        if id_card.get('covr'):
            # 如果不存在专辑对应的目录,就新建一个并写入专辑封面
            os.mkdir(sub_album_cover_folder)
            # 提取封面数据
            pic_data = bytes(id_card['covr'][0])
            self.__savePic(sub_album_cover_folder, info_dict, pic_data)

    def __isPicExist(self,info_dict):
        """ 检测封面是否存在 """
        sub_album_cover_folder = os.path.join(
            self.album_cover_folder, info_dict['album'][-1])
        # 默认封面存在
        isPicExist = True

        if os.path.exists(sub_album_cover_folder):
            fileName_list = os.listdir(sub_album_cover_folder)
            if not fileName_list:
                # 如果目录为空说明封面不存在,直接删除旧文件夹
                isPicExist = False
                rmtree(sub_album_cover_folder)
            else:
                # 如果第一个文件不是图片也需要删除文件夹并重新提取封面
                suffix = os.path.splitext(fileName_list[0])[1][1:]
                if suffix.lower() not in ['png', 'jpg', 'jpeg', 'jiff']:
                    rmtree(sub_album_cover_folder)
                    isPicExist = False
        else:
            isPicExist = False
        return isPicExist,sub_album_cover_folder
                
    def __getPicSuffix(self, pic_data):
        """ 获取二进制数据的后缀名 """
        try:
            suffix = '.' + imghdr.what(None, pic_data)
            if suffix == '.jpeg':
                suffix = '.jpg'
        except:
            suffix = '.jpg'
        return suffix

    def __savePic(self, sub_album_cover_folder,info_dict, pic_data):
        """ 储存提取到的专辑封面 """
        # 获取后缀名
        suffix = self.__getPicSuffix(pic_data)
        # 封面路径
        pic_path = os.path.join(
            sub_album_cover_folder, info_dict['album'][-1] + suffix)
        # 写入封面
        with open(pic_path, 'wb') as f:
            f.write(pic_data)

if __name__ == "__main__":
    getAlbumCover = GetAlbumCover(['D:\\KuGou'])
